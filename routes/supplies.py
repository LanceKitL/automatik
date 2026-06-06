"""
Supplies routes — manage parts/supplies inventory.

All endpoints require admin login.
Blueprint registered at /admin/supplies in app.py.

GET    /                        — list supplies (?low_stock=1)
GET    /<id>                    — supply detail with supplier info
POST   /                        — create supply (admin)
PUT    /<id>                    — update supply (admin)
DELETE /<id>                    — delete supply (admin)
GET    /low-stock               — list supplies below reorder level
"""

from flask import Blueprint, request
from validators.middleware import role_required, logged_in_required
from controllers.suppliesController import (
    getSupplies,
    getSuppliesDetail,
    createSupplies,
    updateSupplies,
    deleteSupplies,
    getLowStockSupplies,
)

supplies_bp = Blueprint("supplies", __name__)


@supplies_bp.route("/", methods=["GET"])
@logged_in_required
@role_required("admin")
def list_supplies():
    """List all supplies with supplier details. Optional ?low_stock=1 filter."""
    return getSupplies()


@supplies_bp.route("/<int:supply_id>", methods=["GET"])
@logged_in_required
@role_required("admin")
def get_supply_detail(supply_id):
    """Get single supply detail with supplier info."""
    return getSuppliesDetail(supply_id)


@supplies_bp.route("/", methods=["POST"])
@logged_in_required
@role_required("admin")
def add_supply():
    """Create a new supply record."""
    return createSupplies()


@supplies_bp.route("/<int:supply_id>", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update_supply(supply_id):
    """Update a supply record."""
    return updateSupplies(supply_id)


@supplies_bp.route("/<int:supply_id>", methods=["DELETE"])
@logged_in_required
@role_required("admin")
def delete_supply(supply_id):
    """Delete a supply (only if no active service bookings reference it)."""
    return deleteSupplies(supply_id)


@supplies_bp.route("/low-stock", methods=["GET"])
@logged_in_required
@role_required("admin")
def low_stock_supplies():
    """List supplies where stock_qty <= reorder_level, with supplier contact info."""
    return getLowStockSupplies()
