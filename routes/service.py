from flask import Blueprint
from validators.middleware import role_required, logged_in_required
from controllers.serviceController import (
    listServiceSlotsHandler,
    createServiceSlotHandler,
    listMyBookingsHandler,
    createBookingHandler,
    updateBookingStatusHandler,
    listWarrantyClaimsHandler,
    submitWarrantyClaimHandler
)

service_bp = Blueprint('service', __name__)

@service_bp.route("/service-slots", methods=["GET"])
@logged_in_required
def list_slots(): return listServiceSlotsHandler()

@service_bp.route("/service-slots", methods=["POST"])
@logged_in_required
@role_required("admin")
def create_slot(): return createServiceSlotHandler()

@service_bp.route("/booking", methods=["GET"])
@logged_in_required
def list_bookings(): return listMyBookingsHandler()

@service_bp.route("/booking", methods=["POST"])
@logged_in_required
def create_booking(): return createBookingHandler()

@service_bp.route("/booking/<int:booking_id>", methods=["PUT"])
@logged_in_required
@role_required("admin", "agent")
def update_booking(booking_id): return updateBookingStatusHandler(booking_id)

@service_bp.route("/warranty-claims", methods=["GET"])
@logged_in_required
def list_claims(): return listWarrantyClaimsHandler()

@service_bp.route("/warranty-claims", methods=["POST"])
@logged_in_required
def submit_claim(): return submitWarrantyClaimHandler()