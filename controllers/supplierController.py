from datetime import datetime
from flask import request, jsonify
from conn import run_query
import re


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
    is_active = data.get("is_active", 1)

    if not company_name or not company_name.strip():
        return jsonify({"message": "company_name is required."}), 400

    if contact_email:
        email_pattern = r"^[^@]+@[^@]+\.[^@]+$"
        if not re.match(email_pattern, contact_email):
            return jsonify({"message": "Invalid email format."}), 422

    supplier_id = run_query(
        """
        INSERT INTO suppliers (company_name, contact_name, contact_email, contact_phone, address, is_active, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            company_name.strip(),
            contact_name.strip() if contact_name else None,
            contact_email.strip() if contact_email else None,
            contact_phone.strip() if contact_phone else None,
            address.strip() if address else None,
            1 if is_active else 0,
            datetime.now(),
        ),
    )

    return jsonify({"message": "Supplier added successfully.", "supplier_id": supplier_id}), 201


def updateSupplier(supplier_id):
    """
    Update supplier contact info or is_active status.
    Path param: supplier_id
    Body:       company_name, contact_name, contact_email, contact_phone, address, is_active
    Returns:    JSON { message }
    Status:     200, 400, 404
    """
    existing = run_query(
        "SELECT supplier_id FROM suppliers WHERE supplier_id = %s",
        (supplier_id,),
        fetch="one",
    )

    if not existing:
        return jsonify({"message": "Supplier not found."}), 404

    data = request.get_json(silent=True) or {}

    fields = {
        "company_name": data.get("company_name"),
        "contact_name": data.get("contact_name"),
        "contact_email": data.get("contact_email"),
        "contact_phone": data.get("contact_phone"),
        "address": data.get("address"),
        "is_active": data.get("is_active"),
    }

    update_fields = []
    params = []

    for field_name, value in fields.items():
        if value is not None:
            if field_name == "is_active":
                value = 1 if value else 0
            update_fields.append(f"{field_name} = %s")
            params.append(value)

    if not update_fields:
        return jsonify({"message": "No fields to update."}), 400

    if data.get("contact_email"):
        email_pattern = r"^[^@]+@[^@]+\.[^@]+$"
        if not re.match(email_pattern, data["contact_email"]):
            return jsonify({"message": "Invalid email format."}), 422

    params.append(supplier_id)
    run_query(
        f"UPDATE suppliers SET {', '.join(update_fields)} WHERE supplier_id = %s",
        params,
    )

    return jsonify({"message": "Supplier updated successfully."}), 200


def deleteSupplier(supplier_id):
    """
    Delete a supplier (only if no vehicles reference it).
    Path param: supplier_id
    Returns:    JSON { message } (204 has no body)
    Status:     204, 404, 409
    """
    existing = run_query(
        "SELECT supplier_id FROM suppliers WHERE supplier_id = %s",
        (supplier_id,),
        fetch="one",
    )

    if not existing:
        return jsonify({"message": "Supplier not found."}), 404

    vehicles = run_query(
        "SELECT COUNT(*) AS total FROM vehicles WHERE supplier_id = %s",
        (supplier_id,),
        fetch="one",
    )

    if vehicles["total"] > 0:
        return jsonify(
            {"message": "Cannot delete supplier with linked vehicles."}
        ), 409

    run_query("DELETE FROM suppliers WHERE supplier_id = %s", (supplier_id,))
    return jsonify({"message": "Supplier deleted successfully."}), 204
