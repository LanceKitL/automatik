"""
Tests for the full inquiry → sale flow.

Uses Flask test client with mocked database layer so no real DB is needed.

Covered flows:
    1. Cash sale from guest inquiry (auto-create customer)
    2. Installment sale from guest inquiry (auto-create customer + loan approval)
    3. Direct cash sale with existing customer
    4. Agent commission calculation (3.5% of selling price)
    5. Notification delivery on assign / resolve / sale / loan status
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


class TestSalesFlow(unittest.TestCase):
    """End-to-end flow tests with mocked DB layer."""

    maxDiff = None

    def setUp(self):
        # ── Mock the middleware decorators so they always pass through ──
        # IMPORTANT: patch BEFORE importing the app so routes bind to the
        # passthrough versions.
        self.patcher_logged_in = patch("validators.middleware.logged_in_required",
                                       lambda f: f)
        self.patcher_role_admin = patch("validators.middleware.role_required",
                                        lambda *a, **kw: lambda f: f)
        self.patcher_logged_in.start()
        self.patcher_role_admin.start()

        # ── Import the Flask app (controllers get their real run_query/get_db) ──
        with patch("app.load_dotenv", return_value=None):
            from app import app as _app

        # ── Now patch the *local* references in each controller module ──
        # We must use patch.object() on the module attribute, not patch("conn.run_query"),
        # because every controller does "from conn import run_query" at the top of the
        # file — that creates a module-local name that survives patching conn.run_query.
        # We use a SINGLE MagicMock for ALL run_query patches so that setting
        # side_effect / return_value on self.mock_run affects every controller.
        import controllers.salesController
        import controllers.inquiriesController
        import utils.log as utils_log          # audit_log lives here

        self.mock_run = MagicMock(name="run_query_mock")
        self.mock_getdb = MagicMock(name="get_db_mock")

        self._patcher_sales_run = patch.object(controllers.salesController,
                                                "run_query", self.mock_run)
        self._patcher_inq_run = patch.object(controllers.inquiriesController,
                                              "run_query", self.mock_run)
        self._patcher_utils_run = patch.object(utils_log, "run_query", self.mock_run)
        self._patcher_sales_getdb = patch.object(controllers.salesController,
                                                  "get_db", self.mock_getdb)

        self._patcher_sales_run.start()
        self._patcher_inq_run.start()
        self._patcher_utils_run.start()
        self._patcher_sales_getdb.start()

        _app.config["TESTING"] = True
        _app.config["SERVER_NAME"] = "localhost"
        _app.secret_key = "test-secret"
        self.app = _app.test_client()
        self.app.testing = True

        self.default_cursor = _make_cursor()
        self.default_conn = _make_conn(self.default_cursor)
        self.mock_getdb.return_value = (self.default_conn, self.default_cursor)

        self.mock_run.return_value = None

        with self.app.session_transaction() as sess:
            sess["user"] = 1
            sess["role"] = "admin"
            sess.permanent = True

    def tearDown(self):
        self.patcher_logged_in.stop()
        self.patcher_role_admin.stop()
        self._patcher_sales_run.stop()
        self._patcher_sales_getdb.stop()
        self._patcher_inq_run.stop()
        self._patcher_utils_run.stop()

    # ─── fakes ────────────────────────────────

    @staticmethod
    def _fake_vehicle(**kw):
        d = dict(vehicle_id=10, brand="Toyota", model="Fortuner",
                 body_type="SUV", price=2000000.00, year=2025, status="available")
        d.update(kw)
        return d

    @staticmethod
    def _fake_agent(**kw):
        d = dict(user_id=2, username="agent1", email="tanjirokamado22222@gmail.com",
                 role="agent")
        d.update(kw)
        return d

    @staticmethod
    def _fake_customer(**kw):
        d = dict(user_id=3, username="cust-juan", email="lancegomoa@gmail.com",
                 role="customer", email_verified=1)
        d.update(kw)
        return d

    @staticmethod
    def _fake_inquiry(**kw):
        d = dict(inquiry_id=100, user_id=None, agent_id=None, vehicle_id=10,
                 guest_name="Juan Dela Cruz", guest_email="lancegomoa@gmail.com",
                 guest_number="09171234567", message="I want to buy this car",
                 status="open")
        d.update(kw)
        return d

    @staticmethod
    def _fake_loan(**kw):
        d = dict(loan_id=50, sale_id=1, down_payment=500000.00,
                 loan_amount=1500000.00, interest_rate=6.50, term_months=60,
                 monthly_amortization=None, bank_name="automatik_financing",
                 bank_approval_status="pending", customer_id=3,
                 sale_date=MOCK_NOW, selling_price=2000000.00)
        d.update(kw)
        return d

    def _set_session(self, user_id=1, role="admin"):
        with self.app.session_transaction() as sess:
            sess["user"] = user_id
            sess["role"] = role
            sess.permanent = True

    # ─── tests ─────────────────────────────────

    @patch("services.mail_service.welcome_user")
    @patch("controllers.salesController.send_sale_confirmation")
    @patch("controllers.salesController.fire_notif")
    def test_cash_sale_from_guest_inquiry(self, mock_notif, mock_email, mock_welcome):
        """Guest inquiry → cash sale → customer auto-created, commission recorded."""
        inquiry = self._fake_inquiry(status="open", agent_id=None)
        vehicle = self._fake_vehicle()
        agent = self._fake_agent()

        def rq_side_effect(query, *a, **kw):
            q = query.strip().lower()
            if "for update" in q:
                return vehicle
            if "role = 'agent'" in q:
                return agent
            if "from inquiries" in q:
                return inquiry
            return None
        self.mock_run.side_effect = rq_side_effect

        cur = _make_cursor()
        cur.lastrowid = 999
        self.mock_getdb.return_value = (_make_conn(cur), cur)

        payload = dict(vehicle_id=10, inquiry_id=100, agent_id=2,
                       payment_type="cash", selling_price=2000000.00)
        resp = self.app.post("/admin/sales", data=json.dumps(payload),
                             content_type="application/json")
        body = resp.get_json()
        self.assertEqual(resp.status_code, 201,
                         f"Expected 201, got {resp.status_code}: {body}")

        # Customer auto-created
        user_ins = [c for c in cur.execute.call_args_list
                    if "INSERT INTO users" in str(c)]
        self.assertTrue(len(user_ins) >= 1)

        cust_ins = [c for c in cur.execute.call_args_list
                    if "INSERT INTO customer_details" in str(c)]
        self.assertTrue(len(cust_ins) >= 1)

        # Commission = 2M * 3.5% = 70,000
        comm_ins = [c for c in cur.execute.call_args_list
                    if "INSERT INTO agent_commissions" in str(c)]
        self.assertTrue(len(comm_ins) >= 1)
        if comm_ins:
            args = comm_ins[0][0]
            self.assertAlmostEqual(args[1][2], 70000.00, places=2)

        # Inquiry updated with user_id
        upd = [c for c in cur.execute.call_args_list
               if "update inquiries" in str(c).lower() and "user_id" in str(c).lower()]
        self.assertTrue(len(upd) >= 1,
                        f"No UPDATE inquiries found. Calls:\n{cur.execute.call_args_list}")

        self.assertIn("temp_password", body)
        # Controller now fires two notifications: account created + sale created
        self.assertEqual(mock_notif.call_count, 2)
        mock_welcome.assert_called_once()

    @patch("services.mail_service.welcome_user")
    @patch("controllers.salesController.send_sale_confirmation")
    @patch("controllers.salesController.send_loan_status")
    @patch("controllers.salesController.fire_notif")
    @patch("controllers.salesController.generate_amortization_schedule")
    def test_installment_sale_from_guest_inquiry(
        self, mock_gen_sched, mock_notif, mock_loan_email, mock_sale_email, mock_welcome
    ):
        """Guest inquiry → installment sale → loan approved → amort schedule generated."""
        inquiry = self._fake_inquiry(status="open", agent_id=None)
        vehicle = self._fake_vehicle()
        agent = self._fake_agent()

        def rq_side_effect(query, *a, **kw):
            q = query.strip().lower()
            if "for update" in q:
                return vehicle
            if "role = 'agent'" in q:
                return agent
            if "from inquiries" in q:
                return inquiry
            return None
        self.mock_run.side_effect = rq_side_effect

        cur = _make_cursor()
        cur.lastrowid = 999
        self.mock_getdb.return_value = (_make_conn(cur), cur)

        payload = dict(vehicle_id=10, inquiry_id=100, agent_id=2,
                       payment_type="installment", selling_price=2000000.00,
                       down_payment=500000.00, loan_amount=1500000.00,
                       interest_rate=6.50, term_months=60)
        resp = self.app.post("/admin/sales", data=json.dumps(payload),
                             content_type="application/json")
        body = resp.get_json()
        self.assertEqual(resp.status_code, 201,
                         f"Expected 201, got {resp.status_code}: {body}")
        sale_id = body["sale_id"]

        # loan_details inserted with bank_name = 'automatik_financing'
        loan_ins = [c for c in cur.execute.call_args_list
                    if "INSERT INTO loan_details" in str(c)]
        self.assertTrue(len(loan_ins) >= 1)
        if loan_ins:
            args = loan_ins[0][0]
            params = args[1]
            self.assertEqual(params[6], "automatik_financing")

        # Schedule IS generated immediately during createSale (no longer deferred)
        # So mock_gen_sched WILL be called — we just assert loan approved later.

        # ── Approve loan ──
        loan_data = self._fake_loan(loan_id=50, sale_id=sale_id,
                                    bank_approval_status="pending")

        def approve_side_effect(query, *a, **kw):
            q = query.strip().lower()
            if "for update" in q:
                return loan_data
            if "count(*)" in q:
                return {"cnt": 1}  # schedule already exists — don't regenerate on approval
            if "update loan_details" in q:
                return None
            if "select email" in q:
                return {"email": "lancegomoa@gmail.com", "username": "cust-juan"}
            if "select full_name" in q:
                return {"full_name": "Juan Dela Cruz"}
            return None
        self.mock_run.side_effect = approve_side_effect

        cur2 = _make_cursor()
        self.mock_getdb.return_value = (_make_conn(cur2), cur2)

        resp = self.app.put("/admin/loans/50",
                            data=json.dumps({"bank_approval_status": "approved"}),
                            content_type="application/json")
        self.assertEqual(resp.status_code, 200)

        mock_gen_sched.assert_called_once()
        mock_loan_email.assert_called_once()

    @patch("controllers.salesController.send_sale_confirmation")
    @patch("controllers.salesController.fire_notif")
    def test_direct_cash_sale_existing_customer(self, mock_notif, mock_email):
        """Direct cash sale with existing customer_id (no inquiry)."""
        vehicle = self._fake_vehicle()
        agent = self._fake_agent()
        customer = self._fake_customer()

        def rq_side_effect(query, *a, **kw):
            q = query.strip().lower()
            if "for update" in q:
                return vehicle
            if "role = 'agent'" in q:
                return agent
            if "role = 'customer'" in q:
                return customer
            return None
        self.mock_run.side_effect = rq_side_effect

        cur = _make_cursor()
        cur.lastrowid = 1
        self.mock_getdb.return_value = (_make_conn(cur), cur)

        payload = dict(vehicle_id=10, customer_id=3, agent_id=2,
                       payment_type="cash", selling_price=2000000.00)
        resp = self.app.post("/admin/sales", data=json.dumps(payload),
                             content_type="application/json")
        body = resp.get_json()
        self.assertEqual(resp.status_code, 201,
                         f"Expected 201, got {resp.status_code}: {body}")
        self.assertEqual(body["customer_id"], 3)
        self.assertNotIn("temp_password", body)

    @patch("services.mail_service.inquiry_assigned")
    @patch("controllers.inquiriesController.fire_notif")
    def test_inquiry_assign_resolve_flow(self, mock_notif, mock_email):
        """Admin assigns inquiry → agent resolves.  Verifies notifs + status."""
        # ── Admin assigns ──
        self._set_session(1, "admin")
        inquiry = self._fake_inquiry(status="open", agent_id=None)

        def assign_side_effect(query, *a, **kw):
            q = query.strip().lower()
            if "from inquiries where inquiry_id" in q:
                return inquiry
            if "role = 'agent'" in q:
                return self._fake_agent(user_id=2)
            if "from agent_details" in q:
                return {"user_id": 2, "employee_number": "EMP-2025-001"}
            return None
        self.mock_run.side_effect = assign_side_effect

        resp = self.app.put("/inquiry/assign/100",
                            data=json.dumps({"agent_id": 2}),
                            content_type="application/json")
        body = resp.get_json()
        self.assertEqual(resp.status_code, 200,
                         f"Expected 200, got {resp.status_code}: {body}")
        self.assertIn("assigned successfully", body["message"].lower())

        agent_notifs = [c for c in mock_notif.call_args_list
                        if c.kwargs.get("user_id") == 2]
        self.assertGreaterEqual(len(agent_notifs), 1)

        # ── Agent resolves ──
        self._set_session(2, "agent")
        assigned = self._fake_inquiry(status="assigned", agent_id=2)

        def resolve_side_effect(query, *a, **kw):
            q = query.strip().lower()
            if "from inquiries" in q:
                return assigned
            if "select username from users" in q:
                return {"username": "agent1"}
            return None
        self.mock_run.side_effect = resolve_side_effect

        resp = self.app.put("/inquiry/resolve/100", content_type="application/json")
        body = resp.get_json()
        self.assertEqual(resp.status_code, 200,
                         f"Expected 200, got {resp.status_code}: {body}")
        self.assertIn("resolved", body["message"].lower())

    def test_commission_calculation(self):
        """Verify agent commission = selling_price * 3.5% default."""
        from controllers.salesController import insert_agent_commission

        # Default rate (None => 3.5)
        self.mock_run.return_value = {"default_commission_rate": None}
        cursor = MagicMock()
        insert_agent_commission(cursor, 1, 2, 2000000.00)
        cursor.execute.assert_called_once()
        args = cursor.execute.call_args[0][1]
        self.assertAlmostEqual(args[2], 70000.00, places=2)
        self.assertEqual(args[3], 3.5)

        # Custom rate
        cursor.reset_mock()
        self.mock_run.return_value = {"default_commission_rate": 5.0}
        insert_agent_commission(cursor, 1, 2, 1000000.00)
        args = cursor.execute.call_args[0][1]
        self.assertAlmostEqual(args[2], 50000.00, places=2)
        self.assertEqual(args[3], 5.0)


if __name__ == "__main__":
    unittest.main()
