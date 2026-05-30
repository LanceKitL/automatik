from flask import Blueprint, request
from validators.middleware import role_required,logged_in_required
from controllers.inquiriesController import (
    submitInquiry,
    displayInquiries,
    indexCustomerInquiries,
    assignInquiry,
    resolveInquiry,
    closeInquiry
)

inquiry_bp = Blueprint('inquiry', __name__)


#public
@inquiry_bp.route("/", methods=["POST"])
def create():
    return submitInquiry()

# agent
@inquiry_bp.route("/assign/<int:inquiry_id>", methods=["PUT"])
@logged_in_required
@role_required("agent")
def assign_task(inquiry_id):
    return assignInquiry(inquiry_id)

@inquiry_bp.route("/resolve/<int:inquiry_id>", methods=["PUT"])
@logged_in_required
@role_required("agent")
def resolve_task(inquiry_id):
    return resolveInquiry(inquiry_id)

#customer
@inquiry_bp.route("/my")
@logged_in_required
@role_required("customer","admin")
def index_customer_inquiries():
    return indexCustomerInquiries()

#admin
@inquiry_bp.route("/")
@logged_in_required
@role_required("admin","agent")
def admin_index():
    return displayInquiries()

@inquiry_bp.route("/close/<int:inquiry_id>", methods=["PUT"])
@logged_in_required
@role_required("admin")
def close_inquiry(inquiry_id):
    return closeInquiry(inquiry_id)