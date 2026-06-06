"""
Supplies routes — manage inventory parts / supplies.

All endpoints require login; write operations require admin role.

Routes are registered at /admin/supplies (in app.py):
    GET    /admin/supplies/           — list all supplies (optional ?low_stock=1)
    POST   /admin/supplies/           — create a supply (admin)
    GET    /admin/supplies/<id>       — get one supply
    PUT    /admin/supplies/<id>       — update a supply (admin)
    DELETE /admin/supplies/<id>       — delete a supply (admin)
    GET    /admin/supplies/low-stock  — list low-stock supplies (convenience)
"""

from flask import Blueprint
from validators.middleware import role_required, logged_in_required
from controllers.suppliesController import (
    list_supplies,
    get_supply,
    create_supply,
    update_supply,
    delete_supply,
    low_stock_supplies,
)

supplies_bp = Blueprint("supplies", __name__)

# ── List (with optional low_stock filter) ─────────────────────────────────

@supplies_bp.route("/", methods=["GET"])
@logged_in_required
def supplies_list():
    """Return all supplies, optionally filtered to low-stock items."""
    return list_supplies()


# ── Create (admin) ────────────────────────────────────────────────────────

@supplies_bp.route("/", methods=["POST"])
@logged_in_required
@role_required("admin")
def supplies_create():
    """Create a new supply record."""
    return create_supply()


# ── Get single ────────────────────────────────────────────────────────────

@supplies_bp.route("/<int:id>", methods=["GET"])
@logged_in_required
def supplies_detail(id):
    """Return a single supply by ID."""
    return get_supply(id)


# ── Update (admin) ────────────────────────────────────────────────────────

@supplies_bp.route("/<int:id>", methods=["PUT"])
@logged_in_required
@role_required("admin")
def supplies_update(id):
    """Update a supply record."""
    return update_supply(id)


# ── Delete (admin) ────────────────────────────────────────────────────────

@supplies_bp.route("/<int:id>", methods=["DELETE"])
@logged_in_required
@role_required("admin")
def supplies_delete(id):
    """Delete a supply record (checks for active bookings first)."""
    return delete_supply(id)


# ── Low-stock convenience ─────────────────────────────────────────────────

@supplies_bp.route("/low-stock", methods=["GET"])
@logged_in_required
def supplies_low_stock():
    """Return supplies where stock_qty < reorder_level, sorted by urgency."""
    return low_stock_supplies()
