from flask import jsonify, session, request
from conn import run_query


def getServiceStaffDashboard():
    user_id = session["user"]

    for_repair = run_query(
        """SELECT COUNT(*) AS count FROM service_bookings b
           JOIN service_slots s ON b.slot_id = s.slot_id
           WHERE s.slot_type = 'repair' AND b.status IN ('pending','confirmed','in_progress','draft_estimate','awaiting_signature')""",
        fetch="one",
    )

    for_maintenance = run_query(
        """SELECT COUNT(*) AS count FROM service_bookings b
           JOIN service_slots s ON b.slot_id = s.slot_id
           WHERE s.slot_type = 'maintenance' AND b.status IN ('pending','confirmed','in_progress','draft_estimate','awaiting_signature')""",
        fetch="one",
    )

    warranty_claims = run_query(
        "SELECT COUNT(*) AS count FROM warranty_claims WHERE status IN ('submitted','under_review','approved')",
        fetch="one",
    )

    resolved_services = run_query(
        "SELECT COUNT(*) AS count FROM service_bookings WHERE status = 'completed'",
        fetch="one",
    )

    accumulated_revenue = run_query(
        """SELECT COALESCE(SUM(
            JSON_EXTRACT(estimate_data, '$.total')
        ), 0) AS total FROM service_bookings WHERE status = 'completed'""",
        fetch="one",
    )

    maintenance_list = run_query(
        """SELECT b.booking_id, b.status, b.notes, b.estimate_data, b.technician_notes,
                  u.username AS customer_name, v.brand, v.model, v.year, s.slot_datetime
           FROM service_bookings b
           JOIN service_slots s ON b.slot_id = s.slot_id
           JOIN users u ON b.customer_id = u.user_id
           JOIN vehicles v ON b.vehicle_id = v.vehicle_id
           WHERE s.slot_type = 'maintenance'
           ORDER BY s.slot_datetime DESC
           LIMIT 5""",
        fetch="all",
    )

    warranty_claims_list = run_query(
        """SELECT w.claim_id, w.status, w.claim_type, w.submitted_at, w.resolution,
                  u.username AS customer_name, v.brand, v.model
           FROM warranty_claims w
           JOIN sales sa ON w.sale_id = sa.sale_id
           JOIN users u ON sa.customer_id = u.user_id
           JOIN vehicles v ON sa.vehicle_id = v.vehicle_id
           ORDER BY w.submitted_at DESC
           LIMIT 5""",
        fetch="all",
    )

    history = run_query(
        """SELECT b.booking_id, s.slot_type AS entry_type, b.status,
                  u.username AS customer_name, v.brand, v.model, s.slot_datetime
           FROM service_bookings b
           JOIN service_slots s ON b.slot_id = s.slot_id
           JOIN users u ON b.customer_id = u.user_id
           JOIN vehicles v ON b.vehicle_id = v.vehicle_id
           WHERE b.status = 'completed'
           ORDER BY s.slot_datetime DESC
           LIMIT 5""",
        fetch="all",
    )

    return jsonify({
        "data": {
            "for_repair": for_repair["count"],
            "for_maintenance": for_maintenance["count"],
            "warranty_claims": warranty_claims["count"],
            "resolved_services": resolved_services["count"],
            "accumulated_revenue": float(accumulated_revenue["total"]),
            "maintenance_list": maintenance_list,
            "warranty_claims_list": warranty_claims_list,
            "history": history,
        }
    }), 200


def getCustomerListHandler():
    customers = run_query(
        "SELECT u.user_id, u.username, u.email FROM users u WHERE u.role = 'customer' ORDER BY u.username ASC",
        fetch="all",
    )

    for c in customers:
        c["vehicles"] = run_query(
            "SELECT v.vehicle_id, v.brand, v.model, v.year FROM vehicles v JOIN sales s ON v.vehicle_id = s.vehicle_id WHERE s.customer_id = %s",
            (c["user_id"],),
            fetch="all",
        )
        c["full_name"] = ""
        c["phone_number"] = ""

    return jsonify({"data": customers}), 200


