import unittest
from unittest.mock import MagicMock
import json
from datetime import datetime

import conn
import controllers.financingController as fc_mod
import controllers.documentsController as dc_mod
import validators.middleware as mw_mod

from app import app


def _default_side_effect(query, params=None, fetch=None, conn=None, cursor=None):
    """Default mock: middleware auth OK, empty results for fetches, 1 for writes."""
    q_upper = query.strip().upper()
    if "SELECT" in q_upper and "FROM" in q_upper:
        if fetch == "all":
            return []
        if fetch == "one":
            if "users" in query.lower() and "user_id" in query.lower():
                return {"user_id": 1, "role": "admin", "is_active": 1}
            return None
        return 1
    if "INSERT" in q_upper or "UPDATE" in q_upper or "DELETE" in q_upper:
        return 1
    return None


class TestRoutesRegistration(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.client = app.test_client()
        self.mock_db = MagicMock(side_effect=_default_side_effect)
        conn.run_query = self.mock_db
        fc_mod.run_query = self.mock_db
        dc_mod.run_query = self.mock_db
        mw_mod.run_query = self.mock_db

    def _login(self, user_id=1, role="admin"):
        with self.client.session_transaction() as s:
            s["user"] = user_id
            s["role"] = role

    # ── Admin financing routes ──────────────────────────────────────

    def test_get_all_loans_unauthorized(self):
        resp = self.client.get("/admin/loans/")
        self.assertEqual(resp.status_code, 403)

    def test_get_all_loans_empty(self):
        self._login()
        resp = self.client.get("/admin/loans/")
        self.assertEqual(resp.status_code, 404)

    def test_get_loan_by_id_not_found(self):
        self._login()
        resp = self.client.get("/admin/loans/999")
        self.assertEqual(resp.status_code, 404)

    def test_get_loan_by_id_found(self):
        self._login()
        def side_effect(q, p=None, fetch=None, conn=None, cursor=None):
            if "users" in q and "user_id" in q:
                return {"user_id": 1, "role": "admin", "is_active": 1}
            if "loan_details.loan_id" in q and "WHERE" in q:
                return {"loan_id": 1, "sale_id": 10, "loan_amount": 100000.0}
            if "amortization_schedule.loan_id" in q:
                return [{"schedule_id": 1, "month_number": 1, "status": "unpaid"}]
            return None
        self.mock_db.side_effect = side_effect
        resp = self.client.get("/admin/loans/1")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertIn("loan", body)
        self.assertIn("schedule", body)

    def test_get_loan_schedule(self):
        self._login()
        def side_effect(q, p=None, fetch=None, conn=None, cursor=None):
            if "users" in q and "user_id" in q:
                return {"user_id": 1, "role": "admin", "is_active": 1}
            return [{"schedule_id": 1, "month_number": 1, "status": "unpaid"}]
        self.mock_db.side_effect = side_effect
        resp = self.client.get("/admin/loans/1/schedule")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertIn("data", body)

    def test_update_loan_status_no_field(self):
        self._login()
        resp = self.client.put("/admin/loans/1",
                               data=json.dumps({}),
                               content_type="application/json")
        self.assertEqual(resp.status_code, 400)

    def test_update_loan_status_ok(self):
        self._login()
        self.mock_db.side_effect = lambda q, *a, **kw: (
            {"user_id": 1, "role": "admin", "is_active": 1}
            if "users" in q else 1
        )
        resp = self.client.put("/admin/loans/1",
                               data=json.dumps({"bank_approval_status": "approved"}),
                               content_type="application/json")
        self.assertEqual(resp.status_code, 200)

    def test_update_schedule_status_no_field(self):
        self._login()
        resp = self.client.put("/admin/loans/amortization/1/status",
                               data=json.dumps({}),
                               content_type="application/json")
        self.assertEqual(resp.status_code, 400)

    def test_update_schedule_status_ok(self):
        self._login()
        call = [0]
        def side_effect(q, p=None, fetch=None, conn=None, cursor=None):
            call[0] += 1
            if call[0] == 1:
                return {"user_id": 1, "role": "admin", "is_active": 1}
            if call[0] == 2:
                return {"schedule_id": 1, "month_number": 1,
                        "customer_id": 4, "sale_id": 10}
            return 1
        self.mock_db.side_effect = side_effect
        resp = self.client.put("/admin/loans/amortization/1/status",
                               data=json.dumps({"status": "paid"}),
                               content_type="application/json")
        self.assertEqual(resp.status_code, 200)

    def test_get_overdue_schedules(self):
        self._login()
        def side_effect(q, p=None, fetch=None, conn=None, cursor=None):
            if "users" in q and "user_id" in q:
                return {"user_id": 1, "role": "admin", "is_active": 1}
            return [{"schedule_id": 1, "status": "overdue", "loan_amount": 100000.0}]
        self.mock_db.side_effect = side_effect
        resp = self.client.get("/admin/loans/amortization/overdue")
        self.assertEqual(resp.status_code, 200)

    # ── Customer loan routes ────────────────────────────────────────

    def test_customer_get_my_loan(self):
        self._login(role="customer", user_id=4)
        call = [0]
        def side_effect(q, p=None, fetch=None, conn=None, cursor=None):
            call[0] += 1
            if call[0] == 1:
                return {"user_id": 4, "role": "customer", "is_active": 1}
            if call[0] == 2:
                return {"loan_id": 1, "sale_id": 10, "loan_amount": 100000.0}
            return [{"schedule_id": 1, "month_number": 1, "status": "unpaid"}]
        self.mock_db.side_effect = side_effect
        resp = self.client.get("/loans/my")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertIn("loan", body)
        self.assertIn("schedule", body)

    def test_customer_my_loan_forbidden_for_admin(self):
        self._login(role="admin")
        resp = self.client.get("/loans/my")
        self.assertEqual(resp.status_code, 403)

    def test_customer_my_loan_unauthorized(self):
        resp = self.client.get("/loans/my")
        self.assertEqual(resp.status_code, 403)

    # ── Admin document routes ───────────────────────────────────────

    def test_get_all_documents_empty(self):
        self._login()
        resp = self.client.get("/admin/documents/")
        self.assertEqual(resp.status_code, 404)

    def test_get_document_by_id_found(self):
        self._login()
        doc = {"document_id": 1, "sale_id": 10, "document_type": "OR",
               "file_url": "http://example.com/doc.pdf", "is_accessible": 1}
        def side_effect(q, p=None, fetch=None, conn=None, cursor=None):
            if "users" in q and "user_id" in q:
                return {"user_id": 1, "role": "admin", "is_active": 1}
            return doc
        self.mock_db.side_effect = side_effect
        resp = self.client.get("/admin/documents/1")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertIn("data", body)

    def test_upload_document_missing_fields(self):
        self._login()
        resp = self.client.post("/admin/documents/sales/10",
                                data=json.dumps({}),
                                content_type="application/json")
        self.assertEqual(resp.status_code, 400)

    def test_upload_document_ok(self):
        self._login()
        resp = self.client.post("/admin/documents/sales/10",
                                data=json.dumps({
                                    "document_type": "OR",
                                    "file_url": "http://example.com/doc.pdf"
                                }),
                                content_type="application/json")
        self.assertEqual(resp.status_code, 201)

    def test_update_document_ok(self):
        self._login()
        resp = self.client.put("/admin/documents/1",
                               data=json.dumps({"is_accessible": 0}),
                               content_type="application/json")
        self.assertEqual(resp.status_code, 200)

    def test_delete_document_ok(self):
        self._login()
        resp = self.client.delete("/admin/documents/1")
        self.assertEqual(resp.status_code, 200)

    # ── Customer document routes ────────────────────────────────────

    def test_customer_get_my_documents_empty(self):
        self._login(role="customer", user_id=4)
        resp = self.client.get("/portal/documents")
        self.assertEqual(resp.status_code, 404)

    def test_customer_get_my_document_by_id_not_found(self):
        self._login(role="customer", user_id=4)
        resp = self.client.get("/portal/documents/999")
        self.assertEqual(resp.status_code, 404)

    # ── New /admin/sales routes ─────────────────────────────────────

    def test_sales_create_loan_unauthorized(self):
        resp = self.client.post("/admin/sales/1/loan",
                                data=json.dumps({"loan_amount": 100000}),
                                content_type="application/json")
        self.assertEqual(resp.status_code, 403)

    def test_sales_create_loan_ok(self):
        self._login()
        call = [0]
        def side_effect(q, p=None, fetch=None, conn=None, cursor=None):
            call[0] += 1
            if call[0] == 1:
                return {"user_id": 1, "role": "admin", "is_active": 1}
            if call[0] == 2:
                return {"sale_id": 1, "sale_price": 500000.0,
                        "agent_id": 3, "created_at": datetime(2025, 1, 1)}
            return 1
        self.mock_db.side_effect = side_effect
        resp = self.client.post("/admin/sales/1/loan",
                                data=json.dumps({
                                    "loan_amount": 100000,
                                    "interest_rate": 6.5,
                                    "term_months": 12,
                                    "down_payment": 20000
                                }),
                                content_type="application/json")
        self.assertEqual(resp.status_code, 201)

    def test_sales_upload_document_ok(self):
        self._login()
        resp = self.client.post("/admin/sales/1/documents",
                                data=json.dumps({
                                    "document_type": "OR",
                                    "file_url": "http://example.com/or.pdf"
                                }),
                                content_type="application/json")
        self.assertEqual(resp.status_code, 201)

    # ── Compute amortization (remaining_balance fix) ────────────────

    def test_compute_amortization_no_fields(self):
        self._login()
        resp = self.client.post("/admin/loans/1/compute",
                                data=json.dumps({}),
                                content_type="application/json")
        self.assertEqual(resp.status_code, 400)

    def test_compute_amortization_ok(self):
        self._login()
        call = [0]
        def side_effect(q, p=None, fetch=None, conn=None, cursor=None):
            call[0] += 1
            if call[0] == 1:
                return {"user_id": 1, "role": "admin", "is_active": 1}
            if call[0] == 2:
                return {"loan_id": 1, "loan_amount": 100000.0,
                        "sale_date": datetime(2025, 1, 15),
                        "interest_rate": 6.5, "term_months": 12}
            if call[0] == 3:
                return {"paid_principal": 5000.0, "paid_count": 2,
                        "last_paid_period": 2}
            return 1
        self.mock_db.side_effect = side_effect
        resp = self.client.post("/admin/loans/1/compute",
                                data=json.dumps({
                                    "interest_rate": 7.0,
                                    "term_months": 12
                                }),
                                content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertIn("successfully", body.get("message", "").lower())

    def test_compute_amortization_all_paid(self):
        self._login()
        call = [0]
        def side_effect(q, p=None, fetch=None, conn=None, cursor=None):
            call[0] += 1
            if call[0] == 1:
                return {"user_id": 1, "role": "admin", "is_active": 1}
            if call[0] == 2:
                return {"loan_id": 1, "loan_amount": 100000.0,
                        "sale_date": datetime(2025, 1, 15),
                        "interest_rate": 6.5, "term_months": 12}
            if call[0] == 3:
                return {"paid_principal": 100000.0, "paid_count": 12,
                        "last_paid_period": 12}
            return None
        self.mock_db.side_effect = side_effect
        resp = self.client.post("/admin/loans/1/compute",
                                data=json.dumps({
                                    "interest_rate": 7.0,
                                    "term_months": 12
                                }),
                                content_type="application/json")
        self.assertEqual(resp.status_code, 400)
        body = resp.get_json()
        self.assertIn("already paid", body.get("message", "").lower())


if __name__ == "__main__":
    unittest.main()
