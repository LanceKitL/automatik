from conn import run_query
from flask import session, jsonify, request
from datetime import datetime
from utils.log import audit_log
from utils.notification import fire_notif, brodcast_notif
from services.mail_service import inquiry_received
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

#public
# this function is for customer/guest user, this will run whenever they want to 
# submit an inquiry
def submitInquiry(): # -> POST
    """
        this function will send an inquiry to the system.
        if guest: require guest_name, guest_email.
    """
    if session.get("role") == "agent" or session.get("role") == "admin":
        return jsonify({
            "message": "Forbidden Access."
        }), 403  # 403 Forbidden is correct for role-based access denial
    # important questions to answer before proceeding
    # kailan nagkakaron ng inquiry?
    # -> kapag si potential customer or existing customer is may purchase intent, gusto mag test drive
    
    # 1. check first if the current user is logged in
    user = session.get("user")
    data = request.get_json()
    message = data.get("message")
    vehicle_id = data.get("vehicle_id")
    
    if not message:
        return jsonify({
            "message": "Inquiry message is required."
            }), 400
    
    if not vehicle_id:
        return jsonify({
            "message": "vehicle id is required."
            }), 400
    
    if user is not None: # if the inquiry comes from existing customer
        res = run_query("""
                  INSERT INTO inquiries 
                  (user_id, vehicle_id, message, status)
                  VALUES
                  (%s,%s,%s,%s)
                  """,
                  (user,vehicle_id,message,'open'))
        
        audit_log(
            id=res["user_id"], 
            action="POST", 
            tablename="inquiries", 
            record_id=res
            )

        fire_notif(
            user_id=user,
            title="Inquiry Submitted",
            message="Your inquiry has been received. An agent will follow up shortly.",
            channel="in_app",
            ref_type="inquiries",
            ref_id=res
        )

        return jsonify({"message": "Inquiry sent successfully!"}), 200
    else: # if inquiry comes from a guest
        # these fields are required
        name = data.get("name")
        email = data.get("email")
        number = data.get("number")
        
        if not name or not email:
            return jsonify({"message": "please provide your name and email."}), 400

        # kapag may laman edi go except no user_id here 
        res = run_query("""
                    INSERT INTO inquiries 
                    (vehicle_id,guest_name,guest_email,guest_number, message, status)
                    VALUES
                    (%s,%s,%s,%s,%s,%s)
                    """,
                    (vehicle_id,name,email,number,message,'open'))
        
        if not res:
            return jsonify({"message": "sending inquiry failed."}),400
        
        audit_log(
            id=None,
            action="POST", 
            tablename="inquiries", 
            record_id=res,
            new_value=json.dumps({
                "guest_name": name,
                "guest_email": email,
                "guest_number": number,
                },  
                default=str)
            )
        
        # send an email
        inquiry_received(email)
        
        return jsonify({"message": "Inquiry sent successfully!"}), 200


#customer
def indexCustomerInquiries():
    """
        CUSTOMER PORTAL
        
        - this function returns current customers inquiries.
    """
    customer_id = session["user"]
    
    res = run_query("""
                    SELECT * FROM inquiries 
                    JOIN vehicles ON inquiries.vehicle_id = vehicles.vehicle_id
                    WHERE inquiries.user_id = %s
                    """,
                    (customer_id,),
                    fetch="all")
    
    if not res:
        return jsonify({"message": "customer not found."}), 404
    
    formatted_data = []
    
    for row in res:
        formatted_data.append({
            "inquiry_id": row["inquiry_id"],
            "agent_assigned": row["agent_id"],
            "message": row["message"],
            "status": row["status"],
            "resolved_at": row["resolved_at"],
            "vehicle": {
                "model": row["model"],
                "brand": row["brand"],
                "color": row["color"],
                "body_type": row["body_type"],
                "price": row["price"],
            }
        })
    
    return jsonify(formatted_data), 200        


