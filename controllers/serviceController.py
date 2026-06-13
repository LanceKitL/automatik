from flask import session, jsonify, request
from utils.log import audit_log
from utils.notification import fire_notif, broadcast_notif
from datetime import datetime
from conn import run_query, get_db
import mysql.connector
import json

# --- SERVICE SLOTS ---

def listServiceSlotsHandler():
    """
    List available service slots.
    Filters (query string): ?slot_type=test_drive|maintenance|repair, ?date=YYYY-MM-DD
    Returns:    JSON { data: [{ slot_id, slot_datetime, slot_type, capacity, is_available, remaining, ... }] }
    Status:     200
    """
    slot_type = request.args.get("slot_type")
    date = request.args.get("date")

    conditions = ["s.is_available = 1"]
    params = []

    if slot_type:
        conditions.append("s.slot_type = %s")
        params.append(slot_type)
    if date:
        conditions.append("DATE(s.slot_datetime) = %s")
        params.append(date)

    where = " AND ".join(conditions)

    slots = run_query(f"""
        SELECT s.*,
               s.capacity - COALESCE(b.booked, 0) AS remaining
        FROM service_slots s
        LEFT JOIN (
            SELECT slot_id, COUNT(*) AS booked
            FROM service_bookings
            WHERE status != 'cancelled'
            GROUP BY slot_id
        ) b ON s.slot_id = b.slot_id
        WHERE {where}
        ORDER BY s.slot_datetime ASC
    """, params, fetch="all")

    return jsonify({"data": slots}), 200


def getServiceSlotHandler(slot_id):
    """
    Get single slot detail with remaining capacity.
    Path param: slot_id
    Returns:    JSON { data: { slot_id, slot_datetime, slot_type, capacity, is_available, remaining } }
    Status:     200, 404
    """
    slot = run_query("""
        SELECT s.*,
               s.capacity - COALESCE(b.booked, 0) AS remaining
        FROM service_slots s
        LEFT JOIN (
            SELECT slot_id, COUNT(*) AS booked
            FROM service_bookings
            WHERE status != 'cancelled'
            GROUP BY slot_id
        ) b ON s.slot_id = b.slot_id
        WHERE s.slot_id = %s
    """, (slot_id,), fetch="one")

    if not slot:
        return jsonify({"message": "Slot not found."}), 404

    return jsonify({"data": slot}), 200


def createServiceSlotHandler():
    """
    Create a new service slot.
    Body:       slot_datetime (required), slot_type (required, enum), capacity (default 1)
    Returns:    JSON { message, slot_id }
    Status:     201, 400, 422
    """
    data = request.get_json()

    slot_datetime = data.get("slot_datetime")
    slot_type = data.get("slot_type")
    capacity = data.get("capacity", 1)

    if not slot_datetime or not slot_type:
        return jsonify({"message": "slot_datetime and slot_type are required."}), 400

    if slot_type not in ("test_drive", "maintenance", "repair"):
        return jsonify({"message": "slot_type must be test_drive, maintenance, or repair."}), 422

    if not isinstance(capacity, int) or capacity < 1:
        return jsonify({"message": "capacity must be a positive integer."}), 422

    slot_id = run_query("""
        INSERT INTO service_slots (slot_datetime, slot_type, capacity, is_available)
        VALUES (%s, %s, %s, 1)
    """, (slot_datetime, slot_type, capacity))

    audit_log(session["user"], "POST", "service_slots", slot_id)
    return jsonify({"message": "Slot created!", "slot_id": slot_id}), 201


