"""
Supplies controller — CRUD for the supplies table (inventory parts).

Each supply is linked to a supplier and tracks stock quantity,
unit cost, and reorder level.
"""

from datetime import datetime
from flask import request, jsonify
from conn import run_query


def list_supplies():
    """
    GET /admin/supplies/

    Return all supplies, optionally filtered by low_stock query param.
    Joins with suppliers to include contact info.
    """
    low_stock = request.args.get("low_stock")

    if low_stock == "1":
        rows = run_query(
            """
            SELECT s.*, sp.company_name, sp.contact_name,
                   sp.contact_email, sp.contact_phone
            FROM supplies s
            LEFT JOIN suppliers sp ON s.supplier_id = sp.supplier_id
            WHERE s.stock_qty < s.reorder_level
            ORDER BY s.part_name ASC
            """,
            fetch="all",
        )
    else:
        rows = run_query(
            """
            SELECT s.*, sp.company_name, sp.contact_name,
                   sp.contact_email, sp.contact_phone
            FROM supplies s
            LEFT JOIN suppliers sp ON s.supplier_id = sp.supplier_id
            ORDER BY s.part_name ASC
            """,
            fetch="all",
        )

    return jsonify({"data": rows}), 200


def get_supply(supply_id):
    """
    GET /admin/supplies/<id>

    Return a single supply by its ID, including supplier contact info.
    """
    row = run_query(
        """
        SELECT s.*, sp.company_name, sp.contact_name,
               sp.contact_email, sp.contact_phone
        FROM supplies s
        LEFT JOIN suppliers sp ON s.supplier_id = sp.supplier_id
        WHERE s.supply_id = %s
        """,
        (supply_id,),
        fetch="one",
    )

    if not row:
        return jsonify({"message": "Supply not found"}), 404

    return jsonify({"data": row}), 200


def create_supply():
    """
    POST /admin/supplies/

    Create a new supply record.  Validates required fields and
    ensures the referenced supplier exists.
    """
    data = request.get_json(silent=True) or {}

    supplier_id = data.get("supplier_id")
    part_name = data.get("part_name")
    unit_cost = data.get("unit_cost")
    stock_qty = data.get("stock_qty")
    reorder_level = data.get("reorder_level")

    # ── Required field ────────────────────────────────────────────────
    if not part_name:
        return jsonify({"message": "part_name is required."}), 400

    # ── Numeric validations ───────────────────────────────────────────
    if unit_cost is not None and (not isinstance(unit_cost, (int, float)) or unit_cost < 0):
        return jsonify({"message": "unit_cost must be a non-negative number."}), 422

    if stock_qty is not None and (not isinstance(stock_qty, int) or stock_qty < 0):
        return jsonify({"message": "stock_qty must be a non-negative integer."}), 422

    if reorder_level is not None and (not isinstance(reorder_level, int) or reorder_level < 0):
        return jsonify({"message": "reorder_level must be a non-negative integer."}), 422

    # ── Supplier existence ────────────────────────────────────────────
    supplier = run_query(
        "SELECT supplier_id FROM suppliers WHERE supplier_id = %s",
        (supplier_id,),
        fetch="one",
    )
    if not supplier:
        return jsonify({"message": "Supplier not found."}), 404

    # ── Insert ────────────────────────────────────────────────────────
    new_id = run_query(
        """
        INSERT INTO supplies (supplier_id, part_name, unit_cost,
                              stock_qty, reorder_level)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (supplier_id, part_name, unit_cost, stock_qty, reorder_level),
    )

    return jsonify({"message": "Supply added successfully.", "supply_id": new_id}), 201


def update_supply(supply_id):
    """
    PUT /admin/supplies/<id>

    Update an existing supply record.  Only supplied fields are updated.
    """
    data = request.get_json(silent=True) or {}

    # ── Existence check ───────────────────────────────────────────────
    existing = run_query(
        "SELECT * FROM supplies WHERE supply_id = %s",
        (supply_id,),
        fetch="one",
    )
    if not existing:
        return jsonify({"message": "Supply not found."}), 404

    # ── Build dynamic UPDATE ──────────────────────────────────────────
    fields = {
        "part_name": data.get("part_name"),
        "unit_cost": data.get("unit_cost"),
        "stock_qty": data.get("stock_qty"),
        "reorder_level": data.get("reorder_level"),
        "supplier_id": data.get("supplier_id"),
    }

    # Validate numeric fields if present
    if fields["unit_cost"] is not None and (
        not isinstance(fields["unit_cost"], (int, float)) or fields["unit_cost"] < 0
    ):
        return jsonify({"message": "unit_cost must be a non-negative number."}), 422

    if fields["stock_qty"] is not None and (
        not isinstance(fields["stock_qty"], int) or fields["stock_qty"] < 0
    ):
        return jsonify({"message": "stock_qty must be a non-negative integer."}), 422

    update_clauses = []
    params = []
    for col, val in fields.items():
        if val is not None:
            update_clauses.append(f"{col} = %s")
            params.append(val)

    if not update_clauses:
        return jsonify({"message": "No fields to update."}), 400

    params.append(supply_id)
    run_query(
        f"UPDATE supplies SET {', '.join(update_clauses)} WHERE supply_id = %s",
        params,
    )

    return jsonify({"message": "Supply updated successfully."}), 200


def delete_supply(supply_id):
    """
    DELETE /admin/supplies/<id>

    Delete a supply record.  Checks for active service-bookings references
    before deleting (409 if refs exist).
    """
    # ── Existence check ───────────────────────────────────────────────
    existing = run_query(
        "SELECT * FROM supplies WHERE supply_id = %s",
        (supply_id,),
        fetch="one",
    )
    if not existing:
        return jsonify({"message": "Supply not found."}), 404

    # ── Check for active bookings referencing this supply ─────────────
    refs = run_query(
        """
        SELECT COUNT(*) AS total FROM service_bookings
        WHERE supply_id = %s AND status IN ('pending', 'in_progress')
        """,
        (supply_id,),
        fetch="one",
    )
    if refs and refs["total"] > 0:
        return jsonify({
            "message": "Cannot delete supply; it has active service bookings."
        }), 409

    run_query("DELETE FROM supplies WHERE supply_id = %s", (supply_id,))
    return jsonify({"message": "Supply deleted successfully."}), 204


def low_stock_supplies():
    """
    GET /admin/supplies/low-stock

    Convenience endpoint for supplies where stock_qty < reorder_level.
    """
    rows = run_query(
        """
        SELECT s.*, sp.company_name, sp.contact_name,
               sp.contact_email, sp.contact_phone
        FROM supplies s
        LEFT JOIN suppliers sp ON s.supplier_id = sp.supplier_id
        WHERE s.stock_qty < s.reorder_level
        ORDER BY (s.reorder_level - s.stock_qty) DESC
        """,
        fetch="all",
    )
    return jsonify({"data": rows}), 200
