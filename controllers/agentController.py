from flask import jsonify,request,session, abort
from datetime import datetime
from conn import run_query

# ---------- VARIABLES -----------
TASK_TYPES = ["follow_up", "appointment", "demo", "document_prep", "other"]
STATUS = ["pending", "in_progress", "done", "cancelled"]


def getDashboard():
  """
    This function returns the ff:
      - assigned_inquiries
      - pending_tasks
      - total_commissions
  """
  current_agent = session["user"]
  
  if not current_agent:
    return jsonify({
      "message": "agent not found"
    }), 404
  
  data = {}
  
  assigned_inquiries = run_query("""
                             SELECT * FROM inquiries 
                             WHERE agent_id = %s
                             """,
                             (current_agent,),
                             fetch="all")
  
  pending_tasks = run_query("""
                             SELECT * FROM agent_tasks
                             WHERE agent_id = %s
                             """,
                             (current_agent,),
                            fetch="all")
  
  total_commissions = run_query("""
      SELECT s.sale_id, s.selling_price,
             s.selling_price * (
               COALESCE(NULLIF(ad.default_commission_rate, 0),
                 (SELECT COALESCE(setting_value, 3.5) FROM system_settings WHERE setting_key = 'default_commission_rate'),
                 3.5
               ) * 0.01
             ) AS total_commission
      FROM sales s
      JOIN agent_details ad ON s.agent_id = ad.user_id
      WHERE ad.user_id = %s
  """, (current_agent,), fetch="all")

  commission_trend = run_query("""
      SELECT
          DATE_FORMAT(s.sale_date, '%Y-%m') as month,
          COALESCE(SUM(s.selling_price * (
            COALESCE(NULLIF(ad.default_commission_rate, 0),
              (SELECT COALESCE(setting_value, 3.5) FROM system_settings WHERE setting_key = 'default_commission_rate'),
              3.5
            ) * 0.01
          )), 0) as total_commission,
          COALESCE(SUM(s.selling_price), 0) as total_revenue
      FROM sales s
      JOIN agent_details ad ON s.agent_id = ad.user_id
      WHERE ad.user_id = %s
        AND s.sale_date >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
      GROUP BY month
      ORDER BY month ASC
  """, (current_agent,), fetch="all")

  data["inquiries"] = assigned_inquiries
  data["pending_tasks"] = pending_tasks
  data["commissions_and_sales"] = total_commissions
  data["commission_trend"] = commission_trend
  
  return jsonify({"data": data}), 200

def getTestDrives():
    status_filter = request.args.get("status", "upcoming")
    user_id = session["user"]

    status_conditions = {
        "upcoming": "AND b.status IN ('pending', 'confirmed')",
        "completed": "AND b.status = 'completed'",
        "cancelled": "AND b.status = 'cancelled'",
    }
    status_sql = status_conditions.get(status_filter, status_conditions["upcoming"])
    order = "ASC" if status_filter == "upcoming" else "DESC"

    bookings = run_query(f"""
        SELECT b.*, s.slot_datetime, s.slot_type,
               v.brand, v.model, v.year,
               u.username AS customer_name,
               a.username AS assigned_to_name
        FROM service_bookings b
        JOIN service_slots s ON b.slot_id = s.slot_id
        JOIN vehicles v ON b.vehicle_id = v.vehicle_id
        JOIN users u ON b.customer_id = u.user_id
        LEFT JOIN users a ON b.assigned_to = a.user_id
        WHERE b.booking_type = 'test_drive'
        {status_sql}
        ORDER BY s.slot_datetime {order}
    """, fetch="all")

    return jsonify({"data": bookings}), 200

