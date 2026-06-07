"""
Supplier routes — manage parts/service vendors.

All endpoints require admin login.
Blueprint registered at /admin/suppliers in app.py.

GET    /                        — list suppliers (?is_active=0|1)
GET    /<id>                    — supplier detail + vehicle count + supplies
POST   /                        — create supplier (admin)
PUT    /<id>                    — update supplier (admin)
DELETE /<id>                    — delete supplier (admin, only if no linked vehicles)
"""

from flask import Blueprint, jsonify, request
from validators.middleware import role_required, logged_in_required
from controllers.supplierController import (
    getSupplier,
    getDetailsSupplier,
    createSupplier,
    updateSupplier,
    deleteSupplier,
)

supplier_bp = Blueprint("suppliers", __name__)


@supplier_bp.route("/", methods=["GET"])
@logged_in_required
@role_required("admin")
def list_suppliers():
    """Return all suppliers, optional ?is_active=0|1 filter."""
    is_active = request.args.get("is_active")
    return getSupplier(is_active)


@supplier_bp.route("/<int:supplier_id>", methods=["GET"])
@logged_in_required
@role_required("admin")
def details_supplier(supplier_id):
    """Return single supplier detail with vehicle count and supplies list."""
    return getDetailsSupplier(supplier_id)


@supplier_bp.route("/", methods=["POST"])
@logged_in_required
@role_required("admin")
def add_supplier():
    """Create a new supplier."""
    return createSupplier()


@supplier_bp.route("/<int:supplier_id>", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update_supplier(supplier_id):
    """Update a supplier's contact info or is_active status."""
    return updateSupplier(supplier_id)


@supplier_bp.route("/<int:supplier_id>", methods=["DELETE"])
@logged_in_required
@role_required("admin")
def delete_supplier(supplier_id):
    """Delete a supplier (only if no vehicles reference it)."""
    return deleteSupplier(supplier_id)