def updateServiceSlotHandler(slot_id):
    """
    Update slot capacity or availability.
    Path param: slot_id
    Body:       capacity (int >= 1), is_available (bool) — at least one required
    Returns:    JSON { message }
    Status:     200, 400, 404, 409 (reducing below current bookings), 422
    """
    data = request.get_json()
    capacity = data.get("capacity")
    is_available = data.get("is_available")

    if capacity is None and is_available is None:
        return jsonify({"message": "No fields to update."}), 400

    slot = run_query("SELECT * FROM service_slots WHERE slot_id = %s", (slot_id,), fetch="one")
    if not slot:
        return jsonify({"message": "Slot not found."}), 404

    if capacity is not None:
        if not isinstance(capacity, int) or capacity < 1:
            return jsonify({"message": "capacity must be a positive integer."}), 422

        booked = run_query("""
            SELECT COUNT(*) AS total FROM service_bookings
            WHERE slot_id = %s AND status != 'cancelled'
        """, (slot_id,), fetch="one")

        if capacity < booked["total"]:
            return jsonify({"message": "Cannot reduce capacity below current bookings."}), 409

    update_fields = []
    params = []
    if capacity is not None:
        update_fields.append("capacity = %s")
        params.append(capacity)
    if is_available is not None:
        update_fields.append("is_available = %s")
        params.append(1 if is_available else 0)

    params.append(slot_id)
    run_query(f"UPDATE service_slots SET {', '.join(update_fields)} WHERE slot_id = %s", params)
    audit_log(session["user"], "PUT", "service_slots", slot_id)
    return jsonify({"message": "Slot updated!"}), 200


def deleteServiceSlotHandler(slot_id):
    """
    Delete a slot (only if no active pending/confirmed bookings).
    Path param: slot_id
    Returns:    JSON { message } (204 has no body)
    Status:     204, 404, 409
    """
    slot = run_query("SELECT * FROM service_slots WHERE slot_id = %s", (slot_id,), fetch="one")
    if not slot:
        return jsonify({"message": "Slot not found."}), 404

    active = run_query("""
        SELECT COUNT(*) AS total FROM service_bookings
        WHERE slot_id = %s AND status IN ('pending', 'confirmed')
    """, (slot_id,), fetch="one")

    if active["total"] > 0:
        return jsonify({"message": "Slot has active bookings."}), 409

    run_query("DELETE FROM service_slots WHERE slot_id = %s", (slot_id,))
    audit_log(session["user"], "DELETE", "service_slots", slot_id)
    return jsonify({"message": "Slot deleted."}), 204


# --- SERVICE BOOKINGS ---

def listMyBookingsHandler():
    """
    List current customer's service bookings (auto-filtered by session user).
    Returns:    JSON { data: [{ booking_id, slot_id, vehicle_id, status, slot_datetime, brand, model, ... }] }
    Status:     200
    """
    user_id = session["user"]

    bookings = run_query("""
        SELECT b.*, s.slot_datetime, s.slot_type,
               v.brand, v.model, v.year
        FROM service_bookings b
        JOIN service_slots s ON b.slot_id = s.slot_id
        JOIN vehicles v ON b.vehicle_id = v.vehicle_id
        WHERE b.customer_id = %s
        ORDER BY b.created_at DESC
    """, (user_id,), fetch="all")

    return jsonify({"data": bookings}), 200


