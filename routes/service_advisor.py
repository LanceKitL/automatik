"""
Service Advisor portal routes — booking self-assignment, status updates, warranty viewing.

All endpoints require service_advisor role.
Prefix: /service_advisor
"""

from flask import Blueprint
from validators.middleware import role_required, logged_in_required
from controllers.serviceAdvisorController import getServiceAdvisorDashboard
from controllers.serviceController import (
    listAllBookingsHandler,
    getMyBookingsHandler,
    assignToSelfHandler,
    assignAndOpenIntakeHandler,
    createEstimateHandler,
    transmitEstimateHandler,
    signEstimateHandler,
    updateBookingStatusHandler,
    updateTechnicianNotesHandler,
    listAllWarrantyClaimsHandler,
    getWarrantyClaimDetailHandler,
)

service_advisor_bp = Blueprint("service_advisor", __name__)


@service_advisor_bp.route("/dashboard")
@logged_in_required
@role_required("service_advisor")
def dashboard():
    """Aggregated stats for service advisor home."""
    return getServiceAdvisorDashboard()


# ── Bookings ───────────────────────────────────────────────────────────────


@service_advisor_bp.route("/bookings")
@logged_in_required
@role_required("service_advisor")
def index_bookings():
    """List all service bookings with assigned_to info."""
    return listAllBookingsHandler()


@service_advisor_bp.route("/bookings/mine")
@logged_in_required
@role_required("service_advisor")
def my_bookings():
    """List bookings assigned to the current advisor."""
    return getMyBookingsHandler()


@service_advisor_bp.route("/bookings/<int:booking_id>/assign", methods=["PUT"])
@logged_in_required
@role_required("service_advisor")
def assign_self(booking_id):
    """Self-assign a booking to the current advisor."""
    return assignToSelfHandler(booking_id)


@service_advisor_bp.route("/bookings/<int:booking_id>/status", methods=["PUT"])
@logged_in_required
@role_required("service_advisor")
def update_booking_status(booking_id):
    """Update booking status (confirmed / completed / cancelled). Pass ?status= in body."""
    from flask import request
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    if new_status not in ("confirmed", "completed", "cancelled"):
        from flask import jsonify
        return jsonify({"message": "status must be 'confirmed', 'completed', or 'cancelled'."}), 400
    return updateBookingStatusHandler(booking_id, new_status)


@service_advisor_bp.route("/bookings/<int:booking_id>/notes", methods=["PUT"])
@logged_in_required
@role_required("service_advisor")
def update_notes(booking_id):
    """Update technician notes for a booking."""
    return updateTechnicianNotesHandler(booking_id)


# ── Intake & Estimate ──────────────────────────────────────────────────────


@service_advisor_bp.route("/bookings/<int:booking_id>/assign-intake", methods=["PUT"])
@logged_in_required
@role_required("service_advisor")
def assign_intake(booking_id):
    """Self-assign a booking and open intake (status → draft_estimate)."""
    return assignAndOpenIntakeHandler(booking_id)


@service_advisor_bp.route("/bookings/<int:booking_id>/estimate", methods=["PUT"])
@logged_in_required
@role_required("service_advisor")
def save_estimate(booking_id):
    """Save or update the estimate_data for a booking."""
    return createEstimateHandler(booking_id)


@service_advisor_bp.route("/bookings/<int:booking_id>/transmit", methods=["PUT"])
@logged_in_required
@role_required("service_advisor")
def transmit_estimate(booking_id):
    """Lock estimate and set status to awaiting_signature."""
    return transmitEstimateHandler(booking_id)


@service_advisor_bp.route("/bookings/<int:booking_id>/sign", methods=["PUT"])
@logged_in_required
@role_required("service_advisor")
def sign_estimate(booking_id):
    """Sign the estimate (status → in_progress)."""
    return signEstimateHandler(booking_id)


# ── Warranty Claims ────────────────────────────────────────────────────────


@service_advisor_bp.route("/warranty")
@logged_in_required
@role_required("service_advisor")
def index_warranty():
    """List all warranty claims."""
    return listAllWarrantyClaimsHandler()


@service_advisor_bp.route("/warranty/<int:claim_id>")
@logged_in_required
@role_required("service_advisor")
def show_warranty(claim_id):
    """Get warranty claim detail with linked service bookings."""
    return getWarrantyClaimDetailHandler(claim_id)
