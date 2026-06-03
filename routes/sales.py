from flask import Blueprint
from validators.middleware import role_required, logged_in_required
from controllers.salesController import (
    listSales, getSale, createSale, updateSaleStatus,
    getMySales, getMySale,
    getSaleContract, createContract, signContract,
    listInsurance, addInsurance, updateInsurance,
    listLoans, getLoan, createLoan, updateLoanStatus, getLoanSchedule, getMyLoans,
    updateAmortizationStatus, getOverdueAmortizations, recomputeAmortization
)
from controllers.paymentsController import (
    listPayments, getPayment, recordPayment,
    getMyPayments, getSalePayments, getPaymentSummary
)

sales_bp = Blueprint('sales', __name__)

# Sales — Admin
@sales_bp.route("/admin/sales", methods=["GET"])
@logged_in_required
@role_required("admin")
def index_sales(): return listSales()

@sales_bp.route("/admin/sales/<int:sale_id>", methods=["GET"])
@logged_in_required
@role_required("admin")
def show_sale(sale_id): return getSale(sale_id)

@sales_bp.route("/admin/sales", methods=["POST"])
@logged_in_required
@role_required("admin")
def create_new_sale(): return createSale()

@sales_bp.route("/admin/sales/<int:sale_id>/status", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update_status(sale_id): return updateSaleStatus(sale_id)

# Sales — Customer
@sales_bp.route("/sales/my", methods=["GET"])
@logged_in_required
def my_sales(): return getMySales()

@sales_bp.route("/sales/my/<int:sale_id>", methods=["GET"])
@logged_in_required
def my_sale(sale_id): return getMySale(sale_id)

# Contracts
@sales_bp.route("/admin/sales/<int:sale_id>/contract", methods=["GET"])
@logged_in_required
@role_required("admin", "agent")
def show_contract(sale_id): return getSaleContract(sale_id)

@sales_bp.route("/admin/sales/<int:sale_id>/contract", methods=["POST"])
@logged_in_required
@role_required("admin")
def create_new_contract(sale_id): return createContract(sale_id)

@sales_bp.route("/admin/sales/<int:sale_id>/contract/sign", methods=["PUT"])
@logged_in_required
@role_required("admin")
def sign_sale_contract(sale_id): return signContract(sale_id)

# Insurance
@sales_bp.route("/admin/insurance", methods=["GET"])
@logged_in_required
@role_required("admin")
def index_insurance(): return listInsurance()

@sales_bp.route("/admin/sales/<int:sale_id>/insurance", methods=["POST"])
@logged_in_required
@role_required("admin")
def create_insurance(sale_id): return addInsurance(sale_id)

@sales_bp.route("/admin/insurance/<int:insurance_id>", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update_insurance(insurance_id): return updateInsurance(insurance_id)

# Loans — Admin
@sales_bp.route("/admin/loans", methods=["GET"])
@logged_in_required
@role_required("admin")
def index_loans(): return listLoans()

@sales_bp.route("/admin/loans/<int:loan_id>", methods=["GET"])
@logged_in_required
@role_required("admin")
def show_loan(loan_id): return getLoan(loan_id)

@sales_bp.route("/admin/sales/<int:sale_id>/loan", methods=["POST"])
@logged_in_required
@role_required("admin")
def create_new_loan(sale_id): return createLoan(sale_id)

@sales_bp.route("/admin/loans/<int:loan_id>", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update_loan(loan_id): return updateLoanStatus(loan_id)

@sales_bp.route("/admin/loans/<int:loan_id>/schedule", methods=["GET"])
@logged_in_required
@role_required("admin")
def show_loan_schedule(loan_id): return getLoanSchedule(loan_id)

# Loans — Customer
@sales_bp.route("/loans/my", methods=["GET"])
@logged_in_required
def my_loans(): return getMyLoans()

# Amortization
@sales_bp.route("/admin/amortization/<int:schedule_id>/status", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update_amortization(schedule_id): return updateAmortizationStatus(schedule_id)

@sales_bp.route("/admin/amortization/overdue", methods=["GET"])
@logged_in_required
@role_required("admin")
def overdue_amortizations(): return getOverdueAmortizations()

@sales_bp.route("/admin/loans/<int:loan_id>/compute", methods=["POST"])
@logged_in_required
@role_required("admin")
def recompute(loan_id): return recomputeAmortization(loan_id)

# Payments — Admin
@sales_bp.route("/admin/payments", methods=["GET"])
@logged_in_required
@role_required("admin")
def index_payments(): return listPayments()

@sales_bp.route("/admin/payments/<int:payment_id>", methods=["GET"])
@logged_in_required
@role_required("admin")
def show_payment(payment_id): return getPayment(payment_id)

@sales_bp.route("/admin/sales/<int:sale_id>/payments", methods=["POST"])
@logged_in_required
@role_required("admin")
def create_payment(sale_id): return recordPayment(sale_id)

@sales_bp.route("/admin/sales/<int:sale_id>/payments", methods=["GET"])
@logged_in_required
@role_required("admin")
def sale_payments(sale_id): return getSalePayments(sale_id)

@sales_bp.route("/admin/payments/summary", methods=["GET"])
@logged_in_required
@role_required("admin")
def payment_summary(): return getPaymentSummary()

# Payments — Customer
@sales_bp.route("/payments/my", methods=["GET"])
@logged_in_required
def my_payments(): return getMyPayments()
