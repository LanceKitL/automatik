"""
Admin routes — user, agent, and customer management.

All endpoints require admin role.
"""

from flask import Blueprint, request, jsonify
from validators.middleware import role_required, logged_in_required
from controllers.adminController import (
    adminDashboard,
    adminVehicles,
    adminInventory,
    uploadVehiclePhoto,
    adminNotifications,
    adminAuditLogs,
    get_user,
    get_user_with,
    get_user_profile_with,
    update_user_with,
    updateUserProfile,
    delete_user_with,
    createUser,
    get_agents,
    update_commission_rate,
    getAgentDetail,
    get_customers,
    get_customer_with,
    update_customer_with,
    getCustomerSalesHistory,
)
from controllers.serviceController import (
    listAllBookingsHandler,
    updateBookingStatusHandler,
    deleteBookingHandler,
    listAllWarrantyClaimsHandler,
    getWarrantyClaimDetailHandler,
    updateWarrantyStatusHandler,
)
from controllers.documentsController import getAllDocuments

admin_bp = Blueprint('admin', __name__)

# ── Dashboard ────────────────────────────────────────────────────────────

@admin_bp.route('/dashboard')
@logged_in_required
@role_required("admin")
def dashboard():
    """Aggregated stats for admin home."""
    return adminDashboard()

# ── Vehicles / Inventory ──────────────────────────────────────────────────

@admin_bp.route("/vehicles")
@logged_in_required
@role_required("admin")
def vehicles():
    """List all vehicles (admin view — all statuses)."""
    return adminVehicles()


@admin_bp.route("/inventory")
@logged_in_required
@role_required("admin")
def inventory():
    """Combined inventory data: vehicles (with photos), suppliers, supplies, low-stock."""
    return adminInventory()


@admin_bp.route("/inventory/photos", methods=["POST"])
@logged_in_required
@role_required("admin")
def upload_photo():
    """Upload a vehicle photo (multipart/form-data)."""
    return uploadVehiclePhoto()

# ── Notifications ────────────────────────────────────────────────────────

@admin_bp.route("/notifications")
@logged_in_required
@role_required("admin")
def notifications():
    """In-app notifications for the current admin."""
    return adminNotifications()

# ── Audit Logs ───────────────────────────────────────────────────────────

@admin_bp.route("/audit_logs")
@logged_in_required
@role_required("admin")
def audit_logs():
    """Audit log entries (ordered newest first)."""
    return adminAuditLogs()

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

@admin_bp.route("/users", methods=["POST"])
@logged_in_required
@role_required("admin")
def create_user():
    """Create a new user (admin/agent/customer)."""
    return createUser()

@admin_bp.route("/users/<int:user_id>/profile", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update_user_profile(user_id):
    """Update user_profile fields for a user."""
    return updateUserProfile(user_id)

@admin_bp.route("/users/<int:user_id>/delete", methods=["DELETE"])
@logged_in_required
@role_required("admin")
def delete_user(user_id):
    """Delete a user."""
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

@admin_bp.route("/agents/<int:agent_id>")
@logged_in_required
@role_required("admin")
def show_agent(agent_id):
    """Get agent details including total sales count."""
    return getAgentDetail(agent_id)

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

@admin_bp.route("/customer/<int:customer_id>/sales")
@logged_in_required
@role_required("admin")
def customer_sales_history(customer_id):
    """Get sales history for a customer."""
    return getCustomerSalesHistory(customer_id)


# --- Admin: Documents ---

@admin_bp.route("/service/documents")
@logged_in_required
@role_required("admin")
def admin_documents():
    """List all documents."""
    return getAllDocuments()

# --- Admin: Service Bookings ---

@admin_bp.route("/service/bookings")
@logged_in_required
@role_required("admin")
def index_bookings():
    return listAllBookingsHandler()


@admin_bp.route("/service/bookings/<int:booking_id>/confirm", methods=["PUT"])
@logged_in_required
@role_required("admin")
def confirm_booking(booking_id):
    return updateBookingStatusHandler(booking_id, "confirmed")


@admin_bp.route("/service/bookings/<int:booking_id>/status", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update_booking_status(booking_id):
    """Update booking status. Body: { status: "confirmed"|"completed"|"cancelled" }."""
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    if new_status not in ("confirmed", "completed", "cancelled"):
        return jsonify({"message": "status must be 'confirmed', 'completed', or 'cancelled'."}), 400
    return updateBookingStatusHandler(booking_id, new_status)


@admin_bp.route("/service/bookings/<int:booking_id>", methods=["DELETE"])
@logged_in_required
@role_required("admin")
def delete_booking(booking_id):
    """Hard-delete a service booking."""
    return deleteBookingHandler(booking_id)


@admin_bp.route("/service/bookings/<int:booking_id>/complete", methods=["PUT"])
@logged_in_required
@role_required("admin")
def complete_booking(booking_id):
    return updateBookingStatusHandler(booking_id, "completed")


# --- Admin: Warranty Claims ---

@admin_bp.route("/service/warranty")
@logged_in_required
@role_required("admin")
def index_warranty_alias():
    """Alias for /admin/warranty — list all warranty claims."""
    return listAllWarrantyClaimsHandler()

@admin_bp.route("/warranty")
@logged_in_required
@role_required("admin")
def index_warranty():
    return listAllWarrantyClaimsHandler()


@admin_bp.route("/warranty/<int:claim_id>")
@logged_in_required
@role_required("admin")
def show_warranty(claim_id):
    return getWarrantyClaimDetailHandler(claim_id)


@admin_bp.route("/warranty/<int:claim_id>/review", methods=["PUT"])
@logged_in_required
@role_required("admin")
def review_warranty(claim_id):
    return updateWarrantyStatusHandler(claim_id, "under_review")


@admin_bp.route("/warranty/<int:claim_id>/approve", methods=["PUT"])
@logged_in_required
@role_required("admin")
def approve_warranty(claim_id):
    return updateWarrantyStatusHandler(claim_id, "approved")


@admin_bp.route("/warranty/<int:claim_id>/reject", methods=["PUT"])
@logged_in_required
@role_required("admin")
def reject_warranty(claim_id):
    return updateWarrantyStatusHandler(claim_id, "rejected")


@admin_bp.route("/warranty/<int:claim_id>/resolve", methods=["PUT"])
@logged_in_required
@role_required("admin")
def resolve_warranty(claim_id):
    return updateWarrantyStatusHandler(claim_id, "resolved")
