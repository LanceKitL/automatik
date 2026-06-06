"""
Supplier controller — CRUD for the suppliers table.

Each supplier can be linked to vehicles and supplies.
All write operations check existence first, and delete
guards against orphaned vehicle references.
"""

from datetime import datetime
from flask import request, jsonify
from conn import run_query
import re


# ── Validation helpers ────────────────────────────────────────────────────

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _is_valid_email(email):
    """Return True if *email* looks like a rough valid email address."""
    return bool(_EMAIL_RE.match(email)) if email else True


# ── Public endpoints ───────────────────────────────────────────────────────

def searchSupplier(params):
    """Search suppliers by company_name, contact_name, email, or phone."""
    if not params:
        return jsonify({"message": "search parameter is required."}), 400

def getSupplier(is_active):
    """
    List suppliers, optionally filtered by is_active status.
    Query param: ?is_active=0|1 (optional)
    Returns:    JSON { data: [...] }
    Status:     200 (empty list returns 200 with [])
    """
    if is_active is None:
        suppliers = run_query(
            """
            SELECT s.*,
                   (SELECT COUNT(*) FROM vehicles v WHERE v.supplier_id = s.supplier_id) AS total_vehicles
            FROM suppliers s
            ORDER BY s.company_name ASC
            """,
            fetch="all",
        )
    else:
        suppliers = run_query(
            """
            SELECT s.*,
                   (SELECT COUNT(*) FROM vehicles v WHERE v.supplier_id = s.supplier_id) AS total_vehicles
            FROM suppliers s
            WHERE s.is_active = %s
            ORDER BY s.company_name ASC
            """,
            (is_active,),
            fetch="all",
        )

    return jsonify({"data": suppliers}), 200


def getDetailsSupplier(supplier_id):
    """
    Get single supplier detail with vehicle count and supplies list.
    Path param: supplier_id
    Returns:    JSON { data: { ... } }
    Status:     200, 404
    """
    supplier = run_query(
        """
        SELECT s.*,
               (SELECT COUNT(*) FROM vehicles v WHERE v.supplier_id = s.supplier_id) AS total_vehicles
        FROM suppliers s
        WHERE s.supplier_id = %s
        """,
        (supplier_id,),
        fetch="one",
    )

    if not supplier:
        return jsonify({"message": "Supplier not found."}), 404

    supplies = run_query(
        """
        SELECT supply_id, part_name, part_number, unit_cost, stock_qty, reorder_level
        FROM supplies
        WHERE supplier_id = %s
        ORDER BY part_name ASC
        """,
        (supplier_id,),
        fetch="all",
    )

    supplier["supplies"] = supplies
    return jsonify({"data": supplier}), 200


def createSupplier():
    """
    Create a new supplier.
    Body:       company_name (required), contact_name, contact_email, contact_phone, address, is_active
    Returns:    JSON { message, supplier_id }
    Status:     201, 400, 422
    """
    data = request.get_json(silent=True) or {}
    company_name = data.get("company_name")
    contact_name = data.get("contact_name")
    contact_email = data.get("contact_email")
    contact_phone = data.get("contact_phone")
    address = data.get("address")
    is_active = data.get("is_active", 1)  # default active
    created_at = datetime.now()

    # ── Required field ────────────────────────────────────────────────
    if not company_name:
        return jsonify({"message": "company_name is required."}), 400

    # ── Email validation ──────────────────────────────────────────────
    if contact_email and not _is_valid_email(contact_email):
        return jsonify({"message": "Invalid email format."}), 422

    # ── Insert ────────────────────────────────────────────────────────
    supplier_id = run_query(
        """
        INSERT INTO suppliers
            (company_name, contact_name, contact_email, contact_phone,
             address, is_active, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (company_name, contact_name, contact_email,
         contact_phone, address, is_active, created_at),
    )

    return jsonify({
        "message": "Supplier added successfully.",
        "supplier_id": supplier_id,
    }), 201


def updateSupplier(id):
    """Update an existing supplier.  Returns 404 if not found."""
    data = request.get_json(silent=True) or {}

    # ── Existence check ───────────────────────────────────────────────
    existing = run_query(
        "SELECT * FROM suppliers WHERE supplier_id = %s",
        (id,),
        fetch="one",
    )
    if not existing:
        return jsonify({"message": "Supplier not found."}), 404

    # ── Email validation (if provided) ────────────────────────────────
    contact_email = data.get("contact_email")
    if contact_email is not None and not _is_valid_email(contact_email):
        return jsonify({"message": "Invalid email format."}), 422

    # ── Dynamic UPDATE ────────────────────────────────────────────────
    fields = {
        "company_name": data.get("company_name"),
        "contact_name": data.get("contact_name"),
        "contact_email": contact_email,
        "contact_phone": data.get("contact_phone"),
        "address": data.get("address"),
        "is_active": data.get("is_active"),
    }

    update_clauses = []
    params = []
    for col, val in fields.items():
        if val is not None:
            update_clauses.append(f"{col} = %s")
            params.append(val)

    if not update_clauses:
        return jsonify({"message": "No fields to update."}), 400

    params.append(id)
    run_query(
        f"UPDATE suppliers SET {', '.join(update_clauses)} WHERE supplier_id = %s",
        params,
    )

    return jsonify({"message": "Supplier updated successfully."}), 200


def deleteSupplier(id):
    """
    Delete a supplier.  Guards against deleting a supplier that still has
    vehicles referencing it (409).
    """
    # ── Existence check ───────────────────────────────────────────────
    existing = run_query(
        "SELECT * FROM suppliers WHERE supplier_id = %s",
        (id,),
        fetch="one",
    )
    if not existing:
        return jsonify({"message": "Supplier not found."}), 404

    # ── Check vehicle references ──────────────────────────────────────
    refs = run_query(
        "SELECT COUNT(*) AS total FROM vehicles WHERE supplier_id = %s",
        (id,),
        fetch="one",
    )
    if refs and refs["total"] > 0:
        return jsonify({
            "message": "Cannot delete supplier; it has vehicles assigned."
        }), 409

    # ── Delete ────────────────────────────────────────────────────────
    run_query("DELETE FROM suppliers WHERE supplier_id = %s", (id,))
    return jsonify({"message": "Supplier deleted successfully."}), 204
