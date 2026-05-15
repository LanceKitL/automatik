from flask import jsonify, request, session
from utils.log import audit_log
from conn import run_query
import json

# users
def get_user():
    result = run_query("""
                       SELECT 
                       users.username, users.email, users.is_active, users.last_login,
                       user_profile.*
                       FROM users JOIN user_profile ON users.user_id = user_profile.user_id
                       """, 
                       fetch="all")
    
    return jsonify({"data": result})

def get_user_with(id):
    users = run_query(""" 
                       SELECT users.username, users.email, users.is_active, users.last_login, users.role
                       FROM users 
                       WHERE user_id = %s 
                       """, 
                       (id, ), 
                       fetch="one")

    if not users:
        return jsonify({"message": "user not found."}), 404
    
    user_profile = run_query(""" 
                       SELECT * FROM user_profile
                       WHERE user_id = %s 
                       """, 
                       (id, ), 
                       fetch="one")

    users["user_profile"] = user_profile

    return jsonify({"data": users}), 200

def get_user_profile_with(id):
    result = run_query(""" 
                       SELECT * FROM user_profile 
                       WHERE user_id = %s 
                       """, 
                       (id, ), 
                       fetch="one")
    
    return jsonify({"data": result}), 200

def update_user_with(user_id):

    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    role = data.get("role")

    fields = {
        "username": username,
        "email": email,
        "role": role
    }

    updates = []
    params = []

    for field_name, value in fields.items():

        if value is not None:
            updates.append(f"{field_name} = %s")
            params.append(value)

    if not updates:
        return jsonify({
            "message": "No fields to update."
        }), 400

    # Get old user data
    old_value = run_query(
        "SELECT * FROM users WHERE user_id = %s",
        (user_id,),
        fetch="one"
    )

    if not old_value:
        return jsonify({
            "message": "User not found."
        }), 404

    # Check duplicate username/email
    duplicate = None
    if username or email:
        duplicate = run_query(
            """
            SELECT user_id
            FROM users
            WHERE (username = %s OR email = %s)
            AND user_id != %s
            """,
            (username, email, user_id),
            fetch="one"
        )

    if duplicate:
        return jsonify({
            "message": "Username or email already exists."
        }), 400

    params.append(user_id)

    sql = f"""
        UPDATE users
        SET {', '.join(updates)}
        WHERE user_id = %s
    """

    run_query(sql, params)

    # Get updated data
    new_value = run_query(
        "SELECT * FROM users WHERE user_id = %s",
        (user_id,),
        fetch="one"
    )

    # Audit log
    audit_log(
        id=session["user"],
        action="PUT",
        tablename="users",
        record_id=user_id,
        old_value=json.dumps(old_value, default=str),
        new_value=json.dumps(new_value, default=str),
    )

    return jsonify({
        "message": "Update successful!",
        "updated_fields": [k for k, v in fields.items() if v is not None]
    }), 200

def delete_user_with(user_id):
    if user_id is None:
        return jsonify({"message": f"user with id{user_id} not found."}),400

    res = run_query("DELETE FROM users WHERE user_id = %s", (user_id, ))

    if not res:
        return jsonify({"message": f"user {user_id} not found."}), 404

    return jsonify({"message": f"user {user_id} deleted successfully!"}), 200

#agents
def get_agents():
    result = run_query(""" 
                       SELECT users.username, users.role, agent_details.employee_number, 
                       agent_details.hire_date 
                       FROM users 
                       INNER JOIN agent_details ON users.user_id = agent_details.user_id
                       WHERE users.is_active = 1 
                       """,
                       fetch="all")
    
    return jsonify({"data": result})

