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
    createSupplier,
    get_supplier_detail,
    updateSupplier,
    deleteSupplier,
)

supplier_bp = Blueprint('suppliers', __name__)

# ── List ─────────────────────────────────────────────────────────────────

@supplier_bp.route('/')
@logged_in_required
def suppliers():
    """Return all suppliers."""
    res = run_query("SELECT * FROM suppliers", fetch="all")
    return jsonify({"data": res}), 200

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
def get_suppliers(id):
    """Get a single supplier by ID, including supplies list."""
    return get_supplier_detail(id)

# ── Update (admin) ───────────────────────────────────────────────────────

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
