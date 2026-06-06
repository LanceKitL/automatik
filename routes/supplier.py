<<<<<<< HEAD
"""
Supplier routes — manage parts/service vendors.

All endpoints require login; write operations require admin role.

GET    /supplier/        — list all suppliers
POST   /supplier/        — create a supplier (admin)
GET    /supplier/<id>    — get one supplier
PUT    /supplier/<id>    — update a supplier (admin)
DELETE /supplier/<id>    — delete a supplier (admin)
"""

from flask import Blueprint, jsonify
from validators.middleware import role_required, logged_in_required
from conn import run_query
from controllers.supplierController import (
=======
from flask import Blueprint, jsonify, request
from validators.middleware import role_required, logged_in_required
from conn import run_query
from controllers.supplierController import(
    getDetailsSupplier,
    getSupplier,
    searchSupplier,
>>>>>>> 37d1bda (API for suppliers and supplies DONE)
    createSupplier,
    updateSupplier,
    deleteSupplier,
)

supplier_bp = Blueprint('suppliers', __name__)

<<<<<<< HEAD
# ── List ─────────────────────────────────────────────────────────────────

@supplier_bp.route('/')
@logged_in_required
def suppliers():
    """Return all suppliers."""
    res = run_query("SELECT * FROM suppliers", fetch="all")
    return jsonify({"data": res}), 200
=======
#List all suppliers
@supplier_bp.route('/', methods = ['GET'])
@logged_in_required
@role_required('admin')
def suppliers():
    is_active = request.args.get("is_active")
    return getSupplier(is_active)

#Supplier details
@supplier_bp.route('/<int:supplier_id>', methods = ['GET'])
@logged_in_required
@role_required('admin')
def details_supplier(supplier_id):
    return getDetailsSupplier(supplier_id)
>>>>>>> 37d1bda (API for suppliers and supplies DONE)

# ── Create (admin) ───────────────────────────────────────────────────────

@supplier_bp.route('/', methods=['POST'])
@logged_in_required
@role_required('admin')
def add_suppliers():
    """Add a new supplier."""
    return createSupplier()

# ── Get single ───────────────────────────────────────────────────────────

@supplier_bp.route('/<int:id>')
@logged_in_required
<<<<<<< HEAD
def get_suppliers(id):
    """Get a single supplier by ID."""
    res = run_query("SELECT * FROM suppliers WHERE supplier_id = %s", (id,), fetch="one")
    if not res:
        return jsonify({"message": "Supplier not found"}), 404
    return jsonify({"data": res}), 200

# ── Update (admin) ───────────────────────────────────────────────────────
=======
def search_supplier(id):
    params = {
        "supplier_id": id,
        "company_name": request.args.get("company_name"),
        "contact_name": request.args.get("contact_name"),
        "contact_email": request.args.get("contact_email"),
        "contact_phone": request.args.get("contact_phone"),
        "address": request.args.get("address"),
        "is_active": request.args.get("is_active")
    }
    return searchSupplier(params)
>>>>>>> 37d1bda (API for suppliers and supplies DONE)

@supplier_bp.route('/<int:id>', methods=['PUT'])
@logged_in_required
@role_required('admin')
def update_suppliers(id):
    """Update a supplier's details."""
    return updateSupplier(id)

# ── Delete (admin) ───────────────────────────────────────────────────────

@supplier_bp.route('/<int:id>', methods=['DELETE'])
@logged_in_required
@role_required('admin')
def delete_suppliers(id):
    """Delete a supplier."""
    return deleteSupplier(id)
