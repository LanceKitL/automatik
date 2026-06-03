from flask import Blueprint
from validators.middleware import logged_in_required, role_required
from controllers.customerportalController import (
    get_dashboard,
    browse_available_vehicles,
    get_customer_sales,
    get_customer_sale_detail,
    get_customer_payments,
    get_customer_amortization,
    get_customer_documents,
    get_customer_document_detail,
    get_customer_inquiries,
    create_customer_inquiry,
    get_customer_notifications,
    mark_customer_notification_read,
    update_customer_profile,
    get_customer_insurance,
    get_customer_warranty_claims,
    create_customer_warranty_claim,
)

customerportal_bp = Blueprint("customerportal", __name__)


@customerportal_bp.route("/dashboard", methods=["GET"])
@logged_in_required
@role_required("customer")
def customer_dashboard():
    return get_dashboard()


@customerportal_bp.route("/vehicles", methods=["GET"])
@logged_in_required
@role_required("customer")
def customer_vehicles():
    return browse_available_vehicles()


@customerportal_bp.route("/sales", methods=["GET"])
@logged_in_required
@role_required("customer")
def customer_sales():
    return get_customer_sales()


@customerportal_bp.route("/sales/<int:sale_id>", methods=["GET"])
@logged_in_required
@role_required("customer")
def customer_sale_detail(sale_id):
    return get_customer_sale_detail(sale_id)


@customerportal_bp.route("/payments", methods=["GET"])
@logged_in_required
@role_required("customer")
def customer_payments():
    return get_customer_payments()


@customerportal_bp.route("/amortization", methods=["GET"])
@logged_in_required
@role_required("customer")
def customer_amortization():
    return get_customer_amortization()


@customerportal_bp.route("/documents", methods=["GET"])
@logged_in_required
@role_required("customer")
def customer_documents():
    return get_customer_documents()


@customerportal_bp.route("/documents/<int:document_id>", methods=["GET"])
@logged_in_required
@role_required("customer")
def customer_document_detail(document_id):
    return get_customer_document_detail(document_id)


@customerportal_bp.route("/inquiries", methods=["GET"])
@logged_in_required
@role_required("customer")
def customer_inquiries():
    return get_customer_inquiries()


@customerportal_bp.route("/inquiries", methods=["POST"])
@logged_in_required
@role_required("customer")
def customer_create_inquiry():
    return create_customer_inquiry()


@customerportal_bp.route("/notifications", methods=["GET"])
@logged_in_required
@role_required("customer")
def customer_notifications():
    return get_customer_notifications()


@customerportal_bp.route("/notifications/<int:notification_id>/read", methods=["PUT"])
@logged_in_required
@role_required("customer")
def customer_notification_read(notification_id):
    return mark_customer_notification_read(notification_id)


@customerportal_bp.route("/profile", methods=["PUT"])
@logged_in_required
@role_required("customer")
def customer_profile():
    return update_customer_profile()


@customerportal_bp.route("/insurance", methods=["GET"])
@logged_in_required
@role_required("customer")
def customer_insurance():
    return get_customer_insurance()


@customerportal_bp.route("/warranty", methods=["GET"])
@logged_in_required
@role_required("customer")
def customer_warranty_claims():
    return get_customer_warranty_claims()


@customerportal_bp.route("/warranty", methods=["POST"])
@logged_in_required
@role_required("customer")
def customer_create_warranty_claim():
    return create_customer_warranty_claim()
