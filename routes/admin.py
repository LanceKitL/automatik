"""
Admin routes — user, agent, and customer management.

All endpoints require admin role.
"""

from flask import Blueprint
from validators.middleware import role_required, logged_in_required
from controllers.adminController import (
    get_user,
    get_user_with,
    get_user_profile_with,
    update_user_with,
    delete_user_with,
    get_agents,
    update_commission_rate,
    get_customers,
    get_customer_with,
    update_customer_with
)

admin_bp = Blueprint('admin', __name__)

# ── Users ────────────────────────────────────────────────────────────────

@admin_bp.route('/users')
@logged_in_required
@role_required("admin")
def index():
    """List all users (paginated)."""
    return get_user()

@admin_bp.route("/users/<int:user_id>")
@logged_in_required
@role_required("admin")
def show(user_id):
    """Get a single user by ID."""
    return get_user_with(user_id)

@admin_bp.route("/users/<int:user_id>/profile")
@logged_in_required
@role_required("admin")
def show_profile(user_id):
    """Get the user_profile row for a given user."""
    return get_user_profile_with(user_id)

@admin_bp.route("/users/update/<int:user_id>", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update_user(user_id):
    """Update user account fields (username, email, role, etc.)."""
    return update_user_with(user_id)

@admin_bp.route("/users/<int:user_id>/delete", methods=["DELETE"])
@logged_in_required
@role_required("admin")
def delete_user(user_id):
    """Soft-delete or deactivate a user."""
    return delete_user_with(user_id)

# ── Agents ───────────────────────────────────────────────────────────────

@admin_bp.route("/agents")
@logged_in_required
@role_required("admin")
def index_agents():
    """List all users with role='agent'."""
    return get_agents()

@admin_bp.route("/agent/update/<int:agent_id>", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update_agent(agent_id):
    """Update an agent's default commission rate."""
    return update_commission_rate(agent_id)

# ── Customers ────────────────────────────────────────────────────────────

@admin_bp.route("/customer")
@logged_in_required
@role_required("admin")
def index_customers():
    """List all users with role='customer'."""
    return get_customers()

@admin_bp.route("/customer/<int:customer_id>")
@logged_in_required
@role_required("admin")
def show_customer(customer_id):
    """Get a single customer with their details."""
    return get_customer_with(customer_id)

@admin_bp.route("/customer/<int:customer_id>/update", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update_customer(customer_id):
    """Update customer details record."""
    return update_customer_with(customer_id)