def getInquiries():
  """
    Returns all the self-assigned inquiries made by the agent.
  """
  current_agent = session["user"]
  
  if not current_agent:
    return jsonify({
      "message": "agent not found"
    }), 404
  
  assigned_inquiries = run_query("""
                               SELECT
                                i.user_id,

                                CASE
                                    WHEN i.user_id IS NOT NULL THEN up.full_name
                                    ELSE i.guest_name
                                END AS name,

                                CASE
                                    WHEN i.user_id IS NOT NULL THEN up.phone_number
                                    ELSE i.guest_number
                                END AS contact_number,

                                CASE
                                    WHEN i.user_id IS NOT NULL THEN u.email
                                    ELSE i.guest_email
                                END AS email,

                                v.vehicle_id,
                                v.brand,
                                v.model,
                                v.price,

                                i.message,
                                i.status,
                                i.agent_id,
                                i.inquiry_id,
                                i.created_at

                                FROM inquiries i

                                JOIN vehicles v
                                    ON i.vehicle_id = v.vehicle_id

                                LEFT JOIN user_profile up
                                    ON i.user_id = up.user_id
                                
                                LEFT JOIN users u
                                    ON i.user_id = u.user_id

                                WHERE i.agent_id = %s
                            """,
                            (current_agent,),
                            fetch="all")
  
  formatted_response = []
  for row in assigned_inquiries:

    is_guest = row["user_id"] is None

    user_type = ""

    if is_guest:
        user_type = "guest"
    else:
        user_type = "customer"

    formatted_response.append({
        "inquiry_id": row["inquiry_id"],
        "message": row["message"],
        "status": row["status"],
        "agent_assigned": row["agent_id"],
        "user_type": user_type,
        "created_at": row["created_at"].isoformat() if hasattr(row["created_at"], "isoformat") else str(row["created_at"]),
        "contacts": {
            "name": row["name"],
            "email": row["email"],
            "number": row["contact_number"]
        },
        "vehicle": {
            "id": row["vehicle_id"],
            "brand": row["brand"],
            "model": row["model"],
            "price": f"₱{row['price']}"
        }
    })

  return jsonify({
    "data": formatted_response
  })
  
# ---------- TASKS -----------------  

def getTasks():

    current_agent = session["user"]

    status = request.args.get("status")
    task_type = request.args.get("task_type")

    if status and status not in STATUS:
        return jsonify({
            "message": "invalid status"
        }), 400

    if task_type and task_type not in TASK_TYPES:
        return jsonify({
            "message": "invalid task type"
        }), 400

    conditions = ["at.agent_id = %s"]
    params = [current_agent]

    if status:
        conditions.append("at.status = %s")
        params.append(status)

    if task_type:
        conditions.append("at.task_type = %s")
        params.append(task_type)

    where_clause = "WHERE " + " AND ".join(conditions)

    query = f"""
          SELECT
            at.task_id,
            at.title,
            at.task_type,
            at.status,
            at.due_date,
            at.notes,

            ad.employee_number,

            i.inquiry_id,
            i.message AS inquiry_message,
            i.status AS inquiry_status,

            CASE
                WHEN i.user_id IS NOT NULL THEN up.full_name
                ELSE i.guest_name
            END AS customer_name,

            CASE
                WHEN i.user_id IS NOT NULL THEN up.phone_number
                ELSE i.guest_number
            END AS contact_number,

            CASE
                WHEN i.user_id IS NOT NULL THEN u.email
                ELSE i.guest_email
            END AS email,

            v.vehicle_id,
            v.brand,
            v.model,
            v.price

        FROM agent_tasks at

        JOIN agent_details ad
            ON at.agent_id = ad.user_id

        LEFT JOIN inquiries i
            ON at.inquiry_id = i.inquiry_id

        LEFT JOIN user_profile up
            ON i.user_id = up.user_id

        LEFT JOIN users u
            ON i.user_id = u.user_id

        LEFT JOIN vehicles v
            ON i.vehicle_id = v.vehicle_id

        {where_clause}
        """
    rows = run_query(query, params,fetch="all")
    tasks = [] 

    for row in rows:
        task = {
            "task_id": row["task_id"],
            "title": row["title"],
            "task_type": row["task_type"],
            "status": row["status"],
            "due_date": row["due_date"],
            "notes": row["notes"],
            "employee_number": row["employee_number"]
        }

        if row["inquiry_id"]:
            task["inquiry"] = {
                "inquiry_id": row["inquiry_id"],
                "message": row["inquiry_message"],
                "status": row["inquiry_status"],
                "customer_name": row["customer_name"],
                "contact_number": row["contact_number"],
                "email": row["email"],
                "vehicle": {
                    "vehicle_id": row["vehicle_id"],
                    "brand": row["brand"],
                    "model": row["model"],
                    "price": row["price"]
                }
            }
        else:
            task["inquiry"] = None

        tasks.append(task)

    return jsonify({
        "data": tasks
    })
    
