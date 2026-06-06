from flask import request, jsonify
from conn import run_query
from datetime import datetime


def getSupplies():
    """
    List all supplies with supplier details.
    Query param: ?low_stock=1 (filter where stock_qty <= reorder_level)
    Returns:    JSON { data: [...] }
    Status:     200 (empty list returns 200 with [])
    """
    low_stock = request.args.get("low_stock")

    if low_stock == "1":
        supplies = run_query(
            """
            SELECT su.*, sp.company_name, sp.contact_name, sp.contact_email, sp.contact_phone
            FROM supplies su
            JOIN suppliers sp ON su.supplier_id = sp.supplier_id
            WHERE su.stock_qty <= su.reorder_level
            ORDER BY sp.company_name ASC, su.part_name ASC
            """,
            fetch="all",
        )
    else:
        supplies = run_query(
            """
            SELECT su.*, sp.company_name, sp.contact_name, sp.contact_email, sp.contact_phone
            FROM supplies su
            JOIN suppliers sp ON su.supplier_id = sp.supplier_id
            ORDER BY sp.company_name ASC, su.part_name ASC
            """,
            fetch="all",
        )

    return jsonify({"data": supplies}), 200


def getSuppliesDetail(supply_id):
    """
    Get single supply detail with supplier info.
    Path param: supply_id
    Returns:    JSON { data: { ... } }
    Status:     200, 404
    """
    supply = run_query(
        """
        SELECT su.*, sp.company_name, sp.contact_name, sp.contact_email, sp.contact_phone
        FROM supplies su
        JOIN suppliers sp ON su.supplier_id = sp.supplier_id
        WHERE su.supply_id = %s
        """,
        (supply_id,),
        fetch="one",
    )

    if not supply:
        return jsonify({"message": "Supply not found."}), 404

    return jsonify({"data": supply}), 200


