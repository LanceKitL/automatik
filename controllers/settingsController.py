"""
Settings controller — CRUD for system_settings table with caching.

Uses Flask-Caching (cache object from utils.cache) to reduce DB reads.
Cache key: "settings:all" stores the full dict of all settings.
On any write (PUT/POST), the cache is invalidated so the next read
refetches from the database.
"""

from flask import request, jsonify, session
from conn import run_query
from utils.log import audit_log
from utils.cache import cache

# ── Cache key ──────────────────────────────────────────────────────────────
# Stores the full mapping {setting_key: {setting_value, description, ...}}
_SETTINGS_CACHE_KEY = "settings:all"


# ── Helpers ────────────────────────────────────────────────────────────────

def _invalidate_settings_cache():
    """
    Delete the cached settings dict so the next read hits the database.

    Must be called after every INSERT / UPDATE on system_settings.
    Uses the module-level cache singleton (from utils.cache).
    """
    cache.delete(_SETTINGS_CACHE_KEY)


def _build_settings_dict(rows):
    """
    Convert a list of system_settings rows into a dict keyed by setting_key.

    Each value contains the full row so clients can inspect metadata
    (setting_id, description, updated_at, etc.).
    """
    return {row["setting_key"]: row for row in rows}


# ── Public endpoints ───────────────────────────────────────────────────────

def get_all_settings():
    """
    GET /admin/settings

    Return all system settings as a dict keyed by setting_key.
    Results are cached under _SETTINGS_CACHE_KEY to avoid a DB round-trip
    on every request.  Cache is invalidated whenever a setting is created
    or updated.

    Returns:
        200 with JSON body: {"data": {key: row, ...}}
    """
    # 1. Try cache first
    cached = cache.get(_SETTINGS_CACHE_KEY)
    if cached is not None:
        return jsonify({"data": cached}), 200

    # 2. Cache miss — query the database
    rows = run_query(
        """
        SELECT
            s.setting_id,
            s.setting_key,
            s.setting_value,
            s.description,
            s.updated_by,
            s.updated_at
        FROM system_settings s
        ORDER BY s.setting_key ASC
        """,
        fetch="all",
    )

    # 3. Build dict and store in cache
    settings_dict = _build_settings_dict(rows) if rows else {}
    cache.set(_SETTINGS_CACHE_KEY, settings_dict)

    return jsonify({"data": settings_dict}), 200


def get_setting(key):
    """
    GET /admin/settings/<key>

    Return a single setting by its setting_key.

    Reads from the cached full dict when possible, falling back to a
    direct DB query if the cache is empty.

    Returns:
        200 with JSON body: {"data": row}
        404 if the key does not exist.
    """
    # 1. Try from cached dict first
    cached = cache.get(_SETTINGS_CACHE_KEY)
    if cached is not None and key in cached:
        return jsonify({"data": cached[key]}), 200

    # 2. Cache miss — query DB for this specific key
    row = run_query(
        """
        SELECT
            s.setting_id,
            s.setting_key,
            s.setting_value,
            s.description,
            s.updated_by,
            s.updated_at
        FROM system_settings s
        WHERE s.setting_key = %s
        """,
        (key,),
        fetch="one",
    )

    if not row:
        return jsonify({"message": f"Setting '{key}' not found."}), 404

    return jsonify({"data": row}), 200


