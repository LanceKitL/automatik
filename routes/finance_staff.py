"""
Finance Staff portal routes — loan management, payment viewing, amortization.

All endpoints require finance_staff role.
Prefix: /finance_staff
"""

from flask import Blueprint, jsonify, request
from validators.middleware import role_required, logged_in_required
from controllers.financeController import getFinanceDashboard
from controllers.salesController import (
    listLoans, getLoan, createLoan, updateLoanStatus, getLoanSchedule,
    getOverdueAmortizations, updateAmortizationStatus,
    getEligibleSalesForLoan,
    listInsurance, getInsurance, addInsurance, updateInsurance,
)
from controllers.paymentsController import listPayments, getPayment, getPaymentSummary, recordPayment

finance_staff_bp = Blueprint("finance_staff", __name__)


@finance_staff_bp.route("/dashboard")
@logged_in_required
@role_required("finance_staff")
def dashboard():
    """Aggregated stats for finance staff home."""
    return getFinanceDashboard()


# ── Loans ──────────────────────────────────────────────────────────────────


@finance_staff_bp.route("/loans")
@logged_in_required
@role_required("finance_staff")
def index_loans():
    """List all loans (with optional status filter)."""
    return listLoans()


@finance_staff_bp.route("/loans", methods=["POST"])
@logged_in_required
@role_required("finance_staff")
def create_new_loan():
    """
    Create a loan for an installment sale.

    Expects JSON body with:
        - sale_id (int): the sale to attach the loan to
        - loan_amount (float)
        - interest_rate (float)
        - term_months (int)
        - down_payment (float, optional, default 0)

    Delegates to salesController.createLoan() after extracting sale_id from body.
    """
    data = request.get_json(silent=True) or {}
    sale_id = data.get("sale_id")
    if not sale_id:
        return jsonify({"message": "sale_id is required."}), 400
    return createLoan(sale_id)


@finance_staff_bp.route("/loans/eligible-sales")
@logged_in_required
@role_required("finance_staff")
def eligible_sales():
    """List installment sales without loans (eligible for loan creation)."""
    return getEligibleSalesForLoan()


@finance_staff_bp.route("/loans/<int:loan_id>")
@logged_in_required
@role_required("finance_staff")
def show_loan(loan_id):
    """Get a single loan with its amortisation schedule."""
    return getLoan(loan_id)


@finance_staff_bp.route("/loans/<int:loan_id>/status", methods=["PUT"])
@logged_in_required
@role_required("finance_staff")
def update_loan(loan_id):
    """Approve or reject a loan."""
    return updateLoanStatus(loan_id)


@finance_staff_bp.route("/loans/<int:loan_id>/schedule")
@logged_in_required
@role_required("finance_staff")
def show_loan_schedule(loan_id):
    """Get the amortisation schedule for a loan."""
    return getLoanSchedule(loan_id)


# ── Payments ───────────────────────────────────────────────────────────────


@finance_staff_bp.route("/payments")
@logged_in_required
@role_required("finance_staff")
def index_payments():
    """List all payments (with optional date/method filters)."""
    return listPayments()


@finance_staff_bp.route("/payments/<int:payment_id>")
@logged_in_required
@role_required("finance_staff")
def show_payment(payment_id):
    """Get a single payment record."""
    return getPayment(payment_id)


@finance_staff_bp.route("/payments/summary")
@logged_in_required
@role_required("finance_staff")
def payment_summary():
    """Get aggregated payment summary stats."""
    return getPaymentSummary()


@finance_staff_bp.route("/sales/<int:sale_id>/payments", methods=["POST"])
@logged_in_required
@role_required("finance_staff")
def record_sale_payment(sale_id):
    """Record a payment against a sale (finance staff)."""
    return recordPayment(sale_id)


# ── Amortization ───────────────────────────────────────────────────────────


@finance_staff_bp.route("/amortization/overdue")
@logged_in_required
@role_required("finance_staff")
def overdue_amortizations():
    """List all overdue amortization entries."""
    return getOverdueAmortizations()


@finance_staff_bp.route("/amortization/<int:schedule_id>/status", methods=["PUT"])
@logged_in_required
@role_required("finance_staff")
def update_amortization(schedule_id):
    """Manually mark an amortization entry as paid / overdue."""
    return updateAmortizationStatus(schedule_id)


# ── Insurance ───────────────────────────────────────────────────────────────


@finance_staff_bp.route("/insurance")
@logged_in_required
@role_required("finance_staff")
def index_insurance():
    """List all insurance records."""
    return listInsurance()


@finance_staff_bp.route("/insurance/<int:insurance_id>")
@logged_in_required
@role_required("finance_staff")
def show_insurance(insurance_id):
    """Get a single insurance record."""
    return getInsurance(insurance_id)


@finance_staff_bp.route("/sales/<int:sale_id>/insurance", methods=["POST"])
@logged_in_required
@role_required("finance_staff")
def create_insurance(sale_id):
    """Add an insurance policy to a sale."""
    return addInsurance(sale_id)


@finance_staff_bp.route("/insurance/<int:insurance_id>", methods=["PUT"])
@logged_in_required
@role_required("finance_staff")
def edit_insurance(insurance_id):
    """Update an insurance record."""
    return updateInsurance(insurance_id)
