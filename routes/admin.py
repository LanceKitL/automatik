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
from controllers.serviceController import (
    listAllBookingsHandler,
    updateBookingStatusHandler,
    listAllWarrantyClaimsHandler,
    getWarrantyClaimDetailHandler,
    updateWarrantyStatusHandler,
)

admin_bp = Blueprint('admin', __name__)

#users
@admin_bp.route('/users')
@logged_in_required
@role_required("admin")
def index(): return get_user()

@admin_bp.route("/users/<int:user_id>")
@logged_in_required
@role_required("admin")
def show(user_id): return get_user_with(user_id)

@admin_bp.route("/users/<int:user_id>/profile")
@logged_in_required
@role_required("admin")
def show_profile(user_id): return get_user_profile_with(user_id)

# updating users.
@admin_bp.route("/users/update/<int:user_id>", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update_user(user_id): return update_user_with(user_id)

@admin_bp.route("/users/<int:user_id>/delete", methods=["DELETE"])
@logged_in_required
@role_required("admin")
def delete_user(user_id): return delete_user_with(user_id)

# agents
@admin_bp.route("/agents")
@logged_in_required
@role_required("admin")
def index_agents(): return get_agents()

@admin_bp.route("/agent/update/<int:agent_id>", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update_agent(agent_id): return update_commission_rate(agent_id)


# customer
@admin_bp.route("/customer")
@logged_in_required
@role_required("admin")
def index_customers(): return get_customers()

@admin_bp.route("/customer/<int:customer_id>")
@logged_in_required
@role_required("admin")
def show_customer(customer_id): return get_customer_with(customer_id)

@admin_bp.route("/customer/<int:customer_id>/update", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update_customer(customer_id): return update_customer_with(customer_id)


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


@admin_bp.route("/service/bookings/<int:booking_id>/complete", methods=["PUT"])
@logged_in_required
@role_required("admin")
def complete_booking(booking_id):
    return updateBookingStatusHandler(booking_id, "completed")


# --- Admin: Warranty Claims ---

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