#admin
def assignInquiry(inquiry_id):
    """
    ADMIN PORTAL

    Admin assigns an open inquiry to a specific agent.
    Requires 'agent_id' in the request body.

    Sends:
        - In-app notification to the assigned agent
        - Email notification to the guest/customer
    """
    if inquiry_id is None:
        return jsonify({"message": "inquiry_id is required."}), 400

    data = request.get_json(silent=True) or {}
    agent_id = data.get("agent_id")

    if not agent_id:
        return jsonify({"message": "agent_id is required in request body."}), 400

    # Validate the inquiry
    inquiry = run_query("SELECT * FROM inquiries WHERE inquiry_id = %s",
                        (inquiry_id,), fetch="one")
    if not inquiry:
        return jsonify({"message": "Inquiry not found."}), 404

    if inquiry["status"] != "open":
        return jsonify({"message": f"Inquiry is already '{inquiry['status']}'. Only 'open' inquiries can be assigned."}), 400

    if inquiry.get("agent_id"):
        return jsonify({"message": "Inquiry already has an agent assigned."}), 409

    # Validate the target agent
    agent_user = run_query("SELECT * FROM users WHERE user_id = %s AND role = 'agent'",
                           (agent_id,), fetch="one")
    if not agent_user:
        return jsonify({"message": "Agent not found."}), 404

    agent_details = run_query("SELECT * FROM agent_details WHERE user_id = %s",
                              (agent_id,), fetch="one")
    agent_label = agent_details["employee_number"] if agent_details else f"Agent #{agent_id}"

    old_value = inquiry["status"]

    # Assign
    run_query("""
        UPDATE inquiries SET agent_id = %s, status = 'assigned'
        WHERE inquiry_id = %s
    """, (agent_id, inquiry_id))

    new_value = {"agent_id": agent_id, "status": "assigned"}

    audit_log(
        session["user"],
        "PUT",
        "inquiries",
        inquiry_id,
        json.dumps(old_value, default=str),
        json.dumps(new_value, default=str)
    )

    # ── In-app notification to the assigned agent ──
    fire_notif(
        user_id=agent_id,
        title="New Inquiry Assigned",
        message=f"Inquiry #{inquiry_id} has been assigned to you. Please follow up with the customer.",
        channel="in_app",
        ref_type="inquiries",
        ref_id=inquiry_id
    )

    # ── In-app + Email notification to the customer/guest ──
    customer_name = inquiry.get("guest_name") or "Customer"
    customer_email = inquiry.get("guest_email")

    if inquiry.get("user_id"):
        # Existing customer — in-app
        fire_notif(
            user_id=inquiry["user_id"],
            title="Inquiry Assigned",
            message=f"Your inquiry #{inquiry_id} has been assigned to {agent_user['username']}. They will contact you soon.",
            channel="in_app",
            ref_type="inquiries",
            ref_id=inquiry_id
        )
        # Also fetch their email if not already available
        if not customer_email:
            user = run_query("SELECT email FROM users WHERE user_id = %s", (inquiry["user_id"],), fetch="one")
            customer_email = user["email"] if user else None

    if customer_email:
        try:
            from services.mail_service import inquiry_assigned
            inquiry_assigned(customer_email, customer_name, agent_user["username"], inquiry_id)
        except Exception:
            pass

    return jsonify({"message": "Inquiry assigned successfully!"}), 200

