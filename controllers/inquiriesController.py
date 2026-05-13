from conn import run_query
from flask import session, jsonify, request
from datetime import datetime
from utils.log import audit_log

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
    data = request.get_json()

    user_id = data.get("user_id") 
    agent_id = data.get("agent_id") 
    vehicle_id = data.get("vehicle_id") 
    guest_name = data.get("guest_name") 
    guest_email = data.get("guest_email")
    guest_number = data.get("guest_number") 
    message = data.get("message")
    
    required_fields = {
        "vehicle_id": vehicle_id,        
        "guest_email": guest_email,
        "message": message,
        "guest_number": guest_number,
        "guest_name": guest_name
    }
    
    for field_name, value in required_fields.items():
        if not value:
            return jsonify({"message": f"{field_name} is required."})
    res = run_query("""
                       INSERT INTO inquiries
                       (user_id, agent_id, vehicle_id, guest_name, guest_email, guest_number, message)
                       VALUES 
                       (%s,%s,%s,%s,%s,%s,%s)
                       """,
                       (user_id, agent_id,vehicle_id,guest_name, guest_email,guest_number, message))
    
    # always log the inquiry
    # audit_log(None, "POST", "inquiries", None, jsonify(res))
    
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
        return jsonify({"message": "no data found."})
    
    return jsonify({"data": res})
        

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
        return jsonify({"message": "no data found."})
    
    return jsonify({"data": res})

# update specific inquiry -> protected route
def update_inquiry(id):
    # agent can only update the resolved_at field
    
    resolved_at = datetime.now()

    res = run_query("""
                    UPDATE inquiries SET resolved_at = %s
                    WHERE inquiry_id = %s
                    """,
                    (resolved_at, id))
    
    if not res:
        return jsonify({"message": "action failed."})    

    return jsonify({"message": "marked as resolved!."})

# create a handler when the agent successfully assists the customer -> then the resolved_at = current time.


