"""
Sales, Loans, Payments, Insurance, Contracts & Amortization routes.

Prefix-less blueprint; endpoints use /admin/sales/... and /sales/...
"""

from flask import Blueprint
from validators.middleware import role_required, logged_in_required
from controllers.salesController import (
    listSales, getSale, createSale, updateSaleStatus,
    getMySales, getMySale,
    getSaleContract, createContract, signContract, updateContract,
    listInsurance, addInsurance, updateInsurance,
    listLoans, getLoan, createLoan, updateLoanStatus, getLoanSchedule, getMyLoans,
    updateAmortizationStatus, getOverdueAmortizations, recomputeAmortization
)
from controllers.paymentsController import (
    listPayments, getPayment, recordPayment,
    getMyPayments, getSalePayments, getPaymentSummary
)

sales_bp = Blueprint('sales', __name__)

# ══════════════════════════════════════════════════════════════════════════
# SALES
# ══════════════════════════════════════════════════════════════════════════

# ── Admin ────────────────────────────────────────────────────────────────

@sales_bp.route("/admin/sales", methods=["GET"])
@logged_in_required
@role_required("admin")
def index_sales():
    """List all sales (with optional filters)."""
    return listSales()

@sales_bp.route("/admin/sales/<int:sale_id>", methods=["GET"])
@logged_in_required
@role_required("admin")
def show_sale(sale_id):
    """Get full sale detail: loan, payments, insurance, contract."""
    return getSale(sale_id)

@sales_bp.route("/admin/sales", methods=["POST"])
@logged_in_required
@role_required("admin")
def create_new_sale():
    """Create a sale (cash or installment, optionally from an inquiry)."""
    return createSale()