def update_setting(key):
    """
    PUT /admin/settings/<key>

    Update the value of an existing setting.  Logs the change in audit_logs
    and invalidates the settings cache.

    Request body (JSON):
        {"setting_value": "new-value"}

    Validation:
        - setting_value must be present and non-empty (422)

    Returns:
        200 on success.
        400 if setting_value is missing or empty.
        404 if the key does not exist.
    """
    data = request.get_json(silent=True) or {}
    new_value = data.get("setting_value")

    # ── Validate input ─────────────────────────────────────────────────
    if not new_value or (isinstance(new_value, str) and new_value.strip() == ""):
        return jsonify({
            "message": "setting_value is required and must not be empty."
        }), 422

    # ── Check existence & fetch old value for audit log ────────────────
    row = run_query(
        "SELECT * FROM system_settings WHERE setting_key = %s",
        (key,),
        fetch="one",
    )
    if not row:
        return jsonify({"message": f"Setting '{key}' not found."}), 404

    old_value = row["setting_value"]
    # Extract the current user from the session (set by @logged_in_required)
    user_id = session.get("user")

    # ── Perform the UPDATE ─────────────────────────────────────────────
    updated = run_query(
        """
        UPDATE system_settings
        SET setting_value = %s,
            updated_by   = %s,
            updated_at   = NOW()
        WHERE setting_key = %s
        """,
        (new_value.strip(), user_id, key),
    )

    # ── Audit log (old → new) ──────────────────────────────────────────
    audit_log(
        id=user_id,
        action="PUT",
        tablename="system_settings",
        record_id=row["setting_id"],
        old_value=old_value,
        new_value=new_value.strip(),
    )

    # ── Invalidate cache so next read is fresh ─────────────────────────
    _invalidate_settings_cache()

    return jsonify({
        "message": f"Setting '{key}' updated successfully.",
        "previous_value": old_value,
        "new_value": new_value.strip(),
    }), 200


def add_setting():
    """
    POST /admin/settings

    Insert a new system setting.  The key must be unique.

    Request body (JSON):
        {
            "setting_key":   "my_new_key",
            "setting_value": "some-value",
            "description":   "Optional explanation"
        }

    Returns:
        201 with the new setting_id.
        400 if setting_key or setting_value is missing.
        409 if the key already exists.
    """
    data = request.get_json(silent=True) or {}
    setting_key = data.get("setting_key")
    setting_value = data.get("setting_value")
    description = data.get("description")

    # ── Validate required fields ───────────────────────────────────────
    if not setting_key or (isinstance(setting_key, str) and setting_key.strip() == ""):
        return jsonify({"message": "setting_key is required."}), 400

    if not setting_value or (isinstance(setting_value, str) and setting_value.strip() == ""):
        return jsonify({"message": "setting_value is required."}), 422

    setting_key = setting_key.strip()
    setting_value = setting_value.strip()

    # ── Check duplicate key ────────────────────────────────────────────
    existing = run_query(
        "SELECT setting_id FROM system_settings WHERE setting_key = %s",
        (setting_key,),
        fetch="one",
    )
    if existing:
        return jsonify({
            "message": f"Setting key '{setting_key}' already exists."
        }), 409

    user_id = session.get("user")

    # ── Insert the new row ─────────────────────────────────────────────
    new_id = run_query(
        """
        INSERT INTO system_settings
            (setting_key, setting_value, description, updated_by)
        VALUES (%s, %s, %s, %s)
        """,
        (setting_key, setting_value, description, user_id),
    )

    # ── Audit log ──────────────────────────────────────────────────────
    audit_log(
        id=user_id,
        action="POST",
        tablename="system_settings",
        record_id=new_id,
        new_value=setting_value,
    )

    # ── Invalidate cache ───────────────────────────────────────────────
    _invalidate_settings_cache()

    return jsonify({
        "message": "Setting added successfully.",
        "setting_id": new_id,
    }), 201


def get_setting_value(key, default=None):
    """
    Public read-only helper -- fetch a single setting value by key.

    Can be imported and called from any controller during a request
    (e.g. createSale).  Reads from the shared "settings:all" cache
    when possible, falling back to a direct DB query.

    Args:
        key:     The setting_key to look up.
        default: Value returned if the key does not exist.

    Returns:
        The setting_value string, or *default* if not found.
    """
    # 1. Try cache first
    cached = cache.get(_SETTINGS_CACHE_KEY)
    if cached is not None and key in cached:
        return cached[key]["setting_value"]

    # 2. Cache miss -- direct DB query
    row = run_query(
        "SELECT setting_value FROM system_settings WHERE setting_key = %s",
        (key,), fetch="one",
    )
    return row.get("setting_value", default) if row else default