def resolveInquiry(inquiry_id):
    """
    AGENT PORTAL

    Marks an assigned inquiry as 'resolved'.
    Notifies the customer/guest via in-app and email.
    """
    if not inquiry_id:
        return jsonify({"message": "inquiry_id is required."}), 400

    # Only the assigned agent can resolve
    inquiry = run_query("""
        SELECT * FROM inquiries
        WHERE inquiry_id = %s AND agent_id = %s
    """, (inquiry_id, session["user"]), fetch="one")

    if not inquiry:
        return jsonify({"message": "Inquiry not found or not assigned to you."}), 404

    if inquiry["status"] == "resolved":
        return jsonify({"message": "Inquiry is already resolved."}), 400

    old_value = inquiry["status"]

    run_query("""
        UPDATE inquiries SET status = 'resolved', resolved_at = %s
        WHERE inquiry_id = %s
    """, (datetime.now(), inquiry_id))

    audit_log(
        session["user"],
        "PUT",
        "inquiries",
        inquiry_id,
        json.dumps(old_value, default=str),
        json.dumps({"status": "resolved"}, default=str)
    )

    # ── Notify customer/guest ──
    customer_name = inquiry.get("guest_name") or "Customer"
    customer_email = inquiry.get("guest_email")
    agent = run_query("SELECT username FROM users WHERE user_id = %s", (session["user"],), fetch="one")

    if inquiry.get("user_id"):
        fire_notif(
            user_id=inquiry["user_id"],
            title="Inquiry Resolved",
            message=f"Your inquiry #{inquiry_id} has been resolved by {agent['username'] if agent else 'your agent'}. Thank you!",
            channel="in_app",
            ref_type="inquiries",
            ref_id=inquiry_id
        )
        if not customer_email:
            user = run_query("SELECT email FROM users WHERE user_id = %s", (inquiry["user_id"],), fetch="one")
            customer_email = user["email"] if user else None

    if customer_email:
        try:
            from services.mail_service import mail
            from flask_mail import Message
            msg = Message(
                sender=("AutoMatik", "AutoMatik@services.com"),
                subject="Your Inquiry Has Been Resolved",
                recipients=[customer_email]
            )
            msg.body = f"Hi {customer_name},\n\nYour inquiry #{inquiry_id} has been marked as resolved by {agent['username'] if agent else 'your agent'}. If you have further questions, please submit a new inquiry.\n\nThank you for choosing AutoMatik!"
            mail.send(msg)
        except Exception:
            pass

    return jsonify({"message": "Inquiry resolved successfully."}), 200

# admin
def displayInquiries():
    """
    SALES AGENT | ADMIN PORTAL
    
        This function returns the inquiries based on the type of user ['admin','agent']
        
        admin can access the search and filter, and he can all see the inquiries,
        agent can only view inquiries with STATUS = 'open'.
    """
    conditions = []
    values = []
    role = session["role"]
    params = {
        "status": request.args.get("status"),
        "agent_id": request.args.get("agent_id")
    }

    if params.get("status"):
        conditions.append("i.status LIKE %s")
        values.append(f"%{params['status']}%")

    if params.get("agent_id"):
        conditions.append("i.agent_id = %s")
        values.append(params["agent_id"])

    search = ""

    if conditions:
        search = "WHERE " + " AND ".join(conditions)
    
    query = ""
    
    if role == "admin":
        query = f"""
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

            {search}
        """
    else:
        query = f"""
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

            WHERE i.status = 'open' OR (i.agent_id = %s AND i.status = 'assigned')
        """
        values.append(session["user"])
        

    res = run_query(query, tuple(values), fetch="all")

    if not res:
        return jsonify({"message": "No available tasks today, keep up the good work!"})

    formatted_response = []

    for row in res:

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

    return jsonify(formatted_response), 200

def closeInquiry(inquiry_id):
    """
        ADMIN PORTAL
        
        this function closes an inquiry.
    """
    
    if not inquiry_id:
        return jsonify({
            "message": "inquiry_id is required."
        }), 400
    
    res = run_query(
        """
            SELECT * FROM inquiries 
            WHERE inquiry_id = %s AND status = 'resolved'
        """,
        (inquiry_id,),
        fetch="one"
    )
    
    if not res:
        return jsonify({
            "message": "inquiry not found or not marked 'resolved'."
        }), 400
        
    # PASSED CHECKS
    
    # store the old value
    old_value = res["status"]
    
    # set inquiry status to 'closed'
    run_query("""
              UPDATE inquiries SET status = 'closed' 
              WHERE inquiry_id = %s 
              """,
              (inquiry_id,))
    
    audit_log(
        session["user"],
        "PUT",
        "inquiries",
        res["inquiry_id"],
        json.dumps(old_value, default=str),
        json.dumps({"status": "closed"}, default=str)
    )

    if res.get("user_id"):
        fire_notif(
            user_id=res["user_id"],
            title="Inquiry Closed",
            message="Your inquiry has been closed. If you need further assistance, please submit a new inquiry.",
            channel="in_app",
            ref_type="inquiries",
            ref_id=inquiry_id
        )
    
    return jsonify({
        "message": "inquiry marked as 'closed'."
    }), 200