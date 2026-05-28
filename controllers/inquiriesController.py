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

#public
# this function is for customer/guest user, this will run whenever they want to 
# submit an inquiry
def submitInquiry(): # -> POST
    """
        this function will send an inquiry to the system.
        if guest: require guest_name, guest_email.
    """
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
            user=user, 
            action="POST", 
            tablename="inquiries", 
            record_id=res
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
        
        return jsonify({"message": "Inquiry sent successfully!"}), 200


#customer
def indexCustomerInquiries():
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

# admin
def displayInquiries():
    conditions = []
    values = []

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

    res = run_query(query, tuple(values), fetch="all")

    if not res:
        return jsonify({"message": "No inquiries found."}), 404

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