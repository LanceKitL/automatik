from flask import Blueprint, request, session, jsonify
from validators.middleware import role_required 
from controllers.vehicleController import (
    createVehicle,
    updateVehicleHandler,
    deleteVehicleHandler,
    updateVehiclePhoto,
    searchVehicle,
    getVehicles,
    showVehicle,
    showVehiclePhotos
)

vehicles_bp = Blueprint('vehicles', __name__)

# can be accessed by everyone
@vehicles_bp.route("/")
def vehicles(): return getVehicles()

@vehicles_bp.route("/", methods=["POST"])
@role_required("admin")
def add_vehicle(): return createVehicle()

@vehicles_bp.route("/<int:id>")
def get_vehicles(id): return showVehicle(id)
    
# UPDATING VEHICLE
@vehicles_bp.route("/<int:id>", methods=["PUT"])
@role_required("admin")
def update_vehicle(id): return updateVehicleHandler(id)

# DELETING VEHICLE
@vehicles_bp.route("/<int:id>", methods=["DELETE"])
@role_required("admin")
def delete_vehicle(id): return deleteVehicleHandler(id)

@vehicles_bp.route("/<int:id>/photos")
def get_vehicle_photo(id): return showVehiclePhotos(id)


@vehicles_bp.route("/<int:id>/photos", methods=["POST"])
@role_required("admin")
def update_vehicle_photo(id): return updateVehiclePhoto(id)

@vehicles_bp.route("/search")
def search():
    value = request.args.get("param")
    return searchVehicle(value)
    