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
<<<<<<< HEAD
            id=res["user_id"], 
            action="POST", 
            tablename="inquiries", 
            record_id=res
=======
            id=user,
            action="POST",
            tablename="inquiries",
            record_id=res,
            new_value=json.dumps({
                "user_id": user,
                "vehicle_id": vehicle_id,
                "message": message,
                "status": "open"
                },
                default=str)
>>>>>>> feature/web_socket
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


#agent
def assignInquiry(inquiry_id):
    """
    SALES AGENT PORTAL
    
    This function helps agent to self-assign themselves to a specific tasks.
    """
    # inquiries returned to agent dashboard is only status = 'open'
    # inquiry_id cannot be None
    # inquiry_id cannot have an existing agent_id
    current_agent_id = session["user"]
    
    if inquiry_id is None:
        return jsonify({
            "message": "inquiry_id cannot be empty."
        }), 400
    
    res = run_query("""
                    SELECT * FROM inquiries 
                    WHERE inquiry_id = %s
                    """, 
                    (inquiry_id,),
                    fetch="one")
    
    if res.get("agent_id"):
        return jsonify({
            "message": "task already taken."
        }),400
        
    old_value = res.get("status")
    
    run_query("""
              UPDATE inquiries SET agent_id = %s, status = %s
              WHERE inquiry_id = %s 
              """,
              (current_agent_id,'assigned',inquiry_id))
    
    new_value = {
        "agent_id": current_agent_id,
        "status": "assigned"
    }
    
    audit_log(
        current_agent_id,
        "PUT",
        "inquiries",
        res["inquiry_id"],
        json.dumps(old_value, default=str),
        json.dumps(new_value, default=str)
    )    

    # Fetch agent details for the notification message
    agent = run_query("SELECT * FROM agent_details WHERE user_id = %s", (current_agent_id,), fetch="one")
    # Use a fallback label if agent_details record is missing (guard against None crash)
    agent_label = agent["employee_number"] if agent else f"Agent #{current_agent_id}"
    # guest_name is NULL for logged-in users; fall back to user_id for the message
    customer_label = res.get("guest_name") or str(res.get("user_id", "Unknown"))
    brodcast_notif(
        role="admin",
        title="Inquiry Assigned",
        message=f"{agent_label} took inquiry #{inquiry_id} for {customer_label}",
        channel="in_app",
        ref_type="inquiries",
        ref_id=inquiry_id
    )

    return jsonify({
        "message": "task assigned successfully!"
    }), 200

def resolveInquiry(inquiry_id):
    """
    SALES AGENT PORTAL
    
        Marks specific inquiry as 'resolved'.
    """
    # check if inquiry is empty
    # SET status = 'resolved'
    # resolved_at = datetime.now()
    # only resolve at task if its assigned
    
    # first layer -> check if inquiry_id does not exists
    if not inquiry_id:
        return jsonify({
            "message": "inquiry does not exists. failed to update."
        }), 400
    
    # second layer -> check if inquiry_id exists in the database and if the task is assigned to the current agent.
    res = run_query("""
                    SELECT * FROM inquiries 
                    WHERE inquiry_id = %s AND agent_id = %s
                    """,
                    (inquiry_id,session["user"]),
                    fetch="one")

    agent_assigned_inquiries = run_query("""
                                         SELECT * FROM inquiries WHERE agent_id = %s AND status = 'assigned'
                                         """,
                                         (session["user"],),
                                         fetch="all")
    if not res:
        return jsonify({
            "message": "inquiry does not exists.",
        }), 400

    if res["status"] == "resolved":
        return jsonify({
            "message": "task already marked as resolved.",
            "available_tasks": agent_assigned_inquiries
        }), 400
    # if it does exist, get the old value
    old_value = res["status"]
        
    run_query("""
              UPDATE inquiries SET status = %s, resolved_at = %s
              WHERE inquiry_id = %s
              """,
              ('resolved',datetime.now(),inquiry_id))

    audit_log(
        session["user"],
        "PUT",
        "inquiries",
        res["inquiry_id"],
        json.dumps(old_value, default=str),
        json.dumps({"status": "resolved"}, default=str)
    )

    if res.get("user_id"):
        fire_notif(
            user_id=res["user_id"],
            title="Inquiry Resolved",
            message="Your inquiry has been marked as resolved. Thank you!",
            channel="in_app",
            ref_type="inquiries",
            ref_id=inquiry_id
        )

    return jsonify({
        "message": "task marked as resolved."
    })

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

            WHERE i.status = 'open'
        """
        

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