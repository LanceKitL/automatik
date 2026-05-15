from validators.middleware import logged_in_required
from flask import Blueprint
from controllers.profileController import (
    get_profile,
    update_profile
)

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/")
@logged_in_required
def index(): return get_profile()

@profile_bp.route("/update", methods=["PUT"])
@logged_in_required
def update(): return update_profile()