def getServiceHistoryHandler():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    entry_type = request.args.get("type")
    offset = (page - 1) * per_page

    if entry_type == "warranty":
        count = run_query(
            "SELECT COUNT(*) AS total FROM warranty_claims WHERE status IN ('resolved','rejected')", fetch="one",
        )
        items = run_query(
            """SELECT w.claim_id, 'warranty' AS entry_type, w.status,
                      u.username AS customer_name, v.brand, v.model, v.year,
                      w.submitted_at AS slot_datetime,
                      NULL AS assigned_to_name,
                      r.username AS reviewer_name
               FROM warranty_claims w
               JOIN sales sa ON w.sale_id = sa.sale_id
               JOIN users u ON sa.customer_id = u.user_id
               JOIN vehicles v ON sa.vehicle_id = v.vehicle_id
               LEFT JOIN users r ON w.reviewed_by = r.user_id
               WHERE w.status IN ('resolved','rejected')
               ORDER BY w.submitted_at DESC
               LIMIT %s OFFSET %s""",
            (per_page, offset), fetch="all",
        )
    elif entry_type:
        count = run_query(
            """SELECT COUNT(*) AS total FROM service_bookings b
               JOIN service_slots s ON b.slot_id = s.slot_id
               WHERE s.slot_type = %s AND b.status IN ('completed','cancelled')""",
            (entry_type,), fetch="one",
        )
        items = run_query(
            """SELECT b.booking_id, s.slot_type AS entry_type, b.status,
                      u.username AS customer_name, v.brand, v.model, v.year,
                      s.slot_datetime,
                      a.username AS assigned_to_name,
                      NULL AS reviewer_name
               FROM service_bookings b
               JOIN service_slots s ON b.slot_id = s.slot_id
               JOIN users u ON b.customer_id = u.user_id
               JOIN vehicles v ON b.vehicle_id = v.vehicle_id
               LEFT JOIN users a ON b.assigned_to = a.user_id
               WHERE s.slot_type = %s AND b.status IN ('completed','cancelled')
               ORDER BY s.slot_datetime DESC
               LIMIT %s OFFSET %s""",
            (entry_type, per_page, offset), fetch="all",
        )
    else:
        count = run_query(
            """SELECT COUNT(*) AS total FROM (
                SELECT booking_id FROM service_bookings b
                JOIN service_slots s ON b.slot_id = s.slot_id
                WHERE b.status IN ('completed','cancelled') AND s.slot_type IN ('maintenance','repair')
                UNION ALL
                SELECT claim_id FROM warranty_claims WHERE status IN ('resolved','rejected')
            ) AS combined""", fetch="one",
        )
        items = run_query(
            """SELECT * FROM (
                SELECT b.booking_id, s.slot_type AS entry_type, b.status,
                       u.username AS customer_name, v.brand, v.model, v.year,
                       s.slot_datetime,
                       a.username AS assigned_to_name,
                       NULL AS reviewer_name
                FROM service_bookings b
                JOIN service_slots s ON b.slot_id = s.slot_id
                JOIN users u ON b.customer_id = u.user_id
                JOIN vehicles v ON b.vehicle_id = v.vehicle_id
                LEFT JOIN users a ON b.assigned_to = a.user_id
                WHERE b.status IN ('completed','cancelled') AND s.slot_type IN ('maintenance','repair')
                UNION ALL
                SELECT w.claim_id, 'warranty' AS entry_type, w.status,
                       u.username AS customer_name, v.brand, v.model, v.year,
                       w.submitted_at AS slot_datetime,
                       NULL AS assigned_to_name,
                       r.username AS reviewer_name
                FROM warranty_claims w
                JOIN sales sa ON w.sale_id = sa.sale_id
                JOIN users u ON sa.customer_id = u.user_id
                JOIN vehicles v ON sa.vehicle_id = v.vehicle_id
                LEFT JOIN users r ON w.reviewed_by = r.user_id
                WHERE w.status IN ('resolved','rejected')
            ) AS combined
            ORDER BY slot_datetime DESC
            LIMIT %s OFFSET %s""",
            (per_page, offset), fetch="all",
        )

    return jsonify({"data": items, "total": count["total"]}), 200


def createBookingHandler():
    data = request.get_json(silent=True) or {}

    customer_id = data.get("customer_id")
    vehicle_id = data.get("vehicle_id")
    slot_id = data.get("slot_id")
    notes = data.get("notes", "")

    if not all([customer_id, vehicle_id, slot_id]):
        return jsonify({"message": "customer_id, vehicle_id, and slot_id are required."}), 400

    slot = run_query(
        "SELECT slot_type FROM service_slots WHERE slot_id = %s",
        (slot_id,), fetch="one",
    )
    if not slot:
        return jsonify({"message": "Slot not found."}), 404

    booking_type = slot["slot_type"]

    booking_id = run_query(
        """INSERT INTO service_bookings (customer_id, vehicle_id, slot_id, assigned_to, status, notes, booking_type)
           VALUES (%s, %s, %s, %s, 'pending', %s, %s)""",
        (customer_id, vehicle_id, slot_id, session["user"], notes, booking_type),
    )

    return jsonify({"message": "Booking created.", "booking_id": booking_id}), 201


def updateBookingNotesHandler(booking_id):
    data = request.get_json(silent=True) or {}
    notes = data.get("notes", "")

    run_query(
        "UPDATE service_bookings SET notes = %s WHERE booking_id = %s",
        (notes, booking_id),
    )

    return jsonify({"message": "Notes updated."}), 200
