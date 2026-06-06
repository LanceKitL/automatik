"""
Tests for all service & warranty routes (customer + admin endpoints).

Blueprints tested:
  - service_bp (prefix: /service) — customer warranty submit/list
  - admin_bp   (prefix: /admin)   — admin list/detail/status transitions

Uses Flask test client with fully mocked database layer — no real DB needed.
Covers every endpoint with success and error cases, including transactional
FOR UPDATE paths and lock timeout handling.
"""

import json
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone


MOCK_NOW = datetime(2026, 6, 5, 12, 0, 0, tzinfo=timezone.utc)


def _make_cursor():
    c = MagicMock()
    c.fetchone.return_value = None
    c.fetchall.return_value = []
    c.lastrowid = 1
    c.description = None
    return c


def _make_conn(cursor=None):
    c = MagicMock()
    c.cursor.return_value = cursor or _make_cursor()
    return c


class TestWarrantyCustomerEndpoints(unittest.TestCase):
    """Tests for customer warranty endpoints at /service/warranty"""

    maxDiff = None

    def setUp(self):
        # Mock middleware decorators
        self.patcher_logged_in = patch(
            "validators.middleware.logged_in_required", lambda f: f
        )
        self.patcher_role = patch(
            "validators.middleware.role_required", lambda *a, **kw: lambda f: f
        )
        self.patcher_logged_in.start()
        self.patcher_role.start()

        with patch("app.load_dotenv", return_value=None):
            from app import app as _app

        # Patch run_query and get_db at the module level in serviceController
        import controllers.serviceController as sc
        import utils.log as utils_log

        self.mock_run = MagicMock(name="run_query_mock")
        self.mock_getdb = MagicMock(name="get_db_mock")

        self._p_sc_run = patch.object(sc, "run_query", self.mock_run)
        self._p_sc_getdb = patch.object(sc, "get_db", self.mock_getdb)
        self._p_ul = patch.object(utils_log, "run_query", self.mock_run)

        self._p_sc_run.start()
        self._p_sc_getdb.start()
        self._p_ul.start()

        _app.config["TESTING"] = True
        _app.config["SERVER_NAME"] = "localhost"
        _app.secret_key = "test-secret"
        self.app = _app.test_client()
        self.app.testing = True

        # Default cursor/connection for transactional paths
        self.default_cursor = _make_cursor()
        self.default_conn = _make_conn(self.default_cursor)
        self.mock_getdb.return_value = (self.default_conn, self.default_cursor)
        self.mock_run.return_value = None

        # Silence SocketIO
        self._patcher_sio = patch(
            "utils.socket_handler.socketio.emit", return_value=None
        )
        self._patcher_sio.start()

        # Default session: customer
        with self.app.session_transaction() as sess:
            sess["user"] = 1
            sess["role"] = "customer"
            sess.permanent = True

    def tearDown(self):
        self.patcher_logged_in.stop()
        self.patcher_role.stop()
        self._p_sc_run.stop()
        self._p_sc_getdb.stop()
        self._p_ul.stop()
        self._patcher_sio.stop()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _fake_claim(**kw):
        d = dict(
            claim_id=1, sale_id=1, vehicle_id=10,
            claim_type="repair", description="Engine issue",
            status="submitted", resolution=None,
            submitted_at=MOCK_NOW, resolved_at=None,
            brand="Toyota", model="Fortuner", year=2025,
        )
        d.update(kw)
        return d

    # ------------------------------------------------------------------
    # POST /service/warranty — Submit claim
    # ------------------------------------------------------------------

    def test_submit_claim_success(self):
        """Valid payload returns 201 with claim_id."""
        self.mock_run.side_effect = [
            {"sale_id": 1},     # 1. sale ownership check
            None,                # 2. duplicate guard — no existing claim
            100,                 # 3. INSERT returns claim_id
            None,                # 4. audit_log INSERT (via patched run_query)
        ]
        payload = dict(
            vehicle_id=10, sale_id=1,
            claim_type="repair", description="Engine issue",
        )
        resp = self.app.post(
            "/service/warranty",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        body = resp.get_json()
        self.assertEqual(body["claim_id"], 100)

    def test_submit_claim_missing_vehicle_id(self):
        """Missing vehicle_id → 400."""
        payload = dict(sale_id=1, claim_type="repair", description="Broken")
        resp = self.app.post(
            "/service/warranty",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_submit_claim_missing_sale_id(self):
        """Missing sale_id → 400."""
        payload = dict(vehicle_id=10, claim_type="repair", description="Broken")
        resp = self.app.post(
            "/service/warranty",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_submit_claim_missing_claim_type(self):
        """Missing claim_type → 400."""
        payload = dict(vehicle_id=10, sale_id=1, description="Broken")
        resp = self.app.post(
            "/service/warranty",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_submit_claim_missing_description(self):
        """Missing description → 400."""
        payload = dict(vehicle_id=10, sale_id=1, claim_type="repair")
        resp = self.app.post(
            "/service/warranty",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_submit_claim_invalid_claim_type(self):
        """Non-enum claim_type → 422."""
        payload = dict(
            vehicle_id=10, sale_id=1,
            claim_type="invalid", description="Broken",
        )
        resp = self.app.post(
            "/service/warranty",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 422)

    def test_submit_claim_description_too_long(self):
        """Description > 1000 chars → 422."""
        payload = dict(
            vehicle_id=10, sale_id=1, claim_type="repair",
            description="x" * 1001,
        )
        resp = self.app.post(
            "/service/warranty",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 422)

    def test_submit_claim_sale_not_owned(self):
        """Sale not belonging to session user → 403."""
        self.mock_run.return_value = None  # sale lookup returns None
        payload = dict(
            vehicle_id=10, sale_id=999,
            claim_type="repair", description="Not mine",
        )
        resp = self.app.post(
            "/service/warranty",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 403)

    def test_submit_claim_duplicate_active(self):
        """Existing submitted/under_review claim on same sale+vehicle → 409."""
        self.mock_run.side_effect = [
            {"sale_id": 1},       # 1. sale ownership passes
            {"claim_id": 5},      # 2. duplicate found
        ]
        payload = dict(
            vehicle_id=10, sale_id=1,
            claim_type="repair", description="Duplicate",
        )
        resp = self.app.post(
            "/service/warranty",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 409)
        body = resp.get_json()
        self.assertIn("active claim already exists", body["message"].lower())

    # ------------------------------------------------------------------
    # GET /service/warranty/my — List own claims
    # ------------------------------------------------------------------

    def test_list_my_claims_success(self):
        """Returns list of claims for session user."""
        self.mock_run.return_value = [self._fake_claim()]
        resp = self.app.get("/service/warranty/my")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertIn("data", body)
        self.assertEqual(len(body["data"]), 1)
        self.assertEqual(body["data"][0]["claim_id"], 1)

    def test_list_my_claims_empty(self):
        """Returns empty list when no claims exist."""
        self.mock_run.return_value = []
        resp = self.app.get("/service/warranty/my")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertEqual(len(body["data"]), 0)


class TestWarrantyAdminEndpoints(unittest.TestCase):
    """Tests for admin warranty endpoints at /admin/warranty"""

    maxDiff = None

    def setUp(self):
        self.patcher_logged_in = patch(
            "validators.middleware.logged_in_required", lambda f: f
        )
        self.patcher_role = patch(
            "validators.middleware.role_required", lambda *a, **kw: lambda f: f
        )
        self.patcher_logged_in.start()
        self.patcher_role.start()

        with patch("app.load_dotenv", return_value=None):
            from app import app as _app

        import controllers.serviceController as sc
        import utils.log as utils_log

        self.mock_run = MagicMock(name="run_query_mock")
        self.mock_getdb = MagicMock(name="get_db_mock")

        self._p_sc_run = patch.object(sc, "run_query", self.mock_run)
        self._p_sc_getdb = patch.object(sc, "get_db", self.mock_getdb)
        self._p_ul = patch.object(utils_log, "run_query", self.mock_run)

        self._p_sc_run.start()
        self._p_sc_getdb.start()
        self._p_ul.start()

        _app.config["TESTING"] = True
        _app.config["SERVER_NAME"] = "localhost"
        _app.secret_key = "test-secret"
        self.app = _app.test_client()
        self.app.testing = True

        self.default_cursor = _make_cursor()
        self.default_conn = _make_conn(self.default_cursor)
        self.mock_getdb.return_value = (self.default_conn, self.default_cursor)
        self.mock_run.return_value = None

        self._patcher_sio = patch(
            "utils.socket_handler.socketio.emit", return_value=None
        )
        self._patcher_sio.start()

        # Admin session
        with self.app.session_transaction() as sess:
            sess["user"] = 1
            sess["role"] = "admin"
            sess.permanent = True

    def tearDown(self):
        self.patcher_logged_in.stop()
        self.patcher_role.stop()
        self._p_sc_run.stop()
        self._p_sc_getdb.stop()
        self._p_ul.stop()
        self._patcher_sio.stop()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _fake_claim(**kw):
        d = dict(
            claim_id=1, sale_id=1, vehicle_id=10,
            claim_type="repair", description="Engine issue",
            status="submitted", resolution=None,
            submitted_at=MOCK_NOW, resolved_at=None,
            reviewed_by=None, customer_name="cust1", reviewer_name=None,
            brand="Toyota", model="Fortuner", year=2025,
        )
        d.update(kw)
        return d

    # ------------------------------------------------------------------
    # GET /admin/warranty — List all claims
    # ------------------------------------------------------------------

    def test_list_all_claims_unfiltered(self):
        """Returns all claims with no filter."""
        self.mock_run.return_value = [self._fake_claim()]
        resp = self.app.get("/admin/warranty")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertIn("data", body)
        self.assertEqual(len(body["data"]), 1)

    def test_list_all_claims_filtered(self):
        """Filters by ?status=submitted."""
        self.mock_run.return_value = [self._fake_claim(status="submitted")]
        resp = self.app.get("/admin/warranty?status=submitted")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertEqual(body["data"][0]["status"], "submitted")

    def test_list_all_claims_empty(self):
        """Returns empty list when no claims exist."""
        self.mock_run.return_value = []
        resp = self.app.get("/admin/warranty")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.get_json()["data"]), 0)

    # ------------------------------------------------------------------
    # GET /admin/warranty/<claim_id> — Claim detail
    # ------------------------------------------------------------------

    def test_get_claim_detail_success(self):
        """Returns claim with linked service bookings."""
        claim = self._fake_claim()
        self.mock_run.side_effect = [
            claim,    # 1. claim query
            [],       # 2. linked bookings (empty)
        ]
        resp = self.app.get("/admin/warranty/1")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertIn("data", body)
        self.assertIsInstance(body["data"]["service_bookings"], list)

    def test_get_claim_detail_with_bookings(self):
        """Returns claim with non-empty linked bookings."""
        claim = self._fake_claim()
        booking = dict(
            booking_id=5, slot_id=2, slot_datetime=MOCK_NOW,
            slot_type="repair", status="confirmed",
        )
        self.mock_run.side_effect = [
            claim,      # 1. claim query
            [booking],  # 2. linked bookings
        ]
        resp = self.app.get("/admin/warranty/1")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertEqual(len(body["data"]["service_bookings"]), 1)
        self.assertEqual(
            body["data"]["service_bookings"][0]["booking_id"], 5,
        )

    def test_get_claim_detail_not_found(self):
        """Non-existent claim_id → 404."""
        self.mock_run.return_value = None
        resp = self.app.get("/admin/warranty/999")
        self.assertEqual(resp.status_code, 404)

    # ------------------------------------------------------------------
    # PUT /admin/warranty/<claim_id>/review (submitted → under_review)
    # ------------------------------------------------------------------

    def test_review_claim_success(self):
        """Transition submitted → under_review."""
        self._setup_transition_mock("submitted")
        resp = self.app.put(
            "/admin/warranty/1/review",
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertIn("under_review", body["message"])

    # ------------------------------------------------------------------
    # PUT /admin/warranty/<claim_id>/approve (under_review → approved)
    # ------------------------------------------------------------------

    @patch("controllers.serviceController.fire_notif")
    def test_approve_claim_success(self, mock_notif):
        """Transition under_review → approved with notification."""
        self._setup_transition_mock("under_review")
        resp = self.app.put(
            "/admin/warranty/1/approve",
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        mock_notif.assert_called_once_with(
            1, "Warranty Approved",
            "Your warranty claim has been approved.",
            "in_app", "warranty_claims", 1,
        )

    # ------------------------------------------------------------------
    # PUT /admin/warranty/<claim_id>/reject (under_review → rejected)
    # ------------------------------------------------------------------

    @patch("controllers.serviceController.fire_notif")
    def test_reject_claim_success(self, mock_notif):
        """Transition under_review → rejected with resolution and notification."""
        self._setup_transition_mock("under_review")
        resp = self.app.put(
            "/admin/warranty/1/reject",
            data=json.dumps({"resolution_text": "Not covered by warranty"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        mock_notif.assert_called_once()

    def test_reject_claim_missing_resolution(self):
        """Reject without resolution_text → 400."""
        self._setup_transition_mock("under_review")
        resp = self.app.put(
            "/admin/warranty/1/reject",
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    # ------------------------------------------------------------------
    # PUT /admin/warranty/<claim_id>/resolve (approved → resolved)
    # ------------------------------------------------------------------

    @patch("controllers.serviceController.fire_notif")
    def test_resolve_claim_success(self, mock_notif):
        """Transition approved → resolved with notification."""
        self._setup_transition_mock("approved")
        resp = self.app.put(
            "/admin/warranty/1/resolve",
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        mock_notif.assert_called_once_with(
            1, "Warranty Resolved",
            "Your warranty claim has been resolved.",
            "in_app", "warranty_claims", 1,
        )

    # ------------------------------------------------------------------
    # Invalid transitions
    # ------------------------------------------------------------------

    def test_invalid_transition_submitted_to_approved(self):
        """submitted → approved directly should fail with 409."""
        self._setup_transition_mock("submitted")
        resp = self.app.put(
            "/admin/warranty/1/approve",
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 409)
        body = resp.get_json()
        self.assertIn("invalid transition", body["message"].lower())

    def test_invalid_transition_submitted_to_rejected(self):
        """submitted → rejected directly should fail with 409."""
        self._setup_transition_mock("submitted")
        resp = self.app.put(
            "/admin/warranty/1/reject",
            data=json.dumps({"resolution_text": "Nope"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 409)

    def test_invalid_transition_submitted_to_resolved(self):
        """submitted → resolved directly should fail with 409."""
        self._setup_transition_mock("submitted")
        resp = self.app.put(
            "/admin/warranty/1/resolve",
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 409)

    def test_invalid_transition_under_review_to_resolved(self):
        """under_review → resolved directly should fail with 409."""
        self._setup_transition_mock("under_review")
        resp = self.app.put(
            "/admin/warranty/1/resolve",
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 409)

    def test_invalid_transition_rejected_to_approved(self):
        """rejected terminals — any further transition should fail with 409."""
        self._setup_transition_mock("rejected")
        resp = self.app.put(
            "/admin/warranty/1/review",
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 409)

    def test_invalid_transition_resolved_to_any(self):
        """resolved terminals — any further transition should fail with 409."""
        self._setup_transition_mock("resolved")
        resp = self.app.put(
            "/admin/warranty/1/review",
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 409)

    def test_invalid_transition_approved_to_review(self):
        """approved → under_review should fail with 409."""
        self._setup_transition_mock("approved")
        resp = self.app.put(
            "/admin/warranty/1/review",
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 409)

    def test_invalid_transition_approved_to_reject(self):
        """approved → rejected should fail with 409."""
        self._setup_transition_mock("approved")
        resp = self.app.put(
            "/admin/warranty/1/reject",
            data=json.dumps({"resolution_text": "Too late"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 409)

    # ------------------------------------------------------------------
    # Claim not found on transition
    # ------------------------------------------------------------------

    def test_claim_not_found_on_transition(self):
        """Non-existent claim_id on any transition → 404."""
        # cursor.fetchone returns None (default from _make_cursor)
        self.mock_getdb.return_value = (self.default_conn, self.default_cursor)
        # Ensure fetchone returns None
        self.default_cursor.fetchone.return_value = None
        resp = self.app.put(
            "/admin/warranty/999/review",
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 404)

    # ------------------------------------------------------------------
    # Lock timeout handling (503)
    # ------------------------------------------------------------------

    def test_lock_timeout_on_review(self):
        """Lock wait timeout during FOR UPDATE → 503."""
        from mysql.connector.errors import OperationalError
        err = OperationalError("Lock wait timeout exceeded; try restarting transaction")
        self.default_cursor.execute.side_effect = err
        self.mock_getdb.return_value = (self.default_conn, self.default_cursor)
        resp = self.app.put(
            "/admin/warranty/1/review",
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 503)
        body = resp.get_json()
        self.assertIn("resource locked", body["error"].lower())
        # Verify rollback was called
        self.default_conn.rollback.assert_called_once()

    def test_lock_timeout_on_approve(self):
        """Lock wait timeout during approve → 503."""
        from mysql.connector.errors import OperationalError
        err = OperationalError("Lock wait timeout exceeded; try restarting transaction")
        self.default_cursor.execute.side_effect = err
        self.mock_getdb.return_value = (self.default_conn, self.default_cursor)
        resp = self.app.put(
            "/admin/warranty/1/approve",
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 503)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _setup_transition_mock(self, from_status):
        """Configure cursor to return a claim with the given status.

        The claim dict must include 'customer_id' (from the JOIN in the
        FOR UPDATE query) so notification calls work.
        """
        claim = self._fake_claim(status=from_status)
        claim["customer_id"] = 1  # added by JOIN with sales
        self.default_cursor.fetchone.return_value = claim
        self.mock_getdb.return_value = (self.default_conn, self.default_cursor)


if __name__ == "__main__":
    unittest.main()
