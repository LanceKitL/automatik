from flask import Blueprint, jsonify, request
from validators.middleware import role_required, logged_in_required
from conn import run_query
from controllers.suppliesController import (
    getLowStockSupplies,
    getSupplies,
    getSuppliesDetail,
    createSupplies,
    updateSupplies,
    deleteSupplies
)

supplies_bp = Blueprint('supplies', __name__)

#List all supplies with supplier details
@supplies_bp.route('/', methods = ['GET'])
def list_supplies():
    return getSupplies()

#Get supply details
@supplies_bp.route('/details', methods = ['GET'])
def get_supply_details():
    return getSuppliesDetail()

#Create supply
@supplies_bp.route('/', methods = ['POST'])
def add_supply():
    return createSupplies()

#Update supply
@supplies_bp.route('/<int:supply_id>', methods = ['PUT'])
def update_supply(supply_id):
    return updateSupplies(supply_id)

#Delete supply
@supplies_bp.route('/<int:supply_id>', methods = ['DELETE'])
def delete_supply(supply_id):
    return deleteSupplies(supply_id)

#Get supplies that are below reorder level
@supplies_bp.route('/low-stock', methods = ['GET'])
def low_stock_supplies():
    return getLowStockSupplies()