def createTask():
    data = request.get_json()

    current_agent = session["user"]
    if not current_agent:
        return jsonify({"message": "Unauthorized"}), 401

    inquiry_id = data.get("inquiry_id")
    notes = data.get("notes")

    required_fields = {
        "task_type": data.get("task_type"),
        "title": data.get("title"),
        "due_date": data.get("due_date"),
    }

    for field_name, value in required_fields.items():
        if not value:
            return jsonify({
                "message": f"{field_name} is required."
            }), 400

    # Optional: verify inquiry exists
    if inquiry_id:
        inquiry = run_query(
            "SELECT inquiry_id FROM inquiries WHERE inquiry_id = %s",
            (inquiry_id,),
            fetch="one"
        )

        if not inquiry:
            return jsonify({
                "message": "Inquiry not found."
            }), 404

    res = run_query("""
        INSERT INTO agent_tasks
        (
            agent_id,
            inquiry_id,
            task_type,
            title,
            due_date,
            status,
            notes,
            created_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """,
    (
        current_agent,
        inquiry_id,
        required_fields["task_type"],
        required_fields["title"],
        required_fields["due_date"],
        "pending",
        notes,
        datetime.now()
    ))

    if not res:
        return jsonify({
            "message": "Task insertion failed."
        }), 400

    return jsonify({
        "message": "Task added successfully!"
    }), 200
    
def updateTask(task_id):

    current_agent = session.get("user")

    if not current_agent:
        return jsonify({
            "message": "Unauthorized"
        }), 401

    task = run_query("""
        SELECT *
        FROM agent_tasks
        WHERE task_id = %s
        AND agent_id = %s
    """,
    (task_id, current_agent),
    fetch="one")

    if not task:
        return jsonify({
            "message": "task not found"
        }), 404

    data = request.get_json()

    status = data.get("status")
    task_type = data.get("task_type")

    if status and status not in STATUS:
        return jsonify({
            "message": "invalid status"
        }), 400

    if task_type and task_type not in TASK_TYPES:
        return jsonify({
            "message": "invalid task type"
        }), 400

    fields = {
        "notes": data.get("notes"),
        "status": status,
        "due_date": data.get("due_date"),
        "task_type": task_type
    }

    updates = []
    params = []

    for field, value in fields.items():
        if value is not None:
            updates.append(f"{field} = %s")
            params.append(value)

    if not updates:
        return jsonify({
            "message": "no fields to update or field is immutable."
        }), 400

    params.append(task_id)

    query = f"""
        UPDATE agent_tasks
        SET {", ".join(updates)}
        WHERE task_id = %s
    """

    run_query(query, params)

    return jsonify({
        "message": f"task [{task_id}] updated successfully"
    }), 200
    
def deleteTask(task_id):

    current_agent = session.get("user")

    if not current_agent:
        return jsonify({
            "message": "Unauthorized"
        }), 401

    if not task_id:
        return jsonify({
            "message": "task id is required"
        }), 400

    # Ensure task exists and belongs to current agent
    task = run_query("""
        SELECT task_id
        FROM agent_tasks
        WHERE task_id = %s
        AND agent_id = %s
    """,
    (task_id, current_agent),
    fetch="one")

    if not task:
        return jsonify({
            "message": "task not found"
        }), 404

    deleted = run_query("""
        DELETE FROM agent_tasks
        WHERE task_id = %s
        AND agent_id = %s
    """,
    (task_id, current_agent))

    if not deleted:
        return jsonify({
            "message": "failed to delete task"
        }), 400

    return jsonify({
        "message": f"task [{task_id}] deleted successfully"
    }), 200
    

# -------- ADMIN ROUTES -------- 
# -------- AGENT COMMISSIONS -------- 

