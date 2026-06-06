"""
Settings routes — manage system-wide configuration key-value pairs.

All endpoints require login; write operations also require the admin role.

Routes are registered at /admin (in app.py), producing:
    GET    /admin/settings          — list all settings (cached)
    GET    /admin/settings/<key>    — get a single setting
    PUT    /admin/settings/<key>    — update a setting value (admin)
    POST   /admin/settings          — add a new setting key (admin)
"""

from flask import Blueprint
from validators.middleware import role_required, logged_in_required
from controllers.settingsController import (
    get_all_settings,
    get_setting,
    update_setting,
    add_setting,
)

settings_bp = Blueprint("settings", __name__)

# ── List all ───────────────────────────────────────────────────────────────

@settings_bp.route("/settings", methods=["GET"])
@logged_in_required
@role_required("admin")
def list_settings():
    """
    Return every system setting as a dict keyed by setting_key.
    Results are cached (default TTL 300 s) to avoid repeated DB queries.
    """
    return get_all_settings()


# ── Get single ─────────────────────────────────────────────────────────────

@settings_bp.route("/settings/<key>", methods=["GET"])
@logged_in_required
@role_required("admin")
def get_setting_by_key(key):
    """
    Return a single setting identified by its setting_key.
    404 if the key does not exist in system_settings.
    """
    return get_setting(key)


# ── Update ─────────────────────────────────────────────────────────────────

@settings_bp.route("/settings/<key>", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update_setting_value(key):
    """
    Update setting_value for an existing key.
    Logs the change in audit_logs (old → new).
    Invalidates the settings cache so subsequent reads are fresh.
    """
    return update_setting(key)


# ── Create ─────────────────────────────────────────────────────────────────

@settings_bp.route("/settings", methods=["POST"])
@logged_in_required
@role_required("admin")
def add_new_setting():
    """
    Insert a new setting key / value pair.
    The key must be unique (409 on duplicate).
    Invalidates the settings cache.
    """
    return add_setting()
