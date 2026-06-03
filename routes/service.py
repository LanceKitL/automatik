from flask import Blueprint
from validators.middleware import role_required, logged_in_required
from controllers.serviceController import (
    listServiceSlotsHandler,
    getServiceSlotHandler,
    createServiceSlotHandler,
    updateServiceSlotHandler,
    deleteServiceSlotHandler,
    listMyBookingsHandler,
    createBookingHandler,
    updateBookingStatusHandler,
    listWarrantyClaimsHandler,
    submitWarrantyClaimHandler,
)

service_bp = Blueprint("service", __name__)

# --- Slots (Public: GET, Admin: POST/PUT/DELETE) ---

@service_bp.route("/slots", methods=["GET"])
def list_slots():
    return listServiceSlotsHandler()


@service_bp.route("/slots/<int:slot_id>", methods=["GET"])
def get_slot(slot_id):
    return getServiceSlotHandler(slot_id)


@service_bp.route("/slots", methods=["POST"])
@logged_in_required
@role_required("admin")
def create_slot():
    return createServiceSlotHandler()


@service_bp.route("/slots/<int:slot_id>", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update_slot(slot_id):
    return updateServiceSlotHandler(slot_id)


@service_bp.route("/slots/<int:slot_id>", methods=["DELETE"])
@logged_in_required
@role_required("admin")
def delete_slot(slot_id):
    return deleteServiceSlotHandler(slot_id)


# --- Bookings (Customer: POST/GET/cancel, Admin: confirm/complete handled via admin blueprint) ---

@service_bp.route("/bookings/my", methods=["GET"])
@logged_in_required
@role_required("customer")
def list_my_bookings():
    return listMyBookingsHandler()


@service_bp.route("/bookings", methods=["POST"])
@logged_in_required
@role_required("customer")
def create_booking():
    return createBookingHandler()


@service_bp.route("/bookings/<int:booking_id>/cancel", methods=["PUT"])
@logged_in_required
@role_required("customer")
def cancel_booking(booking_id):
    return updateBookingStatusHandler(booking_id, "cancelled")


# --- Warranty (Customer: POST/GET) ---

@service_bp.route("/warranty", methods=["POST"])
@logged_in_required
@role_required("customer")
def submit_claim():
    return submitWarrantyClaimHandler()


@service_bp.route("/warranty/my", methods=["GET"])
@logged_in_required
@role_required("customer")
def list_my_claims():
    return listWarrantyClaimsHandler()
