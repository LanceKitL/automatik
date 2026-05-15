from flask import Blueprint, jsonify
from validators.middleware import role_required, logged_in_required
from conn import run_query
from controllers.supplierController import(
    createSupplier,
    updateSupplier,
    deleteSupplier,
)

supplier_bp = Blueprint('suppliers', __name__)

#List all suppliers
@supplier_bp.route('/')
@logged_in_required
def suppliers ():
    res = run_query("SELECT * FROM suppliers", fetch= "all")
    return jsonify ({"data": res}), 200

#Create Suppliers
@supplier_bp.route('/', methods = ['POST'])
@logged_in_required
@role_required('admin')
def add_suppliers(): return createSupplier()

#Get suppliers
@supplier_bp.route('/<int:id>')
@logged_in_required
def get_suppliers(id):
     res = run_query("SELECT * FROM suppliers WHERE supplier_id = %s", (id,),fetch="one")

     if not res:
          return jsonify ({"message": "Supplier not found"}), 404
     
     return jsonify ({"data": res}), 200

#Update Suppliers
@supplier_bp.route('/<int:id>', methods = ['PUT'])
@logged_in_required
@role_required('admin')
def update_suppliers(id): return updateSupplier(id)

#Delete Suppliers
@supplier_bp.route('/<int:id>', methods = ['DELETE'])
@logged_in_required
@role_required('admin')
def delete_suppliers(id): return deleteSupplier(id)