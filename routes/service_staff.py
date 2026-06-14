from flask import Blueprint, request, jsonify
from validators.middleware import role_required, logged_in_required
from controllers.serviceStaffController import (
    getServiceStaffDashboard,
    getCustomerListHandler,
    getServiceHistoryHandler,
    createBookingHandler,
    updateBookingNotesHandler,
)
from controllers.serviceController import (
    listAllBookingsHandler,
    listAllWarrantyClaimsHandler,
    updateWarrantyStatusHandler,
)

service_staff_bp = Blueprint("service_staff", __name__)


@service_staff_bp.route("/dashboard")
@logged_in_required
@role_required("service_staff", "service_advisor")
def dashboard():
    return getServiceStaffDashboard()


@service_staff_bp.route("/bookings")
@logged_in_required
@role_required("service_staff", "service_advisor")
def index_bookings():
    return listAllBookingsHandler()


@service_staff_bp.route("/bookings", methods=["POST"])
@logged_in_required
@role_required("service_staff", "service_advisor")
def create_booking():
    return createBookingHandler()


@service_staff_bp.route("/bookings/<int:booking_id>/notes", methods=["PUT"])
@logged_in_required
@role_required("service_staff", "service_advisor")
def update_notes(booking_id):
    return updateBookingNotesHandler(booking_id)


@service_staff_bp.route("/customers")
@logged_in_required
@role_required("service_staff", "service_advisor")
def list_customers():
    return getCustomerListHandler()


@service_staff_bp.route("/history")
@logged_in_required
@role_required("service_staff", "service_advisor")
def history():
    return getServiceHistoryHandler()


@service_staff_bp.route("/warranty")
@logged_in_required
@role_required("service_staff", "service_advisor")
def index_warranty():
    return listAllWarrantyClaimsHandler()


@service_staff_bp.route("/warranty/<int:claim_id>/review", methods=["PUT"])
@logged_in_required
@role_required("service_staff", "service_advisor")
def review_warranty(claim_id):
    return updateWarrantyStatusHandler(claim_id, "under_review")


@service_staff_bp.route("/warranty/<int:claim_id>/approve", methods=["PUT"])
@logged_in_required
@role_required("service_staff", "service_advisor")
def approve_warranty(claim_id):
    return updateWarrantyStatusHandler(claim_id, "approved")


@service_staff_bp.route("/warranty/<int:claim_id>/reject", methods=["PUT"])
@logged_in_required
@role_required("service_staff", "service_advisor")
def reject_warranty(claim_id):
    data = request.get_json(silent=True) or {}
    resolution = data.get("resolution_text", "")
    if not resolution:
        return jsonify({"message": "Resolution note is required when rejecting a claim."}), 400
    return updateWarrantyStatusHandler(claim_id, "rejected")


@service_staff_bp.route("/warranty/<int:claim_id>/resolve", methods=["PUT"])
@logged_in_required
@role_required("service_staff", "service_advisor")
def resolve_warranty(claim_id):
    return updateWarrantyStatusHandler(claim_id, "resolved")