@sales_bp.route("/admin/sales/<int:sale_id>/status", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update_status(sale_id):
    """Transition sale status (pending → completed / cancelled)."""
    return updateSaleStatus(sale_id)

# ── Customer ─────────────────────────────────────────────────────────────

@sales_bp.route("/sales/my", methods=["GET"])
@logged_in_required
def my_sales():
    """List the current customer's own sales."""
    return getMySales()

@sales_bp.route("/sales/my/<int:sale_id>", methods=["GET"])
@logged_in_required
def my_sale(sale_id):
    """Get a single sale for the current customer."""
    return getMySale(sale_id)

# ══════════════════════════════════════════════════════════════════════════
# CONTRACTS
# ══════════════════════════════════════════════════════════════════════════

@sales_bp.route("/admin/sales/<int:sale_id>/contract", methods=["GET"])
@logged_in_required
@role_required("admin", "agent")
def show_contract(sale_id):
    """Get the contract for a sale."""
    return getSaleContract(sale_id)

@sales_bp.route("/admin/sales/<int:sale_id>/contract", methods=["POST"])
@logged_in_required
@role_required("admin")
def create_new_contract(sale_id):
    """Create a draft contract for a sale."""
    return createContract(sale_id)

@sales_bp.route("/admin/sales/<int:sale_id>/contract/sign", methods=["PUT"])
@logged_in_required
@role_required("admin")
def sign_sale_contract(sale_id):
    """Sign (finalise) a sale contract."""
    return signContract(sale_id)

@sales_bp.route("/admin/sales/<int:sale_id>/contract", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update_sale_contract(sale_id):
    """Update contract URL and/or status."""
    return updateContract(sale_id)

# ══════════════════════════════════════════════════════════════════════════
# INSURANCE
# ══════════════════════════════════════════════════════════════════════════

@sales_bp.route("/admin/insurance", methods=["GET"])
@logged_in_required
@role_required("admin")
def index_insurance():
    """List all insurance records."""
    return listInsurance()

@sales_bp.route("/admin/sales/<int:sale_id>/insurance", methods=["POST"])
@logged_in_required
@role_required("admin")
def create_insurance(sale_id):
    """Add an insurance policy to a sale."""
    return addInsurance(sale_id)

@sales_bp.route("/admin/insurance/<int:insurance_id>", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update_insurance(insurance_id):
    """Update an insurance record (dates, status, provider)."""
    return updateInsurance(insurance_id)

# ══════════════════════════════════════════════════════════════════════════
# LOANS
# ══════════════════════════════════════════════════════════════════════════

# ── Admin ────────────────────────────────────────────────────────────────

@sales_bp.route("/admin/loans", methods=["GET"])
@logged_in_required
@role_required("admin")
def index_loans():
    """List all loans (with optional status filter)."""
    return listLoans()

@sales_bp.route("/admin/loans/<int:loan_id>", methods=["GET"])
@logged_in_required
@role_required("admin")
def show_loan(loan_id):
    """Get a single loan with its amortisation schedule."""
    return getLoan(loan_id)

@sales_bp.route("/admin/sales/<int:sale_id>/loan", methods=["POST"])
@logged_in_required
@role_required("admin")
def create_new_loan(sale_id):
    """Create a loan for an existing installment sale."""
    return createLoan(sale_id)

@sales_bp.route("/admin/loans/<int:loan_id>", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update_loan(loan_id):
    """Approve or reject a loan."""
    return updateLoanStatus(loan_id)

@sales_bp.route("/admin/loans/<int:loan_id>/schedule", methods=["GET"])
@logged_in_required
@role_required("admin")
def show_loan_schedule(loan_id):
    """Get the amortisation schedule for a loan."""
    return getLoanSchedule(loan_id)

# ── Customer ─────────────────────────────────────────────────────────────

@sales_bp.route("/loans/my", methods=["GET"])
@logged_in_required
def my_loans():
    """List the current customer's own loans."""
    return getMyLoans()

# ══════════════════════════════════════════════════════════════════════════
# AMORTIZATION
# ══════════════════════════════════════════════════════════════════════════

@sales_bp.route("/admin/amortization/<int:schedule_id>/status", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update_amortization(schedule_id):
    """Manually mark an amortization entry as paid / overdue."""
    return updateAmortizationStatus(schedule_id)

@sales_bp.route("/admin/amortization/overdue", methods=["GET"])
@logged_in_required
@role_required("admin")
def overdue_amortizations():
    """List all overdue amortization entries."""
    return getOverdueAmortizations()

@sales_bp.route("/admin/loans/<int:loan_id>/compute", methods=["POST"])
@logged_in_required
@role_required("admin")
def recompute(loan_id):
    """Recompute and regenerate the amortisation schedule for a loan."""
    return recomputeAmortization(loan_id)

# ══════════════════════════════════════════════════════════════════════════
# PAYMENTS
# ══════════════════════════════════════════════════════════════════════════

# ── Admin ────────────────────────────────────────────────────────────────

@sales_bp.route("/admin/payments", methods=["GET"])
@logged_in_required
@role_required("admin")
def index_payments():
    """List all payments (with optional date/method filters)."""
    return listPayments()

@sales_bp.route("/admin/payments/<int:payment_id>", methods=["GET"])
@logged_in_required
@role_required("admin")
def show_payment(payment_id):
    """Get a single payment record."""
    return getPayment(payment_id)

@sales_bp.route("/admin/sales/<int:sale_id>/payments", methods=["POST"])
@logged_in_required
@role_required("admin")
def create_payment(sale_id):
    """Record a payment against a sale."""
    return recordPayment(sale_id)

@sales_bp.route("/admin/sales/<int:sale_id>/payments", methods=["GET"])
@logged_in_required
@role_required("admin")
def sale_payments(sale_id):
    """Get all payments for a specific sale."""
    return getSalePayments(sale_id)

@sales_bp.route("/admin/payments/summary", methods=["GET"])
@logged_in_required
@role_required("admin")
def payment_summary():
    """Get aggregated payment summary stats."""
    return getPaymentSummary()

# ── Customer ─────────────────────────────────────────────────────────────

@sales_bp.route("/payments/my", methods=["GET"])
@logged_in_required
def my_payments():
    """List the current customer's own payments."""
    return getMyPayments()
