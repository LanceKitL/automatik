from flask import Blueprint, request, session, jsonify
from validators.middleware import role_required 
from conn import run_query
from controllers.supplierController import(
    createSupplier,
    searchSupplier,
    updateSupplier,
    deleteSupplier,
)

supplier_bp = Blueprint('suppliers', __name__)

#List all suppliers
@supplier_bp.route('/')
def suppliers ():
    res = run_query("SELECT * FROM suppliers", fetch= "all")
    return jsonify ({"data": res}), 200

#Create Suppliers
@supplier_bp.route('/', methods = ['POST'])
@role_required('admin')
def add_suppliers(): return createSupplier()

#Get suppliers
@supplier_bp.route('/<int:id>')
def get_suppliers(id):
     res = run_query("SELECT * FROM suppliers WHERE supplier_id = %s", (id,),fetch="one")

     if not res:
          return jsonify ({"message": "Supplier not found"}), 400
     
     return jsonify ({"data": res}), 200

#Update Suppliers
@supplier_bp.route('/<int:id>', methods = ['PUT'])
@role_required('admin')
def update_suppliers(id): return updateSupplier(id)

#Delete Suppliers
@supplier_bp.route('/<int:id>', methods = ['DELETE'])
@role_required('admin')
def delete_suppliers(id): return deleteSupplier(id)