def createBookingHandler():
    """
    Create a service booking. Uses FOR UPDATE + lock timeout handling (503).
    Body:       slot_id (required), vehicle_id (required), booking_type (required, enum),
                warranty_claim_id (optional)
    Returns:    JSON { message, booking_id }
    Status:     201, 400, 409 (slot full), 422, 503
    """
    data = request.get_json()
    user_id = session["user"]
    slot_id = data.get("slot_id")
    vehicle_id = data.get("vehicle_id")
    booking_type = data.get("booking_type")
    warranty_claim_id = data.get("warranty_claim_id")

    if not slot_id or not vehicle_id or not booking_type:
        return jsonify({"message": "slot_id, vehicle_id, and booking_type are required."}), 400

    if booking_type not in ("test_drive", "maintenance", "repair"):
        return jsonify({"message": "booking_type must be test_drive, maintenance, or repair."}), 422

    conn, cursor = get_db()
    try:
        cursor.execute(
            "SELECT capacity, is_available FROM service_slots WHERE slot_id = %s FOR UPDATE",
            (slot_id,))
        slot = cursor.fetchone()

        if not slot or not slot["is_available"]:
            return jsonify({"message": "Slot is unavailable."}), 400

        cursor.execute(
            "SELECT COUNT(*) AS total FROM service_bookings WHERE slot_id = %s AND status != %s",
            (slot_id, "cancelled"))
        current_bookings = cursor.fetchone()["total"]

        if current_bookings >= slot["capacity"]:
            return jsonify({"message": "Slot has reached its capacity."}), 409

        cursor.execute("""
            INSERT INTO service_bookings
            (customer_id, slot_id, vehicle_id, booking_type, status, warranty_claim_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, slot_id, vehicle_id, booking_type, "pending", warranty_claim_id))
        booking_id = cursor.lastrowid

        if (current_bookings + 1) >= slot["capacity"]:
            cursor.execute(
                "UPDATE service_slots SET is_available = 0 WHERE slot_id = %s",
                (slot_id,))

        conn.commit()
        audit_log(session["user"], "POST", "service_bookings", booking_id, conn=conn, cursor=cursor)

        # Notify agents and admins about the new booking
        broadcast_notif(
            role="agent",
            title="New Booking",
            message=f"{booking_type.replace('_', ' ').title()} booking #{booking_id} created.",
            channel="in_app",
            ref_type="service_bookings",
            ref_id=booking_id,
        )
        broadcast_notif(
            role="admin",
            title="New Booking",
            message=f"{booking_type.replace('_', ' ').title()} booking #{booking_id} created.",
            channel="in_app",
            ref_type="service_bookings",
            ref_id=booking_id,
        )

        return jsonify({"message": "Booking created!", "booking_id": booking_id}), 201

    except mysql.connector.errors.OperationalError as e:
        conn.rollback()
        if "Lock wait timeout" in str(e):
            return jsonify({"error": "Resource locked. Retry."}), 503
        raise
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def updateBookingStatusHandler(booking_id, new_status):
    """
    Transition booking status through: pending -> confirmed | pending -> cancelled | confirmed -> completed.
    Restores slot capacity on cancel. Notifies customer on confirm.
    Path param: booking_id
    Action:     "confirmed" | "completed" | "cancelled" (passed from route)
    Returns:    JSON { message }
    Status:     200, 400, 404, 409 (invalid transition), 503
    """
    valid = {"confirmed", "completed", "cancelled"}
    if new_status not in valid:
        return jsonify({"message": "Invalid status."}), 400

    conn, cursor = get_db()
    try:
        cursor.execute(
            "SELECT * FROM service_bookings WHERE booking_id = %s FOR UPDATE",
            (booking_id,))
        booking = cursor.fetchone()

        if not booking:
            return jsonify({"message": "Booking not found."}), 404

        if new_status == "cancelled" and booking["status"] == "cancelled":
            return jsonify({"message": "Booking is already cancelled."}), 409

        if new_status == "confirmed" and booking["status"] != "pending":
            return jsonify({"message": "Only pending bookings can be confirmed."}), 409

        if new_status == "completed" and booking["status"] != "confirmed":
            return jsonify({"message": "Only confirmed bookings can be completed."}), 409

        cursor.execute(
            "UPDATE service_bookings SET status = %s WHERE booking_id = %s",
            (new_status, booking_id))

        if new_status == "cancelled":
            cursor.execute(
                "UPDATE service_slots SET is_available = 1 WHERE slot_id = %s",
                (booking["slot_id"],))

        conn.commit()

        if new_status == "confirmed":
            fire_notif(booking["customer_id"], "Booking Confirmed",
                       "Your service booking has been confirmed.", "in_app",
                       "service_bookings", booking_id)

        audit_log(session["user"], f"PUT status={new_status}",
                  "service_bookings", booking_id, conn=conn, cursor=cursor)
        return jsonify({"message": f"Booking {new_status}."}), 200

    except mysql.connector.errors.OperationalError as e:
        conn.rollback()
        if "Lock wait timeout" in str(e):
            return jsonify({"error": "Resource locked. Retry."}), 503
        raise
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def listAllBookingsHandler():
    """
    List all service bookings (admin / service_advisor). JOINs customer, slot, vehicle, assigned advisor.
    Returns:    JSON { data: [{ booking_id, customer_name, slot_datetime, slot_type, brand, model, status, assigned_to_name, ... }] }
    Status:     200
    """
    bookings = run_query("""
        SELECT b.*, s.slot_datetime, s.slot_type,
               v.brand, v.model, v.year,
               u.username AS customer_name,
               a.username AS assigned_to_name
        FROM service_bookings b
        JOIN service_slots s ON b.slot_id = s.slot_id
        JOIN vehicles v ON b.vehicle_id = v.vehicle_id
        JOIN users u ON b.customer_id = u.user_id
        LEFT JOIN users a ON b.assigned_to = a.user_id
        ORDER BY b.created_at DESC
    """, fetch="all")

    return jsonify({"data": bookings}), 200


def getMyBookingsHandler():
    """
    List bookings assigned to the current logged-in user (service_advisor).
    Returns:    JSON { data: [{ booking_id, customer_name, slot_datetime, slot_type, brand, model, status, technician_notes, ... }] }
    Status:     200
    """
    user_id = session["user"]
    bookings = run_query("""
        SELECT b.*, s.slot_datetime, s.slot_type,
               v.brand, v.model, v.year,
               u.username AS customer_name
        FROM service_bookings b
        JOIN service_slots s ON b.slot_id = s.slot_id
        JOIN vehicles v ON b.vehicle_id = v.vehicle_id
        JOIN users u ON b.customer_id = u.user_id
        WHERE b.assigned_to = %s
        ORDER BY b.created_at DESC
    """, (user_id,), fetch="all")

    return jsonify({"data": bookings}), 200


def assignToSelfHandler(booking_id):
    """
    Self-assign a service booking to the current logged-in service_advisor.
    Only unassigned bookings may be claimed.
    Path param: booking_id
    Returns:    JSON { message }
    Status:     200, 404, 409
    """
    user_id = session["user"]
    conn, cursor = get_db()
    try:
        cursor.execute(
            "SELECT * FROM service_bookings WHERE booking_id = %s FOR UPDATE",
            (booking_id,))
        booking = cursor.fetchone()

        if not booking:
            return jsonify({"message": "Booking not found."}), 404

        if booking["assigned_to"] is not None:
            return jsonify({"message": "Booking is already assigned."}), 409

        cursor.execute(
            "UPDATE service_bookings SET assigned_to = %s WHERE booking_id = %s",
            (user_id, booking_id))
        conn.commit()

        audit_log(session["user"], "PUT self-assign",
                  "service_bookings", booking_id, conn=conn, cursor=cursor)
        return jsonify({"message": "Booking assigned to you."}), 200

    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def updateTechnicianNotesHandler(booking_id):
    """
    Update the technician_notes for a service booking.
    Only the assigned advisor or an admin may update notes.
    Path param: booking_id
    Body:       technician_notes (string, required)
    Returns:    JSON { message }
    Status:     200, 400, 403, 404
    """
    data = request.get_json(silent=True) or {}
    notes = data.get("technician_notes")
    if notes is None:
        return jsonify({"message": "technician_notes is required."}), 400

    booking = run_query(
        "SELECT * FROM service_bookings WHERE booking_id = %s",
        (booking_id,), fetch="one")
    if not booking:
        return jsonify({"message": "Booking not found."}), 404

    user_id = session["user"]
    if booking["assigned_to"] != user_id:
        # Admins may also update
        user_role = run_query(
            "SELECT role FROM users WHERE user_id = %s",
            (user_id,), fetch="one")
        if not user_role or user_role["role"] not in ("admin", "service_advisor"):
            return jsonify({"message": "Not authorized to update notes for this booking."}), 403

    run_query(
        "UPDATE service_bookings SET technician_notes = %s WHERE booking_id = %s",
        (notes, booking_id))

    audit_log(session["user"], "PUT technician_notes",
              "service_bookings", booking_id)
    return jsonify({"message": "Technician notes updated."}), 200


# --- ESTIMATE & INTAKE FLOW ---


def assignAndOpenIntakeHandler(booking_id):
    """
    Self-assign a booking and immediately open intake (set status to draft_estimate).
    Only unassigned bookings in 'confirmed' status may be opened.
    Path param: booking_id
    Returns:    JSON { message }
    Status:     200, 404, 409
    """
    user_id = session["user"]
    conn, cursor = get_db()
    try:
        cursor.execute(
            "SELECT * FROM service_bookings WHERE booking_id = %s FOR UPDATE",
            (booking_id,))
        booking = cursor.fetchone()

        if not booking:
            return jsonify({"message": "Booking not found."}), 404

        if booking["assigned_to"] is not None:
            return jsonify({"message": "Booking is already assigned."}), 409

        if booking["status"] not in ("confirmed", "pending"):
            return jsonify({"message": "Only pending or confirmed bookings can be opened."}), 409

        cursor.execute(
            "UPDATE service_bookings SET assigned_to = %s, status = 'draft_estimate' WHERE booking_id = %s",
            (user_id, booking_id))
        conn.commit()

        audit_log(session["user"], "PUT assign-and-open-intake",
                  "service_bookings", booking_id, conn=conn, cursor=cursor)
        return jsonify({"message": "Booking assigned and intake opened.", "booking_id": booking_id}), 200

    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def createEstimateHandler(booking_id):
    """
    Save or update the estimate_data JSON for a booking.
    Only allowed when status is 'draft_estimate'.
    Path param: booking_id
    Body:       estimate_data (object, required) — { parts: [...], labor: [...], misc: [...], subtotal, tax, total }
    Returns:    JSON { message }
    Status:     200, 400, 403, 404
    """
    data = request.get_json(silent=True) or {}
    estimate_data = data.get("estimate_data")
    if not estimate_data:
        return jsonify({"message": "estimate_data is required."}), 400

    booking = run_query(
        "SELECT * FROM service_bookings WHERE booking_id = %s",
        (booking_id,), fetch="one")
    if not booking:
        return jsonify({"message": "Booking not found."}), 404

    if booking["status"] != "draft_estimate":
        return jsonify({"message": "Estimate can only be edited in draft_estimate status."}), 403

    run_query(
        "UPDATE service_bookings SET estimate_data = %s WHERE booking_id = %s",
        (json.dumps(estimate_data), booking_id))

    audit_log(session["user"], "PUT estimate", "service_bookings", booking_id)
    return jsonify({"message": "Estimate saved."}), 200


def transmitEstimateHandler(booking_id):
    """
    Lock the estimate and set status to 'awaiting_signature'.
    The booking's estimate_data must already exist.
    Path param: booking_id
    Returns:    JSON { message }
    Status:     200, 400, 404, 409
    """
    booking = run_query(
        "SELECT * FROM service_bookings WHERE booking_id = %s",
        (booking_id,), fetch="one")
    if not booking:
        return jsonify({"message": "Booking not found."}), 404

    if booking["status"] != "draft_estimate":
        return jsonify({"message": "Only draft estimates can be transmitted."}), 409

    if not booking.get("estimate_data"):
        return jsonify({"message": "No estimate data to transmit. Save an estimate first."}), 400

    run_query(
        "UPDATE service_bookings SET status = 'awaiting_signature' WHERE booking_id = %s",
        (booking_id,))

    fire_notif(booking["customer_id"], "Estimate Ready for Signature",
               "Your service estimate is ready. Please review and sign digitally.",
               "in_app", "service_bookings", booking_id)

    audit_log(session["user"], "PUT transmit-estimate",
              "service_bookings", booking_id)
    return jsonify({"message": "Estimate transmitted for signature."}), 200


def signEstimateHandler(booking_id):
    """
    Customer signs the estimate, setting status to 'in_progress'.
    Path param: booking_id
    Returns:    JSON { message }
    Status:     200, 404, 409
    """
    booking = run_query(
        "SELECT * FROM service_bookings WHERE booking_id = %s",
        (booking_id,), fetch="one")
    if not booking:
        return jsonify({"message": "Booking not found."}), 404

    if booking["status"] != "awaiting_signature":
        return jsonify({"message": "Only estimates awaiting signature can be signed."}), 409

    run_query(
        "UPDATE service_bookings SET status = 'in_progress' WHERE booking_id = %s",
        (booking_id,))

    audit_log(session["user"], "PUT sign-estimate",
              "service_bookings", booking_id)
    return jsonify({"message": "Estimate signed. Work is now in progress."}), 200


# --- WARRANTY CLAIMS ---

WARRANTY_TRANSITIONS = {
    "submitted":    ["under_review"],
    "under_review": ["approved", "rejected"],
    "approved":     ["resolved"],
    "rejected":     [],
    "resolved":     [],
}


def submitWarrantyClaimHandler():
    """
    Submit a new warranty claim. Verifies sale belongs to current user.
    Prevents duplicate active claims on the same (sale_id, vehicle_id).
    Body:       vehicle_id (required), sale_id (required), claim_type (required, enum),
                description (required, max 1000 chars)
    Returns:    JSON { message, claim_id }
    Status:     201, 400, 403 (sale not owned), 409 (duplicate), 422
    """
    data = request.get_json()
    user_id = session["user"]
    vehicle_id = data.get("vehicle_id")
    sale_id = data.get("sale_id")
    claim_type = data.get("claim_type")
    description = data.get("description")

    if not vehicle_id or not sale_id or not claim_type or not description:
        return jsonify({"message": "vehicle_id, sale_id, claim_type, and description are required."}), 400

    if claim_type not in ("repair", "replacement", "refund"):
        return jsonify({"message": "claim_type must be repair, replacement, or refund."}), 422

    if len(description) > 1000:
        return jsonify({"message": "description must be 1000 characters or fewer."}), 422

    sale = run_query("""
        SELECT sale_id FROM sales
        WHERE sale_id = %s AND customer_id = %s
    """, (sale_id, user_id), fetch="one")

    if not sale:
        return jsonify({"message": "Sale not found or does not belong to you."}), 403

    existing = run_query("""
        SELECT claim_id FROM warranty_claims
        WHERE sale_id = %s AND vehicle_id = %s AND status IN ('submitted', 'under_review')
        LIMIT 1
    """, (sale_id, vehicle_id), fetch="one")

    if existing:
        return jsonify({
            "message": "An active claim already exists for this vehicle on this sale."
        }), 409

    claim_id = run_query("""
        INSERT INTO warranty_claims
        (vehicle_id, sale_id, claim_type, description, status)
        VALUES (%s, %s, %s, %s, %s)
    """, (vehicle_id, sale_id, claim_type, description, "submitted"))

    audit_log(session["user"], "POST", "warranty_claims", claim_id)
    return jsonify({"message": "Claim submitted!", "claim_id": claim_id}), 201


def listWarrantyClaimsHandler():
    """
    List current customer's warranty claims (auto-filtered by session via sales JOIN).
    Returns:    JSON { data: [{ claim_id, sale_id, claim_type, status, brand, model, ... }] }
    Status:     200
    """
    user_id = session["user"]

    claims = run_query("""
        SELECT w.*, v.brand, v.model, v.year
        FROM warranty_claims w
        JOIN sales s ON w.sale_id = s.sale_id
        JOIN vehicles v ON w.vehicle_id = v.vehicle_id
        WHERE s.customer_id = %s
        ORDER BY w.submitted_at DESC
    """, (user_id,), fetch="all")

    return jsonify({"data": claims}), 200


def listAllWarrantyClaimsHandler():
    """
    List all warranty claims (admin). JOINs customer, reviewer, vehicle.
    Filter (query string): ?status=submitted|under_review|approved|rejected|resolved
    Returns:    JSON { data: [{ claim_id, customer_name, reviewer_name, status, brand, model, ... }] }
    Status:     200
    """
    status = request.args.get("status")

    conditions = []
    params = []

    if status:
        conditions.append("w.status = %s")
        params.append(status)

    where = (" WHERE " + " AND ".join(conditions)) if conditions else ""

    claims = run_query(f"""
        SELECT w.*, v.brand, v.model, v.year,
               u.username AS customer_name,
               r.username AS reviewer_name
        FROM warranty_claims w
        JOIN sales s ON w.sale_id = s.sale_id
        JOIN vehicles v ON w.vehicle_id = v.vehicle_id
        JOIN users u ON s.customer_id = u.user_id
        LEFT JOIN users r ON w.reviewed_by = r.user_id
        {where}
        ORDER BY w.submitted_at DESC
    """, params, fetch="all")

    return jsonify({"data": claims}), 200


def getWarrantyClaimDetailHandler(claim_id):
    """
    Get warranty claim detail with linked service bookings.
    Path param: claim_id
    Returns:    JSON { data: { claim_id, ..., service_bookings: [...] } }
    Status:     200, 404
    """
    claim = run_query("""
        SELECT w.*, v.brand, v.model, v.year,
               u.username AS customer_name,
               r.username AS reviewer_name
        FROM warranty_claims w
        JOIN sales s ON w.sale_id = s.sale_id
        JOIN vehicles v ON w.vehicle_id = v.vehicle_id
        JOIN users u ON s.customer_id = u.user_id
        LEFT JOIN users r ON w.reviewed_by = r.user_id
        WHERE w.claim_id = %s
    """, (claim_id,), fetch="one")

    if not claim:
        return jsonify({"message": "Claim not found."}), 404

    bookings = run_query("""
        SELECT b.*, s.slot_datetime, s.slot_type
        FROM service_bookings b
        JOIN service_slots s ON b.slot_id = s.slot_id
        WHERE b.warranty_claim_id = %s
    """, (claim_id,), fetch="all")

    claim["service_bookings"] = bookings
    return jsonify({"data": claim}), 200


def updateWarrantyStatusHandler(claim_id, new_status):
    """
    Transition warranty status through the DAG. Uses FOR UPDATE + lock timeout handling (503).
    Notifies customer on approve/reject/resolve. Sets reviewed_by + resolved_at where applicable.
    Path param: claim_id
    Action:     "under_review" | "approved" | "rejected" | "resolved" (passed from route)
    Body:       resolution_text (required only for reject)
    Returns:    JSON { message }
    Status:     200, 400, 404, 409 (invalid transition), 503
    """
    if new_status not in ["under_review", "approved", "rejected", "resolved"]:
        return jsonify({"message": "Invalid status."}), 400

    data = request.get_json()
    resolution = data.get("resolution_text")

    if new_status == "rejected" and not resolution:
        return jsonify({"message": "Resolution note is required when rejecting a claim."}), 400

    conn, cursor = get_db()
    try:
        cursor.execute("""
            SELECT w.*, s.customer_id
            FROM warranty_claims w
            JOIN sales s ON w.sale_id = s.sale_id
            WHERE w.claim_id = %s FOR UPDATE
        """, (claim_id,))
        claim = cursor.fetchone()

        if not claim:
            return jsonify({"message": "Claim not found."}), 404

        if new_status not in WARRANTY_TRANSITIONS.get(claim["status"], []):
            return jsonify({
                "message": f"Invalid transition: {claim['status']} -> {new_status}"
            }), 409

        update_fields = ["status = %s"]
        update_params = [new_status]

        if new_status in ("under_review", "approved", "rejected"):
            update_fields.append("reviewed_by = %s")
            update_params.append(session["user"])

        if new_status == "rejected":
            update_fields.append("resolution = %s")
            update_params.append(resolution)

        if new_status == "resolved":
            update_fields.append("resolved_at = %s")
            update_params.append(datetime.now())

        update_params.append(claim_id)
        cursor.execute(
            f"UPDATE warranty_claims SET {', '.join(update_fields)} WHERE claim_id = %s",
            update_params)

        conn.commit()

        if new_status == "approved":
            fire_notif(claim["customer_id"], "Warranty Approved",
                       "Your warranty claim has been approved.", "in_app",
                       "warranty_claims", claim_id)

        if new_status == "rejected":
            fire_notif(claim["customer_id"], "Warranty Rejected",
                       f"Your warranty claim was rejected: {resolution}", "in_app",
                       "warranty_claims", claim_id)

        if new_status == "resolved":
            fire_notif(claim["customer_id"], "Warranty Resolved",
                       "Your warranty claim has been resolved.", "in_app",
                       "warranty_claims", claim_id)

        audit_log(session["user"], f"PUT status={new_status}",
                  "warranty_claims", claim_id, conn=conn, cursor=cursor,
                  old_value=json.dumps({"status": claim["status"]}, default=str),
                  new_value=json.dumps({"status": new_status}, default=str))

        return jsonify({"message": f"Claim status updated to {new_status}."}), 200

    except mysql.connector.errors.OperationalError as e:
        conn.rollback()
        if "Lock wait timeout" in str(e):
            return jsonify({"error": "Resource locked. Retry."}), 503
        raise
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