def getCommissions():
    current_agent = session["user"]
    
    if not current_agent:
        abort(404)
    
    rows = run_query("""
        SELECT
            ac.commission_id,
            ac.sale_id,
            ac.rate_applied,
            ac.commission_amount,
            ac.is_paid,
            ac.paid_at,
            s.sale_date,
            s.status AS sale_status,
            s.selling_price,
            COALESCE(up.full_name, u.username) AS customer_name,
            v.brand,
            v.model
        FROM agent_commissions ac
        JOIN sales s ON ac.sale_id = s.sale_id
        JOIN vehicles v ON s.vehicle_id = v.vehicle_id
        LEFT JOIN users u ON s.customer_id = u.user_id
        LEFT JOIN user_profile up ON s.customer_id = up.user_id
        WHERE ac.agent_id = %s
        ORDER BY s.sale_date DESC
    """, (current_agent,), fetch="all")
    
    return jsonify({
        "data": rows
    }), 200
    
def getCommissionsAdmin():
    agent_id = request.args.get("agent_id")
    is_paid = request.args.get("is_paid")

    query = """
        SELECT ac.*, s.sale_date, s.selling_price,
               COALESCE(up.full_name, cu.username) AS customer_name,
               v.brand, v.model, v.year,
               ag.username AS agent_name
        FROM agent_commissions ac
        JOIN sales s ON ac.sale_id = s.sale_id
        JOIN vehicles v ON s.vehicle_id = v.vehicle_id
        JOIN users cu ON s.customer_id = cu.user_id
        LEFT JOIN user_profile up ON s.customer_id = up.user_id
        LEFT JOIN users ag ON ac.agent_id = ag.user_id
        WHERE 1=1
    """
    params = []

    if agent_id:
        query += " AND ac.agent_id = %s"
        params.append(agent_id)

    if is_paid is not None:
        if is_paid not in ("0", "1"):
            return jsonify({"error": "is_paid must be 0 or 1"}), 400

        query += " AND ac.is_paid = %s"
        params.append(int(is_paid))

    query += " ORDER BY s.sale_date DESC"
    commissions = run_query(query, tuple(params) if params else None, fetch="all")

    return jsonify(commissions), 200

def payCommission(commission_id):
    if not commission_id:
        return jsonify({
            "message": "commission_id has no value."
        }), 400

    # check if the commission is already paid and existing
    commission = run_query("""
        SELECT ac.*, s.status AS sale_status
        FROM agent_commissions ac
        JOIN sales s ON ac.sale_id = s.sale_id
        WHERE ac.commission_id = %s
    """, (commission_id,), fetch="one")
    
    if not commission:
        return jsonify({
            "message": "commission not found."
        }), 404
    
    if commission["is_paid"] == 1:
        return jsonify({
            "message": "commission already paid."
        }), 400
    
    if commission["sale_status"] not in ("active", "completed"):
        return jsonify({
            "message": "Cannot pay commission: sale must be active or completed."
        }), 400
    
    paid_at = datetime.now()
    
    run_query("""
              UPDATE agent_commissions
              SET is_paid = %s, paid_at = %s 
              """,
              (1,paid_at))
    
    return jsonify({
        "message": "commission status updated to 'paid'"
    }), 200
    
def agentPerformance(agent_id):
    if not agent_id:
        return jsonify({
            "message": "agent_id not found."
        }), 400

    stats = run_query(
        """
        SELECT
            COUNT(*) AS total_sales,
            COALESCE(SUM(commission_amount), 0) AS revenue,
            COALESCE(SUM(commission_id), 0) AS commission_total,
            COALESCE(AVG(rate_applied), 0) AS avg_rate
        FROM agent_commissions
        WHERE agent_id = %s
        """,
        (agent_id,),
        fetch="one"
    )

    return jsonify({
        "agent_id": agent_id,
        "total_sales": stats["total_sales"],
        "revenue": float(stats["revenue"]),
        "commission_total": float(stats["commission_total"]),
        "avg_rate": float(stats["avg_rate"])
    }), 200


