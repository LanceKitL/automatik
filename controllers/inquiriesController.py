from conn import run_query
from flask import session, jsonify, request
from datetime import datetime
from utils.log import audit_log
import json
# inquiry_id
# user_id
# agent_id
# vehicle_id
# guest_name
# guest_email
# guest_number
# message
# status
# created_at
# resolved_at

# POST 
def submit_inquiry():
    data = request.get_json(silent=True) or {}

    user_id = data.get("user_id")
    agent_id = data.get("agent_id")
    vehicle_id = data.get("vehicle_id") 
    guest_name = data.get("guest_name") 
    guest_email = data.get("guest_email")
    guest_number = data.get("guest_number") 
    message = data.get("message")

    role = session.get("role")
    session_user = session.get("user")

    if role == "agent":
        agent_id = session_user

    if agent_id is not None:
        agent = run_query(
            "SELECT user_id FROM users WHERE user_id = %s AND role = %s",
            (agent_id, "agent"),
            fetch="one"
        )
        if not agent:
            return jsonify({"message": "agent_id is invalid."}), 400

    if user_id is not None:
        user = run_query(
            "SELECT user_id FROM users WHERE user_id = %s",
            (user_id,),
            fetch="one"
        )
        if not user:
            return jsonify({"message": "user_id is invalid."}), 400
    
    required_fields = {
        "vehicle_id": vehicle_id,        
        "guest_email": guest_email,
        "message": message,
        "guest_number": guest_number,
        "guest_name": guest_name
    }
    
    for field_name, value in required_fields.items():
        if not value:
            return jsonify({"message": f"{field_name} is required."}), 400
    res = run_query("""
                       INSERT INTO inquiries
                       (user_id, agent_id, vehicle_id, guest_name, guest_email, guest_number, message)
                       VALUES 
                       (%s,%s,%s,%s,%s,%s,%s)
                       """,
                       (user_id, agent_id,vehicle_id,guest_name, guest_email,guest_number, message))
    
    # always log the inquiry
    audit_log(session["user"], "POST", "inquiries", res)
    
    # take aways: once the agent assigned the task on them, it should be logged.
    if not res: 
        return jsonify({"message": "inquiries not sent successfully!"} ), 400
    
    return jsonify({"message": "inquiries sent successfully!"}), 200

# GET -> logged in required, role_required("agent")
def get_inquiries():
    role = session["role"]
    res = None

    if role == "admin":
        res = run_query("""
                        SELECT * FROM inquiries
                        """,
                        fetch="all")
    else:
        res = run_query("""
                SELECT * FROM inquiries
                WHERE status = 'open'
                """,
                fetch="all")
    
    if not res:
        return jsonify({"data": []}), 200

    return jsonify({"data": res}), 200
        

# GET specific inquiry ->  logged in required, role_required("agent", "admin")
def get_inquiry_details(id):
    role = session["role"]
    res = None
    
    if role == "admin":
        res = run_query("""
                        SELECT * FROM inquiries 
                        WHERE inquiry_id = %s
                        """,
                        (id, ),
                        fetch="one")
    else:
        res = run_query("""
                SELECT * FROM inquiries 
                WHERE status = 'open' AND inquiry_id = %s
                """,
                (id, ),
                fetch="one")

    if not res:
        return jsonify({"message": "no data found."}), 404

    return jsonify({"data": res}), 200

# update specific inquiry -> protected route
def update_inquiry(id):
    # agent can only update their assigned inquiry
    role = session.get("role")
    session_user = session.get("user")

    if role == "agent":
        inquiry = run_query(
            """
            SELECT inquiry_id
            FROM inquiries
            WHERE inquiry_id = %s AND agent_id = %s
            """,
            (id, session_user),
            fetch="one"
        )
        if not inquiry:
            return jsonify({"message": "inquiry not found or access denied."}), 403

    existing = run_query(
        "SELECT inquiry_id FROM inquiries WHERE inquiry_id = %s",
        (id,),
        fetch="one"
    )
    if not existing:
        return jsonify({"message": "inquiry not found."}), 404

    resolved_at = datetime.now()

    res = run_query(
        """
        UPDATE inquiries
        SET resolved_at = %s, status = %s
        WHERE inquiry_id = %s
        """,
        (resolved_at, "resolved", id)
    )
    
    if not res:
        return jsonify({"message": "action failed."}), 400    

    return jsonify({"message": "marked as resolved."}), 200

# create a handler when the agent successfully assists the customer -> then the resolved_at = current time.


