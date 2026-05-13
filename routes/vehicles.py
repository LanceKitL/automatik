from flask import Blueprint, request, session, jsonify
from validators.middleware import role_required 
from conn import run_query
from controllers.vehicleController import (
    createVehicle,
    updateVehicleHandler,
    deleteVehicleHandler,
    updateVehiclePhoto,
    searchVehicle
)

vehicles_bp = Blueprint('vehicles', __name__)

# can be accessed by everyone
@vehicles_bp.route("/")
def vehicles():
    res = run_query("SELECT * FROM vehicles", fetch="all")
    return jsonify({"data": res}), 200


@vehicles_bp.route("/", methods=["POST"])
@role_required("admin")
def add_vehicle(): return createVehicle()

@vehicles_bp.route("/<int:id>")
def get_vehicles(id):
    car = run_query("SELECT * FROM vehicles WHERE vehicle_id = %s", (id, ), fetch="one")
    
    if not car:
        return jsonify({"message": "no vehicle found."}), 400    
    
    return jsonify({"data": car}), 200
    
# UPDATING VEHICLE
@vehicles_bp.route("/<int:id>", methods=["PUT"])
@role_required("admin")
def update_vehicle(id): return updateVehicleHandler(id)

# DELETING VEHICLE
@vehicles_bp.route("/<int:id>", methods=["DELETE"])
@role_required("admin")
def delete_vehicle(id): return deleteVehicleHandler(id)

@vehicles_bp.route("/<int:id>/photos")
def get_vehicle_photo(id):
    res = run_query("SELECT * FROM vehicle_photos WHERE vehicle_id = %s",(id, ), fetch="all")
    
    if not res: 
        return jsonify({"message": f"vehicle {id} does not exists."}), 400

    return jsonify({"data": res}), 200

@vehicles_bp.route("/<int:id>/photos", methods=["POST"])
@role_required("admin")
def update_vehicle_photo(id): return updateVehiclePhoto(id)


@vehicles_bp.route("/search")
def search():
    value = request.args.get("param")
    return searchVehicle(value)
    