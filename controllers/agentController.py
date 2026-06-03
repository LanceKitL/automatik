from flask import jsonify,request,session
from datetime import datetime
from conn import run_query


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
                                 SELECT s.sale_id, s.selling_price, s.selling_price * (ad.default_commission_rate * 0.01) AS total_commission FROM sales s
                                 JOIN agent_details ad ON s.agent_id = ad.user_id
                                 WHERE ad.user_id = %s
                                """,
                                (current_agent,),
                                fetch="all")
  
  data["inquiries"] = assigned_inquiries
  data["pending_tasks"] = pending_tasks
  data["commissions_and_sales"] = total_commissions
  
  return jsonify({"data": data}), 200

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
                                i.inquiry_id

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
TASK_TYPES = ["follow_up", "appointment", "demo", "document_prep", "other"]
STATUS = ["pending", "in_progress", "done", "cancelled"]

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