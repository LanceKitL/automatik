from flask import Blueprint, session
from validators.middleware import role_required, logged_in_required
from controllers.financingController import (
    getAllLoans,
    getLoanById,
    createLoan,
    updateLoanStatus,
    getLoanSchedule,
    getMyLoan,
    updateScheduleStatus,
    getOverdueSchedules,
    computeAmortization
)

financing_bp = Blueprint('financing', __name__)

# GET /loans/
@financing_bp.route("/")
@logged_in_required
@role_required("admin")
def get_all_loans(): return getAllLoans()

# GET /loans/<loan_id>
@financing_bp.route("/<int:loan_id>")
@logged_in_required
@role_required("admin")
def get_loan(loan_id): return getLoanById(loan_id)

# POST /loans/sales/<sale_id>/loan
@financing_bp.route("/sales/<int:sale_id>/loan", methods=["POST"])
@logged_in_required
@role_required("admin")
def create_loan(sale_id): return createLoan(sale_id)

# PUT /loans/<loan_id>
@financing_bp.route("/<int:loan_id>", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update_loan(loan_id): return updateLoanStatus(loan_id)

# GET /loans/<loan_id>/schedule
@financing_bp.route("/<int:loan_id>/schedule")
@logged_in_required
@role_required("admin")
def get_loan_schedule(loan_id): return getLoanSchedule(loan_id)

# PUT /loans/amortization/<schedule_id>/status
@financing_bp.route("/amortization/<int:schedule_id>/status", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update_schedule_status(schedule_id): return updateScheduleStatus(schedule_id)

# GET /loans/amortization/overdue
@financing_bp.route("/amortization/overdue")
@logged_in_required
@role_required("admin")
def get_overdue_schedules(): return getOverdueSchedules()

# POST /loans/<loan_id>/compute
@financing_bp.route("/<int:loan_id>/compute", methods=["POST"])
@logged_in_required
@role_required("admin")
def compute_amortization(loan_id): return computeAmortization(loan_id)

# GET /loans/my - customer
@financing_bp.route("/my")
@logged_in_required
@role_required("customer")
def get_my_loan():
    customer_id = session["user"]
    return getMyLoan(customer_id)