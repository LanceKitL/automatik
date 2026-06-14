"""
Vehicle routes — public browsing + admin CRUD for inventory + photos.

Public:  GET  /vehicle/        — list all vehicles
         GET  /vehicle/search  — filtered search
         GET  /vehicle/<id>    — single vehicle detail
Admin:   POST /vehicle/create         — add a vehicle
         PUT  /vehicle/update/<id>
         DELETE /vehicle/delete/<id>
         POST /vehicle/add/photo
         PUT  /vehicle/photo/<photo_id>  — update photo details
         DELETE /vehicle/delete/photo/<photo_id>
         PUT  /vehicle/update/status/<vehicle_id>
         GET  /vehicle/low_stock
"""

from flask import Blueprint, request
from validators.middleware import role_required, logged_in_required
from controllers.vehicleController import (
    createVehicle,
    updateVehicleHandler,
    deleteVehicleHandler,
    searchVehicle,
    getVehicles,
    showVehicle,
    addPhoto,
    updateVehiclePhoto,
    removePhoto,
    updateStatus,
    indexLowStocks,
    guestReserveVehicle,
    guestPayReservationFee,
    handleContactForm,
    handleChatbot,
    handleChatbotStatus,
)

vehicles_bp = Blueprint('vehicles', __name__)

# ── Public endpoints ─────────────────────────────────────────────────────

@vehicles_bp.route("/")
def vehicles():
    """List all vehicles with their primary photo."""
    return getVehicles()

@vehicles_bp.route("/search")
def search():
    """Search/filter vehicles by brand, model, fuel_type, status, price range."""
    params = {
        "brand": request.args.get("brand"),
        "model": request.args.get("model"),
        "fuel_type": request.args.get("fuel_type"),
        "status": request.args.get("status"),
        "price_min": request.args.get("price_min"),
        "price_max": request.args.get("price_max")
    }
    return searchVehicle(params)

@vehicles_bp.route("/<int:id>")
def get_vehicles(id):
    """Get full details of a single vehicle (including photos)."""
    return showVehicle(id)


@vehicles_bp.route("/<int:id>/reserve", methods=["POST"])
def reserve_vehicle(id):
    """Public: guest reserves a vehicle."""
    return guestReserveVehicle(id)


@vehicles_bp.route("/<int:inquiry_id>/pay-reservation", methods=["POST"])
def pay_reservation(inquiry_id):
    """Public: guest pays reservation fee."""
    return guestPayReservationFee(inquiry_id)


@vehicles_bp.route("/contact", methods=["POST"])
def contact():
    """Public: submit contact form."""
    return handleContactForm()


@vehicles_bp.route("/chatbot", methods=["POST"])
def chatbot():
    """Public: chatbot message."""
    return handleChatbot()


@vehicles_bp.route("/chatbot/status", methods=["GET"])
def chatbot_status():
    """Public: check if chatbot is enabled."""
    return handleChatbotStatus()


# ── Admin: Vehicle CRUD ──────────────────────────────────────────────────

@vehicles_bp.route("/create", methods=["POST"])
@logged_in_required
@role_required("admin")
def add_vehicle():
    """Add a new vehicle to the inventory."""
    return createVehicle()

@vehicles_bp.route("/update/<int:id>", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update_vehicle(id):
    """Update vehicle details."""
    return updateVehicleHandler(id)

@vehicles_bp.route("/delete/<int:id>", methods=["DELETE"])
@logged_in_required
@role_required("admin")
def delete_vehicle(id):
    """Delete (or deactivate) a vehicle."""
    return deleteVehicleHandler(id)

# ── Admin: Vehicle photos ────────────────────────────────────────────────

@vehicles_bp.route("/add/photo", methods=["POST"])
@logged_in_required
@role_required("admin")
def createPhoto():
    """Upload a photo for a vehicle."""
    return addPhoto()

@vehicles_bp.route("/photo/<int:photo_id>", methods=["PUT"])
@logged_in_required
@role_required("admin")
def editVehiclePhoto(photo_id):
    """Update a vehicle photo's URL, sort order, or upload time."""
    return updateVehiclePhoto(photo_id)

@vehicles_bp.route("/delete/photo/<int:photo_id>", methods=["DELETE"])
@logged_in_required
@role_required("admin")
def deletePhoto(photo_id):
    """Remove a photo from a vehicle."""
    return removePhoto(photo_id)

# ── Admin: Status & stock ────────────────────────────────────────────────

@vehicles_bp.route("/update/status/<int:vehicle_id>", methods=["PUT"])
@logged_in_required
@role_required("admin")
def changeStatus(vehicle_id):
    """Manually update a vehicle's status (available/reserved/sold, etc.)."""
    return updateStatus(vehicle_id)

@vehicles_bp.route("/low_stock", methods=["GET"])
@logged_in_required
@role_required("admin")
def get_stocks():
    """List vehicles below a given stock threshold (?threshold=N)."""
    threshold = request.args.get("threshold")
    return indexLowStocks(threshold)
