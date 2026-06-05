"""
Profile routes — read and update the current user's own profile.

GET  /profile/       — get own profile
PUT  /profile/update — update own profile
"""

from validators.middleware import logged_in_required
from flask import Blueprint
from controllers.profileController import (
    get_profile,
    update_profile
)

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/")
@logged_in_required
def index():
    """Get the current user's profile (user_profile + user basics)."""
    return get_profile()

@profile_bp.route("/update", methods=["PUT"])
@logged_in_required
def update():
    """Update the current user's profile fields."""
    return update_profile()