def update_commission_rate(agent_id):
    """
    [ADMIN ONLY]
    Update hire_date and/or commission rate of an agent.
    """

    # Check if agent exists
    existing = run_query(
        "SELECT * FROM agent_details WHERE user_id = %s",
        (agent_id,),
        fetch="one"
    )

    if not existing:
        return jsonify({
            "message": f"agent with id [{agent_id}] does not exist."
        }), 400

    data = request.get_json()

    hire_date = data.get("hire_date")
    default_commission_rate = data.get("default_commission_rate")

    allowed_fields = {
        "hire_date": hire_date,
        "default_commission_rate": default_commission_rate
    }

    update_fields = []
    params = []
    # Save old values
    old_value = {
        "hire_date": existing.get("hire_date"),
        "default_commission_rate": existing.get("default_commission_rate")
    }

    # Save new values
    new_value = {}

    for field_name, value in allowed_fields.items():

        # IMPORTANT:
        # allow 0 or 0.0 values
        if value is not None:
            update_fields.append(f"{field_name} = %s")
            params.append(value)

            new_value[field_name] = value

    if not update_fields:
        return jsonify({
            "message": "No fields provided."
        }), 400

    params.append(agent_id)

    query = f"""
        UPDATE agent_details
        SET {', '.join(update_fields)}
        WHERE user_id = %s
    """

    # Execute update
    run_query(query, params)

    # Audit log
    audit_log(
        id=session["user"],
        action="PUT",
        tablename="agent_details",
        record_id=agent_id,
        old_value=json.dumps(old_value, default=str),
        new_value=json.dumps(new_value, default=str)
    )

    return jsonify({
        "message": "Updated successfully!",
        "updated_fields": list(new_value.keys())
    }), 200


#customer
def get_customers():
    customer = run_query("""
                         SELECT * FROM customer_details 
                         JOIN users ON customer_details.user_id = users.user_id
                         JOIN user_profile ON customer_details.user_id = user_profile.user_id 
                         """,
                         fetch="all")
    
    return jsonify({"data": customer})

def get_customer_with(customer_id):
    customer = run_query("""
                         SELECT * FROM customer_details 
                         JOIN users ON customer_details.user_id = users.user_id
                         JOIN user_profile ON customer_details.user_id = user_profile.user_id 
                         WHERE customer_details.user_id = %s
                         """,
                         (customer_id, ),
                         fetch="one")
    
    if not customer:
        return jsonify({"message": f"customer with id[{customer_id}] not found."})

    
    return jsonify({"data": customer}), 200

def update_customer_with(customer_id):
    """
    [ADMIN ONLY]
    Update specific customer_details fields.
    """
    data = request.get_json()

    preferred_contact_method = data.get("preferred_contact_method") # email | sms |whatsapp
    preferred_payment_method = data.get("preferred_payment_method") # cash | installment | bank_transfer
    notes = data.get("notes")

    allowed_fields = {
        "preferred_contact_method": preferred_contact_method,
        "preferred_payment_method": preferred_payment_method,
        "notes": notes,
    }

    update_fields = []
    params = []
    selected_fields = []

    for field_name, value in allowed_fields.items():

        # allow empty string / 0 if needed
        if value is not None:
            selected_fields.append(field_name)
            update_fields.append(f"{field_name} = %s")
            params.append(value)

    if not update_fields:
        return jsonify({
            "message": "No fields to update."
        }), 400

    # Check if customer exists
    customer = run_query(
        f"""
        SELECT {', '.join(selected_fields)}
        FROM customer_details
        WHERE user_id = %s
        """,
        (customer_id,),
        fetch="one"
    )

    if not customer:
        return jsonify({
            "message": "Customer not found."
        }), 404

    old_value = customer

    # Update
    params.append(customer_id)

    query = f"""
        UPDATE customer_details
        SET {', '.join(update_fields)}
        WHERE user_id = %s
    """

    run_query(query, params)

    # Get updated values
    new_value = run_query(
        f"""
        SELECT {', '.join(selected_fields)}
        FROM customer_details
        WHERE user_id = %s
        """,
        (customer_id,),
        fetch="one"
    )

    # Audit log
    audit_log(
        id=session["user"],
        action="PUT",
        tablename="customer_details",
        record_id=customer_id,
        old_value=json.dumps(old_value, default=str),
        new_value=json.dumps(new_value, default=str),
    )

    return jsonify({
        "message": "Customer updated successfully!",
        "updated_fields": selected_fields
    }), 200
