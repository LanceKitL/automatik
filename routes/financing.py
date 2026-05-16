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
    getOverdueSchedules
)

financing_bp = Blueprint('financing', __name__)

@financing_bp.route("/")
@logged_in_required
@role_required("admin")
def get_all_loans(): return getAllLoans()

@financing_bp.route("/<int:loan_id>")
@logged_in_required
@role_required("admin")
def get_loan(loan_id): return getLoanById(loan_id)

@financing_bp.route("/sales/<int:sale_id>/loan", methods=["POST"])
@logged_in_required
@role_required("admin")
def create_loan(sale_id): return createLoan(sale_id)

@financing_bp.route("/<int:loan_id>", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update_loan(loan_id): return updateLoanStatus(loan_id)


@financing_bp.route("/<int:loan_id>/schedule")
@logged_in_required
@role_required("admin")
def get_loan_schedule(loan_id): return getLoanSchedule(loan_id)

@financing_bp.route("/my")
@logged_in_required
@role_required("customer")
def get_my_loan():
    customer_id = session["user"]
    return getMyLoan(customer_id)

@financing_bp.route("/amortization/<int:schedule_id>/status", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update_schedule_status(schedule_id): return updateScheduleStatus(schedule_id)

@financing_bp.route("/amortization/overdue")
@logged_in_required
@role_required("admin")
def get_overdue_schedules(): return getOverdueSchedules()