from flask import Blueprint
from validators.middleware import role_required, logged_in_required
from controllers.paymentsController import (
    getAllPayments,
    showPayments,
    recordPayments,
    showMyPayments,
    showSalesPayments,
    getPaymentsSummarry
)

payment_bp = Blueprint('payments',__name__)




@payment_bp.route("/payments")
@logged_in_required
@role_required("admin")
def AllPayments(): return getAllPayments()

