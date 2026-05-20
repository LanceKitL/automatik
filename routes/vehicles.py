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
    removePhoto,
    updateStatus,
    indexLowStocks
)

vehicles_bp = Blueprint('vehicles', __name__)

# can be accessed by everyone
@vehicles_bp.route("/") # /vehicle
def vehicles(): return getVehicles()

@vehicles_bp.route("/search")
def search():
    # filter by brand, model, fuel_type, status, price_min, price_max.
    # join first the first photo of the vehicle, then filter by the query parameters.
    params = {
        "brand": request.args.get("brand"),
        "model": request.args.get("model"),
        "fuel_type": request.args.get("fuel_type"),
        "status": request.args.get("status"),
        "price_min": request.args.get("price_min"),
        "price_max": request.args.get("price_max")
    }
    return searchVehicle(params)

@vehicles_bp.route("/<int:id>") # /vehicle/<id>
def get_vehicles(id): return showVehicle(id)

# admin only routes
@vehicles_bp.route("/create", methods=["POST"]) 
@logged_in_required
@role_required("admin")
def add_vehicle(): return createVehicle()
    
@vehicles_bp.route("/update/<int:id>", methods=["PUT"]) # update
@logged_in_required
@role_required("admin")
def update_vehicle(id): return updateVehicleHandler(id)

@vehicles_bp.route("/delete/<int:id>", methods=["DELETE"]) # delete
@logged_in_required
@role_required("admin")
def delete_vehicle(id): return deleteVehicleHandler(id)

# for vehicle photos
@vehicles_bp.route("/add/photo", methods=["POST"])
@logged_in_required
@role_required("admin")
def createPhoto(): return addPhoto()

@vehicles_bp.route("/delete/<int:photo_id>/photo", methods=["DELETE"])
@logged_in_required
@role_required("admin")
def deletePhoto(photo_id): return removePhoto(photo_id)

@vehicles_bp.route("/update/<int:vehicle_id>/status", methods=["PUT"])
@logged_in_required
@role_required("admin")
def changeStatus(vehicle_id):return updateStatus(vehicle_id)

@vehicles_bp.route("/low_stock", methods=["GET"])
@logged_in_required
@role_required("admin")
def get_stocks():
    threshold = request.args.get("threshold")
    return indexLowStocks(threshold)
