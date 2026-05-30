from flask import Blueprint, request
from validators.middleware import role_required,logged_in_required
from controllers.inquiriesController import (
    submitInquiry,
    displayInquiries,
    indexCustomerInquiries,
    assignInquiry,
)

inquiry_bp = Blueprint('inquiry', __name__)


#public
@inquiry_bp.route("/", methods=["POST"])
def create():
    return submitInquiry()

#agent
@inquiry_bp.route("/assign/<int:inquiry_id>", methods=["PUT"])
@logged_in_required
@role_required("agent")
def assign_task(inquiry_id):
    return assignInquiry(inquiry_id)

#customer
@inquiry_bp.route("/my")
@logged_in_required
@role_required("customer","admin")
def index_customer_inquiries():
    return indexCustomerInquiries()

#admin
@inquiry_bp.route("/")
@role_required("admin","agent")
def admin_index():
    return displayInquiries()