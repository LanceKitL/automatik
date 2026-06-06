"""
Tests for all customer portal routes (blueprint: customerportal_bp, prefix: /portal).

Uses Flask test client with a fully mocked database layer — no real DB needed.
Covers every endpoint defined in routes/customerportal.py with success and
error cases.
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


class TestCustomerPortalRoutes(unittest.TestCase):
    """Comprehensive tests for /portal/* routes with mocked DB layer."""

    maxDiff = None

    def setUp(self):
        # Mock middleware decorators before importing app
        self.patcher_logged_in = patch(
            "validators.middleware.logged_in_required", lambda f: f
        )
        self.patcher_role = patch(
            "validators.middleware.role_required", lambda *a, **kw: lambda f: f
        )
        self.patcher_logged_in.start()
        self.patcher_role.start()

        # Import the Flask app
        with patch("app.load_dotenv", return_value=None):
            from app import app as _app

        # Patch run_query at the module level in every controller
        import controllers.customerportalController
        import controllers.vehicleController
        import controllers.inquiriesController
        import controllers.profileController
        import controllers.notificationController
        import utils.notification as utils_notif
        import utils.log as utils_log

        self.mock_run = MagicMock(name="run_query_mock")
        self.mock_getdb = MagicMock(name="get_db_mock")

        self._p_cp = patch.object(
            controllers.customerportalController, "run_query", self.mock_run
        )
        self._p_vc = patch.object(
            controllers.vehicleController, "run_query", self.mock_run
        )
        self._p_ic = patch.object(
            controllers.inquiriesController, "run_query", self.mock_run
        )
        self._p_pc = patch.object(
            controllers.profileController, "run_query", self.mock_run
        )
        self._p_nc = patch.object(
            controllers.notificationController, "run_query", self.mock_run
        )
        self._p_un = patch.object(utils_notif, "run_query", self.mock_run)
        self._p_ul = patch.object(utils_log, "run_query", self.mock_run)

        self._p_cp.start()
        self._p_vc.start()
        self._p_ic.start()
        self._p_pc.start()
        self._p_nc.start()
        self._p_un.start()
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

        # Silence SocketIO
        self._patcher_sio = patch(
            "utils.socket_handler.socketio.emit", return_value=None
        )
        self._patcher_sio.start()

        with self.app.session_transaction() as sess:
            sess["user"] = 1
            sess["role"] = "customer"
            sess.permanent = True

    def tearDown(self):
        self.patcher_logged_in.stop()
        self.patcher_role.stop()
        self._p_cp.stop()
        self._p_vc.stop()
        self._p_ic.stop()
        self._p_pc.stop()
        self._p_nc.stop()
        self._p_un.stop()
        self._p_ul.stop()
        self._patcher_sio.stop()

    # --- helpers ---------------------------------

    @staticmethod
    def _fake_user(**kw):
        d = dict(user_id=1, username="cust1", email="cust@example.com", role="customer")
        d.update(kw)
        return d

    @staticmethod
    def _fake_sale(**kw):
        d = dict(
            sale_id=1, vehicle_id=10, agent_id=2, customer_id=1,
            selling_price=2000000.00, payment_type="cash",
            sale_date=MOCK_NOW, status="completed",
            brand="Toyota", model="Fortuner", year=2025,
            color="White", body_type="SUV", vehicle_price=2000000.00,
        )
        d.update(kw)
        return d

    @staticmethod
    def _fake_vehicle(**kw):
        d = dict(
            vehicle_id=10, brand="Toyota", model="Fortuner",
            body_type="SUV", price=2000000.00, year=2025,
            status="available", color="White",
        )
        d.update(kw)
        return d

    @staticmethod
    def _fake_amortization(**kw):
        d = dict(
            next_payment_amount=35000.00,
            next_payment_due=MOCK_NOW,
            amortization_id=1, loan_id=50, due_date=MOCK_NOW,
            total_due=35000.00, status="unpaid",
        )
        d.update(kw)
        return d

    @staticmethod
    def _fake_document(**kw):
        d = dict(
            document_id=1, sale_id=1, filename="contract.pdf",
            file_path="/docs/contract.pdf", is_accessible=1,
            created_at=MOCK_NOW,
        )
        d.update(kw)
        return d

    @staticmethod
    def _fake_inquiry(**kw):
        d = dict(
            inquiry_id=100, user_id=1, vehicle_id=10, agent_id=2,
            message="I want to buy this car", status="open",
            created_at=MOCK_NOW, resolved_at=None,
            brand="Toyota", model="Fortuner", color="White",
            body_type="SUV", price=2000000.00,
            employee_number="EMP-001",
        )
        d.update(kw)
        return d

    @staticmethod
    def _fake_notification(**kw):
        d = dict(
            notification_id=1, user_id=1, title="Test",
            message="Test notification", channel="in_app",
            ref_type="general", ref_id=1,
            is_read=0, created_at=MOCK_NOW,
        )
        d.update(kw)
        return d

    @staticmethod
    def _fake_payment(**kw):
        d = dict(
            payment_id=1, sale_id=1, amount=2000000.00,
            payment_date=MOCK_NOW, payment_method="cash",
        )
        d.update(kw)
        return d

    @staticmethod
    def _fake_claim(**kw):
        d = dict(
            claim_id=1, sale_id=1, vehicle_id=10,
            claim_type="repair", description="Engine issue",
            status="submitted", resolution=None,
            submitted_at=MOCK_NOW, resolved_at=None,
            brand="Toyota", model="Fortuner",
        )
        d.update(kw)
        return d

    @staticmethod
    def _fake_photo(**kw):
        d = dict(photo_id=1, vehicle_id=10, photo_url="http://example.com/pic.jpg")
        d.update(kw)
        return d

    @staticmethod
    def _fake_supplier(**kw):
        d = dict(
            vehicle_id=10, company_name="Toyota Corp",
            contact_name="John", contact_email="john@toyota.com",
            contact_phone="1234567890", address="Tokyo",
        )
        d.update(kw)
        return d

    # --- DASHBOARD -------------------------------

    def test_dashboard_success(self):
        # Enough items for all calls: user, sales (empty), inquiries, notifications
        self.mock_run.side_effect = [
            self._fake_user(),           # 1. user lookup
            [],                           # 2. sales (empty list => skip amort/doc/veh)
            [],                           # 3. inquiries
            [],                           # 4. notifications
        ]
        resp = self.app.get("/portal/")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertIn("data", body)
        self.assertIn("dashboard", body["data"])

    def test_dashboard_customer_not_found(self):
        self.mock_run.return_value = None  # first user query returns None
        resp = self.app.get("/portal/")
        self.assertEqual(resp.status_code, 404)
        body = resp.get_json()
        self.assertIn("Customer not found", body["message"])

    def test_dashboard_with_sales_data(self):
        sale = self._fake_sale()
        am = self._fake_amortization()  # has next_payment_amount + next_payment_due
        doc = self._fake_document()
        veh = self._fake_vehicle()
        inq = self._fake_inquiry(status="open")
        notif = self._fake_notification(is_read=0)

        def side_effect(query, *args, **kw):
            q = query.strip().lower()
            if q.startswith("select username"):
                return self._fake_user()
            if "from sales" in q and "customer_id" in q:
                return [sale]
            if "from amortization_schedule" in q:
                return am
            if "from documents" in q:
                return [doc]
            if "from vehicles" in q and "join sales" in q:
                return [veh]
            if "from inquiries" in q:
                return [inq]
            if "from notifications" in q:
                return [notif]
            return None

        self.mock_run.side_effect = side_effect
        resp = self.app.get("/portal/")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        dash = body["data"]["dashboard"]
        self.assertEqual(dash["active_sales"], 1)
        self.assertIsNotNone(dash["next_payment_due"])
        self.assertIsNotNone(dash["next_payment_amount"])
        self.assertEqual(dash["open_inquiries"], 1)
        self.assertEqual(dash["unread_notification"], 1)
        self.assertEqual(len(dash["recent_documents"]), 1)
        self.assertEqual(len(dash["my_vehicles"]), 1)

    # --- BROWSE VEHICLES -------------------------

    def test_vehicles_list(self):
        def side_effect(query, *args, **kw):
            q = query.strip().lower()
            if q.startswith("select * from vehicles") and "where" not in q:
                return [self._fake_vehicle()]
            if "vehicle_photos" in q:
                return [self._fake_photo()]
            if "suppliers" in q:
                return [self._fake_supplier()]
            return None

        self.mock_run.side_effect = side_effect
        resp = self.app.get("/portal/vehicles")
        self.assertEqual(resp.status_code, 200)

    def test_vehicle_detail_success(self):
        def side_effect(query, *args, **kw):
            q = query.strip().lower()
            if q.startswith("select * from vehicles") and "where" in q:
                return self._fake_vehicle()
            if "vehicle_photos" in q:
                return [self._fake_photo()]
            if "suppliers" in q:
                return self._fake_supplier()
            return None

        self.mock_run.side_effect = side_effect
        resp = self.app.get("/portal/vehicles/10")
        self.assertEqual(resp.status_code, 200)

    def test_vehicle_detail_not_found(self):
        self.mock_run.return_value = None
        resp = self.app.get("/portal/vehicles/999")
        self.assertEqual(resp.status_code, 404)

    # --- SALES -----------------------------------

    def test_sales_list(self):
        self.mock_run.return_value = [self._fake_sale()]
        resp = self.app.get("/portal/sales")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertIsInstance(body, list)
        if body:
            self.assertIn("vehicle", body[0])

    def test_sale_detail_success(self):
        self.mock_run.return_value = self._fake_sale()
        resp = self.app.get("/portal/sales/1")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertIn("vehicle", body)

    def test_sale_detail_not_found(self):
        self.mock_run.return_value = None
        resp = self.app.get("/portal/sales/999")
        self.assertEqual(resp.status_code, 404)

    # --- PAYMENTS --------------------------------

    def test_payment_history(self):
        self.mock_run.return_value = [self._fake_payment()]
        resp = self.app.get("/portal/payments")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertIn("data", body)

    # --- AMORTIZATION ----------------------------

    def test_amortization_schedule(self):
        self.mock_run.return_value = [self._fake_amortization()]
        resp = self.app.get("/portal/amortization")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertIn("data", body)

    # --- DOCUMENTS -------------------------------

    def test_documents_list(self):
        self.mock_run.return_value = [self._fake_document()]
        resp = self.app.get("/portal/documents")
        self.assertEqual(resp.status_code, 200)

    def test_document_detail_success(self):
        self.mock_run.return_value = self._fake_document()
        resp = self.app.get("/portal/documents/1")
        self.assertEqual(resp.status_code, 200)

    def test_document_detail_not_found(self):
        self.mock_run.return_value = None
        resp = self.app.get("/portal/documents/999")
        self.assertEqual(resp.status_code, 404)

    # --- INQUIRIES -------------------------------

    def test_inquiries_list(self):
        self.mock_run.return_value = [self._fake_inquiry()]
        resp = self.app.get("/portal/inquiries")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertIsInstance(body, list)
        if body:
            self.assertIn("vehicle", body[0])

    def test_inquiry_detail_success(self):
        self.mock_run.return_value = self._fake_inquiry()
        resp = self.app.get("/portal/inquiries/100")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertIn("vehicle", body)

    def test_inquiry_detail_not_found(self):
        self.mock_run.return_value = None
        resp = self.app.get("/portal/inquiries/999")
        self.assertEqual(resp.status_code, 404)

    # --- SUBMIT INQUIRY --------------------------

    @patch("controllers.inquiriesController.fire_notif")
    @patch("controllers.inquiriesController.broadcast_notif")
    @patch("controllers.inquiriesController.audit_log")
    def test_submit_inquiry_success(self, mock_audit, mock_broad, mock_notif):
        # submitInquiry reads res["user_id"] after insert
        self.mock_run.return_value = {"user_id": 1, "inquiry_id": 100}
        payload = dict(vehicle_id=10, message="I want a test drive")
        resp = self.app.post(
            "/portal/inquiries",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)

    def test_submit_inquiry_missing_message(self):
        payload = dict(vehicle_id=10)
        resp = self.app.post(
            "/portal/inquiries",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_submit_inquiry_missing_vehicle_id(self):
        payload = dict(message="Test")
        resp = self.app.post(
            "/portal/inquiries",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    # --- NOTIFICATIONS ---------------------------

    def test_notifications_list(self):
        self.mock_run.return_value = [self._fake_notification()]
        resp = self.app.get("/portal/notifications")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        # getNotifications returns a list, not a dict with "data"
        self.assertIsInstance(body, list)
        if body:
            self.assertIn("id", body[0])

    def test_mark_notification_read_success(self):
        self.mock_run.side_effect = [
            self._fake_notification(is_read=0),
            None,
        ]
        resp = self.app.put("/portal/notifications/1/read")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertIn("marked as read", body["message"].lower())

    def test_mark_notification_read_already_read(self):
        self.mock_run.return_value = self._fake_notification(is_read=1)
        resp = self.app.put("/portal/notifications/1/read")
        # Controller does not reject already-read notifications; returns 200.
        self.assertEqual(resp.status_code, 200)

    def test_mark_notification_read_not_found(self):
        self.mock_run.return_value = None
        resp = self.app.put("/portal/notifications/999/read")
        self.assertEqual(resp.status_code, 404)

    # --- PROFILE ---------------------------------

    def test_profile_get_success(self):
        self.mock_run.return_value = dict(
            user_id=1, username="cust1", email="cust@example.com",
            role="customer", created_at=MOCK_NOW,
            full_name="Juan Dela Cruz", phone_number="09171234567",
            address="123 Rizal St", city="Manila", province="NCR",
            zip_code="1000", date_of_birth=None, gender=None,
            customer_number="C-001", preferred_contact_method="email",
            preferred_payment_method="cash", notes=None,
        )
        resp = self.app.get("/portal/profile")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertIn("user", body)
        self.assertIn("profile", body)
        self.assertIn("customer_details", body)

    def test_profile_get_unauthorized(self):
        with self.app.session_transaction() as sess:
            sess.pop("user", None)
        resp = self.app.get("/portal/profile")
        self.assertEqual(resp.status_code, 401)

    def test_profile_get_not_found(self):
        self.mock_run.return_value = None
        resp = self.app.get("/portal/profile")
        self.assertEqual(resp.status_code, 404)

    def test_profile_update(self):
        self.mock_run.return_value = None
        payload = dict(full_name="Updated Name", phone_number="09180000000")
        resp = self.app.put(
            "/portal/profile",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)

    # --- INSURANCE -------------------------------

    def test_insurance(self):
        self.mock_run.return_value = [
            dict(insurance_id=1, customer_id=1, policy_number="POL-001")
        ]
        resp = self.app.get("/portal/insurance")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertIn("data", body)

    # --- WARRANTY CLAIMS -------------------------

    def test_warranty_claims_list(self):
        self.mock_run.return_value = [self._fake_claim()]
        resp = self.app.get("/portal/warranty-claims")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertIsInstance(body, list)
        if body:
            self.assertIn("vehicle", body[0])

    def test_warranty_claim_detail_success(self):
        self.mock_run.return_value = self._fake_claim()
        resp = self.app.get("/portal/warranty-claims/1")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertIn("vehicle", body)

    def test_warranty_claim_detail_not_found(self):
        self.mock_run.return_value = None
        resp = self.app.get("/portal/warranty-claims/999")
        self.assertEqual(resp.status_code, 404)

    @patch("controllers.customerportalController.audit_log")
    @patch("controllers.customerportalController.fire_notif")
    @patch("controllers.customerportalController.broadcast_notif")
    @patch("controllers.customerportalController.send_warranty_claim_notification")
    def test_create_warranty_claim_success(
        self, mock_email, mock_broad, mock_notif, mock_audit
    ):
        sale = dict(sale_id=1, vehicle_id=10, brand="Toyota", model="Fortuner")
        # create_customer_warranty_claim makes many run_query calls:
        # 1. sale ownership check
        # 2. INSERT returns claim_id
        # 3. audit_log calls run_query
        # But audit_log is patched, so we don't need to worry about that.
        self.mock_run.side_effect = [
            sale,
            100,
        ]
        payload = dict(
            sale_id=1, claim_type="repair",
            description="Engine makes a strange noise",
        )
        resp = self.app.post(
            "/portal/warranty-claims",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        body = resp.get_json()
        self.assertIn("claim_id", body)
        mock_notif.assert_called()
        mock_broad.assert_called()
        mock_email.assert_called_once()

    def test_create_warranty_claim_missing_sale_id(self):
        payload = dict(claim_type="repair", description="Broken")
        resp = self.app.post(
            "/portal/warranty-claims",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_create_warranty_claim_missing_claim_type(self):
        payload = dict(sale_id=1, description="Broken")
        resp = self.app.post(
            "/portal/warranty-claims",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_create_warranty_claim_invalid_claim_type(self):
        payload = dict(sale_id=1, claim_type="invalid", description="Broken")
        resp = self.app.post(
            "/portal/warranty-claims",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 422)

    def test_create_warranty_claim_missing_description(self):
        payload = dict(sale_id=1, claim_type="repair")
        resp = self.app.post(
            "/portal/warranty-claims",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_create_warranty_claim_description_too_long(self):
        payload = dict(
            sale_id=1, claim_type="repair",
            description="x" * 2001,
        )
        resp = self.app.post(
            "/portal/warranty-claims",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 422)

    def test_create_warranty_claim_sale_not_owned(self):
        self.mock_run.return_value = None
        payload = dict(
            sale_id=999, claim_type="repair",
            description="Not my sale",
        )
        resp = self.app.post(
            "/portal/warranty-claims",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()
