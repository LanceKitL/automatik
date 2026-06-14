from flask import Blueprint, request
from validators.middleware import role_required, logged_in_required
from controllers.customerportalController import (
    index, # dashboard
    get_customer_sale,
    get_customer_sales,
    get_payment_history,
    get_customer_inquiries,
    get_customer_inquiry,
    get_customer_warranty_claims,
    create_customer_warranty_claim,
    get_customer_warranty_claim,
    get_profile,
    get_documents,
    get_document,
    get_amortization_schedule,
    payAmortization,
    get_insurance,
    getRecentNotifications,
    getAllNotifications,
    reserveVehicle,
    payReservationFee,
)
from controllers.vehicleController import (
    getVehicles,
    showVehicle
)

from controllers.inquiriesController import (
    submitInquiry
)

from controllers.profileController import (
    update_profile,
)

from controllers.notificationController import (
    getNotifications,
    markAsRead
)

from controllers.paymentsController import uploadPaymentProof

customerportal_bp = Blueprint("customerportal", __name__)

# --------- DASHBOARD ------------
@customerportal_bp.route("/")
@logged_in_required
@role_required("customer")
def dashboard():
    """GET /customer-portal/
    Customer portal dashboard.
    Returns aggregated dashboard data: active sales count, next payment due/amount,
    recent documents, owned vehicles, open inquiries, and unread notifications.
    Requires logged-in customer role.
    """
    return index()

# --------- BROWSE VEHICLE ------------
@customerportal_bp.route("/vehicles")
@logged_in_required
@role_required("customer")
def vehicles_list():
    """GET /customer-portal/vehicles
    List all available vehicles for browsing.
    Requires logged-in customer role.
    Delegates to vehicleController.getVehicles().
    """
    return getVehicles()

@customerportal_bp.route("/vehicles/<int:vehicle_id>")
@logged_in_required
@role_required("customer")
def vehicle_detail(vehicle_id):
    """GET /customer-portal/vehicles/<vehicle_id>
    View details of a specific vehicle.
    Path parameter: vehicle_id (int) — the vehicle to retrieve.
    Requires logged-in customer role.
    Delegates to vehicleController.showVehicle(vehicle_id).
    """
    return showVehicle(vehicle_id)


@customerportal_bp.route("/vehicles/<int:vehicle_id>/reserve", methods=["POST"])
@logged_in_required
@role_required("customer")
def reserve_vehicle(vehicle_id):
    """POST /customer-portal/vehicles/<vehicle_id>/reserve
    Reserve a vehicle (changes status to 'reserved', creates an inquiry).
    Requires logged-in customer role.
    """
    return reserveVehicle(vehicle_id)

@customerportal_bp.route("/reservations/<int:inquiry_id>/pay", methods=["POST"])
@logged_in_required
@role_required("customer")
def pay_reservation_fee(inquiry_id):
    """POST /customer-portal/reservations/<inquiry_id>/pay
    Record reservation fee payment for a reserved vehicle.
    Requires logged-in customer role.
    """
    return payReservationFee(inquiry_id)

# --------- OWN SALES ------------
@customerportal_bp.route("/sales")
@logged_in_required
@role_required("customer")
def sales_list():
    """GET /customer-portal/sales
    List all sales/purchases belonging to the authenticated customer.
    Requires logged-in customer role.
    Delegates to customerportalController.get_customer_sales().
    """
    return get_customer_sales()

@customerportal_bp.route("/sales/<int:sale_id>")
@logged_in_required
@role_required("customer")
def sale_detail(sale_id):
    """GET /customer-portal/sales/<sale_id>
    View details of a single sale/purchase.
    Path parameter: sale_id (int) — the sale to retrieve.
    Requires logged-in customer role.
    Delegates to customerportalController.get_customer_sale(sale_id).
    """
    return get_customer_sale(sale_id)

# --------- PAYMENT HISTORY ------------
@customerportal_bp.route("/payments")
@logged_in_required
@role_required("customer")
def payment():
    """GET /customer-portal/payments
    Retrieve payment history for the authenticated customer.
    Requires logged-in customer role.
    Delegates to customerportalController.get_payment_history().
    """
    return get_payment_history()

@customerportal_bp.route("/payments/<int:payment_id>/upload-proof", methods=["POST"])
@logged_in_required
@role_required("customer")
def payment_upload_proof(payment_id):
    """POST /customer-portal/payments/<payment_id>/upload-proof
    Upload a screenshot as proof of payment.
    Requires logged-in customer role.
    Delegates to paymentsController.uploadPaymentProof(payment_id).
    """
    return uploadPaymentProof(payment_id)

# --------- FULL AMORTIZATION SCHEDULE ------------
@customerportal_bp.route('/amortization')
@logged_in_required
@role_required("customer")
def get_amortization():
    """GET /customer-portal/amortization
    Retrieve the full amortization schedule for all approved loans
    belonging to the authenticated customer.
    Requires logged-in customer role.
    Delegates to customerportalController.get_amortization_schedule().
    """
    return get_amortization_schedule()

@customerportal_bp.route("/amortization/<int:schedule_id>/pay", methods=["POST"])
@logged_in_required
@role_required("customer")
def pay_amortization(schedule_id):
    """POST /customer-portal/amortization/<schedule_id>/pay
    Submit a payment for an amortization entry with screenshot proof.
    Requires logged-in customer role.
    Delegates to customerportalController.payAmortization(schedule_id).
    """
    return payAmortization(schedule_id)

