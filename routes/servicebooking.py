from flask import Blueprint, request, jsonify
from validators.middleware import role_required, logged_in_required

from controllers.serviceController import(
    getServicesSlot,
    createServiceSlots,
    getServiceBooking,
    creatServiceBooking,
    updServiceBooking,
    getWarrantyClaims,
    submitWarrantyClaims,
    updWarrantyClaims
)

services_bp = Blueprint('Service',__name__)

@services_bp.route('/service-slots', methods = ["GET"])
def ServiceSlot(): return getServicesSlot()

@services_bp.route('/service-slots', methods = ["POST"])
@logged_in_required
@role_required("admin")
def postServiceSlot(): return createServiceSlots()


@services_bp.route('/booking/<int:id>', methods = ["GET"])
def ServiceBookings(id): return getServiceBooking(id)

@services_bp.route('/booking', methods = ["POST"])
def postServiceBooking(): return creatServiceBooking()

@services_bp.route('/booking/<int:booking_id>', methods = ["PUT"])
def updateServiceBooking(booking_id): return updServiceBooking(booking_id)

@services_bp.route('/warranty-claims', methods =["GET"] )
def WarrantyClaims(): return getWarrantyClaims()

@services_bp.route('/warranty-claims', methods =["POST"])
def postWarrantyClaim(): return submitWarrantyClaims()

@services_bp.route('/warranty-claims/<int:claim_id>')
def updateWarrantyClaim(claim_id): return updateWarrantyClaim(claim_id)