def agentSubmitInquiry():
    """Agent creates an inquiry on behalf of a walk-in guest. Auto self-assigns."""
    agent_id = session["user"]
    data = request.get_json(silent=True) or {}

    vehicle_id = data.get("vehicle_id")
    message = data.get("message")
    guest_name = data.get("guest_name")
    guest_email = data.get("guest_email")
    guest_number = data.get("guest_number")

    if not all([vehicle_id, message, guest_name, guest_email]):
        return jsonify({"message": "vehicle_id, message, guest_name, and guest_email are required."}), 400

    inquiry_id = run_query("""
        INSERT INTO inquiries (vehicle_id, message, agent_id, status, guest_name, guest_email, guest_number)
        VALUES (%s, %s, %s, 'assigned', %s, %s, %s)
    """, (vehicle_id, message, agent_id, guest_name, guest_email, guest_number))

    if not inquiry_id:
        return jsonify({"message": "Failed to create inquiry."}), 500

    return jsonify({"message": "Inquiry created and assigned.", "inquiry_id": inquiry_id}), 201


def agentBookTestDrive():
    """Agent books a test drive for a walk-in guest (customer_id = NULL)."""
    agent_id = session["user"]
    data = request.get_json(silent=True) or {}

    slot_id = data.get("slot_id")
    vehicle_id = data.get("vehicle_id")
    guest_name = data.get("guest_name")
    guest_email = data.get("guest_email")

    if not all([slot_id, vehicle_id, guest_name, guest_email]):
        return jsonify({"message": "slot_id, vehicle_id, guest_name, and guest_email are required."}), 400

    from conn import get_db
    from utils.notification import broadcast_notif
    from services.mail_service import send_test_drive_confirmed
    import mysql.connector.errors

    conn, cursor = get_db()
    try:
        cursor.execute(
            "SELECT capacity, is_available FROM service_slots WHERE slot_id = %s FOR UPDATE",
            (slot_id,))
        slot = cursor.fetchone()

        if not slot or not slot["is_available"]:
            return jsonify({"message": "Slot is unavailable."}), 400

        cursor.execute(
            "SELECT COUNT(*) AS total FROM service_bookings WHERE slot_id = %s AND status != 'cancelled'",
            (slot_id,))
        current_bookings = cursor.fetchone()["total"]

        if current_bookings >= slot["capacity"]:
            return jsonify({"message": "Slot has reached its capacity."}), 409

        cursor.execute("""
            INSERT INTO service_bookings (customer_id, slot_id, vehicle_id, booking_type, status, notes)
            VALUES (NULL, %s, %s, 'test_drive', 'pending', %s)
        """, (slot_id, vehicle_id, f"Walk-in: {guest_name} <{guest_email}>"))
        booking_id = cursor.lastrowid

        if (current_bookings + 1) >= slot["capacity"]:
            cursor.execute(
                "UPDATE service_slots SET is_available = 0 WHERE slot_id = %s",
                (slot_id,))

        conn.commit()

        from utils.log import audit_log
        audit_log(agent_id, "POST", "service_bookings", booking_id, conn=conn, cursor=cursor)

        # Notify admin
        broadcast_notif(
            role="admin",
            title="New Walk-in Booking",
            message=f"Test drive booking #{booking_id} created for walk-in guest {guest_name}.",
            channel="in_app",
            ref_type="service_bookings",
            ref_id=booking_id,
        )

        # Send confirmation email
        try:
            slot_info = run_query(
                "SELECT slot_datetime FROM service_slots WHERE slot_id = %s",
                (slot_id,), fetch="one", conn=conn, cursor=cursor)
            vehicle_info = run_query(
                "SELECT CONCAT(brand, ' ', model) AS name FROM vehicles WHERE vehicle_id = %s",
                (vehicle_id,), fetch="one", conn=conn, cursor=cursor)

            if slot_info:
                from flask import copy_current_request_context
                import threading

                @copy_current_request_context
                def _send_test_drive():
                    send_test_drive_confirmed(
                        email=guest_email,
                        name=guest_name,
                        booking_id=booking_id,
                        date_time=slot_info["slot_datetime"].strftime("%A, %B %d, %Y at %I:%M %p"),
                        location="AutoMatik Dealership",
                        vehicle_name=vehicle_info["name"] if vehicle_info else "your selected vehicle"
                    )

                threading.Thread(target=_send_test_drive, daemon=True).start()
        except Exception:
            pass

        return jsonify({"message": "Test drive booked! Confirmation email sent.", "booking_id": booking_id}), 201

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