# --------- DOCUMENTS ------------
@customerportal_bp.route("/documents")
@logged_in_required
@role_required("customer")
def documents_list():
    """GET /customer-portal/documents
    List all accessible documents for the authenticated customer.
    Requires logged-in customer role.
    Delegates to customerportalController.get_documents().
    """
    return get_documents()

@customerportal_bp.route("/documents/<int:document_id>")
@logged_in_required
@role_required("customer")
def document_detail(document_id):
    """GET /customer-portal/documents/<document_id>
    View a single document.
    Path parameter: document_id (int) — the document to retrieve.
    Requires logged-in customer role and that the document is accessible.
    Delegates to customerportalController.get_document(document_id).
    """
    return get_document(document_id)

# --------- INQUIRIES ------------
@customerportal_bp.route("/inquiries", methods=["GET", "POST"])
@logged_in_required
@role_required("customer")
def handle_inquiries():
    """GET /customer-portal/inquiries  |  POST /customer-portal/inquiries
    GET:  List all inquiries made by the authenticated customer.
    POST: Submit a new inquiry (delegates to inquiriesController.submitInquiry()).
    Requires logged-in customer role.
    """
    if request.method == "GET":
        return get_customer_inquiries()
    return submitInquiry()

@customerportal_bp.route("/inquiries/<int:inquiry_id>")
@logged_in_required
@role_required("customer")
def inquiry_detail(inquiry_id):
    """GET /customer-portal/inquiries/<inquiry_id>
    View details of a single inquiry.
    Path parameter: inquiry_id (int) — the inquiry to retrieve.
    Requires logged-in customer role.
    Delegates to customerportalController.get_customer_inquiry(inquiry_id).
    """
    return get_customer_inquiry(inquiry_id)

# --------- NOTIFICATIONS ------------
@customerportal_bp.route("/notifications/recent")
@logged_in_required
@role_required("customer")
def recent_notifications():
    """GET /customer-portal/notifications/recent
    Return the 6 most recent notifications (read + unread).
    """
    return getRecentNotifications()


@customerportal_bp.route("/notifications/all")
@logged_in_required
@role_required("customer")
def all_notifications():
    """GET /customer-portal/notifications/all
    Return all notifications for the authenticated customer.
    """
    return getAllNotifications()


@customerportal_bp.route("/notifications")
@logged_in_required
@role_required("customer")
def notifications():
    """GET /customer-portal/notifications
    List all notifications for the authenticated customer,
    ordered by most recent first.
    Requires logged-in customer role.
    Delegates to customerportalController.get_notifications().
    """
    return getNotifications()


@customerportal_bp.route("/notifications/<int:notification_id>/read", methods=["PUT"])
@logged_in_required
@role_required("customer")
def read_notification(notification_id):
    """PUT /customer-portal/notifications/<notification_id>/read
    Mark a single notification as read.
    Path parameter: notification_id (int) — the notification to mark.
    Requires logged-in customer role.
    Delegates to customerportalController.mark_notification_read(notification_id).
    """
    return markAsRead(notification_id)

# --------- USER PROFILE ------------
@customerportal_bp.route("/profile", methods=["GET", "PUT"])
@logged_in_required
@role_required("customer")
def handle_profile():
    """GET /customer-portal/profile  |  PUT /customer-portal/profile
    GET: Retrieve the authenticated customer's profile (account + profile + customer details).
    PUT: Update the authenticated customer's profile.
    Requires logged-in customer role.
    Delegates to customerportalController.get_profile() or profileController.update_profile().
    """
    if request.method == "GET":
        return get_profile()
    
    if request.method == "PUT":
        return update_profile()

# --------- INSURANCE ------------

@customerportal_bp.route("/insurance", methods=["GET"])
@logged_in_required
@role_required("customer")
def handle_insurance():
    """GET /customer-portal/insurance
    Retrieve insurance records for the authenticated customer.
    Requires logged-in customer role.
    Delegates to customerportalController.get_insurance().
    """
    return get_insurance()

# --------- WARRANTY CLAIMS ------------

@customerportal_bp.route("/warranty-claims", methods=["GET", "POST"])
@logged_in_required
@role_required("customer")
def handle_warranty_claims():
    """GET /customer-portal/warranty-claims  |  POST /customer-portal/warranty-claims
    GET:  List all warranty claims submitted by the authenticated customer.
    POST: Submit a new warranty claim.
    Requires logged-in customer role.
    Delegates to customerportalController.get_customer_warranty_claims()
    or create_customer_warranty_claim() accordingly.
    """
    if request.method == "GET":
        return get_customer_warranty_claims()
    
    if request.method == "POST":
        return create_customer_warranty_claim()

@customerportal_bp.route("/warranty-claims/<int:claim_id>")
@logged_in_required
@role_required("customer")
def warranty_claim_detail(claim_id):
    """GET /customer-portal/warranty-claims/<claim_id>
    View details of a single warranty claim.
    Path parameter: claim_id (int) — the warranty claim to retrieve.
    Requires logged-in customer role.
    Delegates to customerportalController.get_customer_warranty_claim(claim_id).
    """
    return get_customer_warranty_claim(claim_id)