def createSupplies():
    """
    Create a new supply/part record.
    Body:       part_name (required), part_number, unit_cost, stock_qty, reorder_level, supplier_id (required)
    Returns:    JSON { message, supply_id }
    Status:     201, 400, 404, 422
    """
    data = request.get_json(silent=True) or {}
    part_name = data.get("part_name")
    part_number = data.get("part_number")
    unit_cost = data.get("unit_cost")
    stock_qty = data.get("stock_qty")
    reorder_level = data.get("reorder_level")
    supplier_id = data.get("supplier_id")

    if not part_name or not part_name.strip():
        return jsonify({"message": "part_name is required."}), 400

    if supplier_id is None:
        return jsonify({"message": "supplier_id is required."}), 400

    if unit_cost is not None:
        try:
            unit_cost = float(unit_cost)
            if unit_cost < 0:
                return jsonify({"message": "unit_cost must be >= 0."}), 422
        except (ValueError, TypeError):
            return jsonify({"message": "unit_cost must be a valid number."}), 422
    else:
        unit_cost = 0.0

    if stock_qty is not None:
        try:
            stock_qty = int(stock_qty)
            if stock_qty < 0:
                return jsonify({"message": "stock_qty must be >= 0."}), 422
        except (ValueError, TypeError):
            return jsonify({"message": "stock_qty must be a valid integer."}), 422
    else:
        stock_qty = 0

    if reorder_level is not None:
        try:
            reorder_level = int(reorder_level)
            if reorder_level < 0:
                return jsonify({"message": "reorder_level must be >= 0."}), 422
        except (ValueError, TypeError):
            return jsonify({"message": "reorder_level must be a valid integer."}), 422
    else:
        reorder_level = 10

    supplier = run_query(
        "SELECT supplier_id FROM suppliers WHERE supplier_id = %s",
        (supplier_id,),
        fetch="one",
    )

    if not supplier:
        return jsonify({"message": "Supplier not found."}), 404

    supply_id = run_query(
        """
        INSERT INTO supplies (part_name, part_number, unit_cost, stock_qty, reorder_level, supplier_id, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            part_name.strip(),
            part_number.strip() if part_number else None,
            unit_cost,
            stock_qty,
            reorder_level,
            supplier_id,
            datetime.now(),
        ),
    )

    return jsonify({"message": "Supply created successfully.", "supply_id": supply_id}), 201


def updateSupplies(supply_id):
    """
    Update a supply record.
    Path param: supply_id
    Body:       part_name, part_number, unit_cost, stock_qty, reorder_level, supplier_id
    Returns:    JSON { message }
    Status:     200, 400, 404, 422
    """
    existing = run_query(
        "SELECT supply_id FROM supplies WHERE supply_id = %s",
        (supply_id,),
        fetch="one",
    )

    if not existing:
        return jsonify({"message": "Supply not found."}), 404

    data = request.get_json(silent=True) or {}

    # Validate numeric fields if provided
    unit_cost = data.get("unit_cost")
    if unit_cost is not None:
        try:
            unit_cost = float(unit_cost)
            if unit_cost < 0:
                return jsonify({"message": "unit_cost must be >= 0."}), 422
        except (ValueError, TypeError):
            return jsonify({"message": "unit_cost must be a valid number."}), 422

    stock_qty = data.get("stock_qty")
    if stock_qty is not None:
        try:
            stock_qty = int(stock_qty)
            if stock_qty < 0:
                return jsonify({"message": "stock_qty must be >= 0."}), 422
        except (ValueError, TypeError):
            return jsonify({"message": "stock_qty must be a valid integer."}), 422

    reorder_level = data.get("reorder_level")
    if reorder_level is not None:
        try:
            reorder_level = int(reorder_level)
            if reorder_level < 0:
                return jsonify({"message": "reorder_level must be >= 0."}), 422
        except (ValueError, TypeError):
            return jsonify({"message": "reorder_level must be a valid integer."}), 422

    supplier_id = data.get("supplier_id")
    if supplier_id is not None:
        supplier = run_query(
            "SELECT supplier_id FROM suppliers WHERE supplier_id = %s",
            (supplier_id,),
            fetch="one",
        )
        if not supplier:
            return jsonify({"message": "Supplier not found."}), 404

    params = {
        "part_name": data.get("part_name"),
        "part_number": data.get("part_number"),
        "unit_cost": unit_cost,
        "stock_qty": stock_qty,
        "reorder_level": reorder_level,
        "supplier_id": data.get("supplier_id"),
        "updated_at": datetime.now(),
    }

    fields = []
    values = []
    for key, value in params.items():
        if value is not None:
            fields.append(f"{key} = %s")
            values.append(value)

    if not fields:
        return jsonify({"message": "At least one field is required to update."}), 400

    values.append(supply_id)
    run_query(
        f"UPDATE supplies SET {', '.join(fields)} WHERE supply_id = %s",
        tuple(values),
    )

    return jsonify({"message": "Supply updated successfully."}), 200


def deleteSupplies(supply_id):
    """
    Delete a supply (only if no active service bookings reference it).
    Path param: supply_id
    Returns:    JSON { message } (204 has no body)
    Status:     204, 404, 409
    """
    existing = run_query(
        "SELECT supply_id FROM supplies WHERE supply_id = %s",
        (supply_id,),
        fetch="one",
    )

    if not existing:
        return jsonify({"message": "Supply not found."}), 404

    # Check if any active service bookings reference this supply
    active = run_query(
        """
        SELECT COUNT(*) AS total FROM service_bookings sb
        JOIN service_slots ss ON sb.slot_id = ss.slot_id
        WHERE sb.notes LIKE %s AND sb.status IN ('pending', 'confirmed')
        """,
        (f"%supply_id={supply_id}%",),
        fetch="one",
    )

    if active and active["total"] > 0:
        return jsonify(
            {"message": "Cannot delete supply referenced by active service bookings."}
        ), 409

    run_query("DELETE FROM supplies WHERE supply_id = %s", (supply_id,))
    return jsonify({"message": "Supply deleted successfully."}), 204


def getLowStockSupplies():
    """
    List supplies where stock_qty <= reorder_level, with supplier contact info.
    Returns:    JSON { data: [...] }
    Status:     200 (empty list returns 200 with [])
    """
    supplies = run_query(
        """
        SELECT su.*, sp.company_name, sp.contact_name, sp.contact_email, sp.contact_phone
        FROM supplies su
        JOIN suppliers sp ON su.supplier_id = sp.supplier_id
        WHERE su.stock_qty <= su.reorder_level
        ORDER BY sp.company_name ASC, su.part_name ASC
        """,
        fetch="all",
    )

    return jsonify({"data": supplies}), 200
