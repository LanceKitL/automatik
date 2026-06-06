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

    res = run_query(
        """
        SELECT * FROM suppliers
        WHERE company_name LIKE %s
           OR contact_name LIKE %s
           OR contact_email LIKE %s
           OR contact_phone LIKE %s
        """,
        (f"%{params}%", f"%{params}%", f"%{params}%", f"%{params}%"),
        fetch="all"
    )

    if not res:
        return jsonify({"message": "Supplier not found"}), 404

    return jsonify({"message": res})


def get_supplier_detail(supplier_id):
    """
    Return a single supplier plus its list of supplies.

    Called from the GET /admin/suppliers/<id> route.
    """
    supplier = run_query(
        "SELECT * FROM suppliers WHERE supplier_id = %s",
        (supplier_id,),
        fetch="one",
    )
    if not supplier:
        return jsonify({"message": "Supplier not found"}), 404

    supplies = run_query(
        "SELECT * FROM supplies WHERE supplier_id = %s",
        (supplier_id,),
        fetch="all",
    )

    supplier["supplies"] = supplies or []
    return jsonify({"data": supplier}), 200


def createSupplier():
    """Create a new supplier with input validation."""
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
