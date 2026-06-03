from flask import Blueprint, request
from validators.middleware import role_required, logged_in_required
from controllers.customerportalController import (
    index,
    get_customer_inquiries,
    create_customer_inquiry,
    get_customer_inquiry,
    get_customer_warranty_claims,
    create_customer_warranty_claim,
    get_customer_warranty_claim,
    get_customer_sales,
    get_customer_sale,
    get_profile,
    update_profile,
    get_vehicles,
    get_vehicle,
    get_documents,
    get_document,
    mark_notification_read,
)

customerportal_bp = Blueprint("customerportal", __name__)

@customerportal_bp.route("/")
@logged_in_required
@role_required("customer")
def dashboard():
    return index()

@customerportal_bp.route("/inquiries", methods=["GET", "POST"])
@logged_in_required
@role_required("customer")
def handle_inquiries():
    if request.method == "GET":
        return get_customer_inquiries()
    return create_customer_inquiry()

@customerportal_bp.route("/inquiries/<int:inquiry_id>")
@logged_in_required
@role_required("customer")
def inquiry_detail(inquiry_id):
    return get_customer_inquiry(inquiry_id)

@customerportal_bp.route("/warranty-claims", methods=["GET", "POST"])
@logged_in_required
@role_required("customer")
def handle_warranty_claims():
    if request.method == "GET":
        return get_customer_warranty_claims()
    return create_customer_warranty_claim()

@customerportal_bp.route("/warranty-claims/<int:claim_id>")
@logged_in_required
@role_required("customer")
def warranty_claim_detail(claim_id):
    return get_customer_warranty_claim(claim_id)

@customerportal_bp.route("/sales")
@logged_in_required
@role_required("customer")
def sales_list():
    return get_customer_sales()

@customerportal_bp.route("/sales/<int:sale_id>")
@logged_in_required
@role_required("customer")
def sale_detail(sale_id):
    return get_customer_sale(sale_id)

@customerportal_bp.route("/profile", methods=["GET", "PUT"])
@logged_in_required
@role_required("customer")
def handle_profile():
    if request.method == "GET":
        return get_profile()
    return update_profile()

@customerportal_bp.route("/vehicles")
@logged_in_required
@role_required("customer")
def vehicles_list():
    return get_vehicles()

@customerportal_bp.route("/vehicles/<int:vehicle_id>")
@logged_in_required
@role_required("customer")
def vehicle_detail(vehicle_id):
    return get_vehicle(vehicle_id)

@customerportal_bp.route("/documents")
@logged_in_required
@role_required("customer")
def documents_list():
    return get_documents()

@customerportal_bp.route("/documents/<int:document_id>")
@logged_in_required
@role_required("customer")
def document_detail(document_id):
    return get_document(document_id)

@customerportal_bp.route("/notifications/<int:notification_id>/read", methods=["PUT"])
@logged_in_required
@role_required("customer")
def read_notification(notification_id):
    return mark_notification_read(notification_id)
