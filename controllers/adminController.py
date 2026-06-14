import os
from flask import jsonify, request, session
from utils.log import audit_log
from conn import run_query
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import json

def adminDashboard():
    """Return aggregated stats for the admin dashboard."""
    total_users = run_query("SELECT COUNT(*) AS count FROM users", fetch="one")
    total_agents = run_query("SELECT COUNT(*) AS count FROM users WHERE role = 'agent'", fetch="one")
    total_customers = run_query("SELECT COUNT(*) AS count FROM users WHERE role = 'customer'", fetch="one")

    open_inquiries = run_query("SELECT COUNT(*) AS count FROM inquiries WHERE status = 'open'", fetch="one")

    total_revenue = run_query(
        """SELECT COALESCE(SUM(s.selling_price), 0) - COALESCE((
            SELECT SUM(commission_amount) FROM agent_commissions WHERE is_paid = 1
        ), 0) AS total FROM sales s""",
        fetch="one",
    )
    active_sales = run_query(
        "SELECT COUNT(*) AS count FROM sales WHERE status IN ('active', 'pending')",
        fetch="one",
    )

    recent_sales = run_query(
        """
        SELECT s.sale_id, s.selling_price, s.payment_type, s.sale_date, s.status,
               v.brand, v.model, v.year, u.username AS customer_name
        FROM sales s
        JOIN vehicles v ON s.vehicle_id = v.vehicle_id
        JOIN users u ON s.customer_id = u.user_id
        ORDER BY s.sale_date DESC LIMIT 5
        """,
        fetch="all",
    )

    recent_bookings = run_query(
        "SELECT * FROM service_bookings ORDER BY created_at DESC LIMIT 5",
        fetch="all",
    )
    recent_warranty = run_query(
        "SELECT * FROM warranty_claims ORDER BY submitted_at DESC LIMIT 5",
        fetch="all",
    )

    return jsonify({
        "data": {
            "stats": {
                "total_users": total_users["count"],
                "total_agents": total_agents["count"],
                "total_customers": total_customers["count"],
                "open_inquiries": open_inquiries["count"],
            },
            "total_revenue": total_revenue["total"],
            "active_sales": active_sales["count"],
            "recent_sales": recent_sales,
            "recent_bookings": recent_bookings,
            "recent_warranty_claims": recent_warranty,
        }
    }), 200

def adminVehicles():
    """Return all vehicles regardless of status (admin view)."""
    result = run_query("""
        SELECT v.*, s.company_name AS supplier_name
        FROM vehicles v
        LEFT JOIN suppliers s ON v.supplier_id = s.supplier_id
        ORDER BY v.created_at DESC
    """, fetch="all")
    return jsonify({"data": result})

def adminNotifications():
    """Return in-app notifications for the logged-in admin."""
    user_id = session["user"]
    result = run_query("""
        SELECT * FROM notifications
        WHERE user_id = %s AND channel = 'in_app'
        ORDER BY created_at DESC
    """, (user_id,), fetch="all")
    return jsonify({"data": result})

def adminAuditLogs():
    """Return all audit logs with optional filters."""
    user_id = request.args.get("user_id")
    table_name = request.args.get("table_name")
    action = request.args.get("action")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")

    query = """
        SELECT a.*, u.username
        FROM audit_logs a
        LEFT JOIN users u ON a.user_id = u.user_id
        WHERE 1=1
    """
    params = []

    if user_id:
        query += " AND a.user_id = %s"
        params.append(user_id)
    if table_name:
        query += " AND a.table_name = %s"
        params.append(table_name)
    if action:
        query += " AND a.action = %s"
        params.append(action)
    if date_from:
        query += " AND a.created_at >= %s"
        params.append(date_from)
    if date_to:
        query += " AND a.created_at <= %s"
        params.append(date_to)

    query += " ORDER BY a.created_at DESC"
    result = run_query(query, tuple(params) if params else None, fetch="all")
    return jsonify({"data": result})

# ── Inventory (combined vehicles / suppliers / supplies) ──────────────────

def adminInventory():
    """Return vehicles with photos, suppliers, supplies, and low-stock info for the combined inventory page."""
    # 1. Vehicles with supplier name
    vehicles = run_query("""
        SELECT v.*, s.company_name AS supplier_name
        FROM vehicles v
        LEFT JOIN suppliers s ON v.supplier_id = s.supplier_id
        ORDER BY v.created_at DESC
    """, fetch="all")

    # 2. Photos per vehicle (grouped)
    photos = run_query("""
        SELECT vehicle_id, photo_id, photo_url, sort_order
        FROM vehicle_photos
        ORDER BY vehicle_id, sort_order ASC
    """, fetch="all")

    photos_by_vehicle = {}
    for p in photos:
        photos_by_vehicle.setdefault(p["vehicle_id"], []).append(p)

    # Attach photos to each vehicle
    for v in vehicles:
        v["photos"] = photos_by_vehicle.get(v["vehicle_id"], [])

    # 3. Suppliers
    suppliers = run_query("""
        SELECT s.*,
               (SELECT COUNT(*) FROM vehicles v WHERE v.supplier_id = s.supplier_id) AS total_vehicles
        FROM suppliers s
        ORDER BY s.company_name ASC
    """, fetch="all")

    # 4. Supplies
    supplies = run_query("""
        SELECT su.*, sp.company_name
        FROM supplies su
        JOIN suppliers sp ON su.supplier_id = sp.supplier_id
        ORDER BY sp.company_name ASC, su.part_name ASC
    """, fetch="all")

    # 5. Low-stock threshold from system_settings
    threshold_setting = run_query(
        "SELECT setting_value FROM system_settings WHERE setting_key = 'low_stock_threshold'",
        fetch="one"
    )
    threshold = int(threshold_setting["setting_value"]) if threshold_setting else 5

    # 6. Compute low-stock brands (groups with available count < threshold)
    low_stock = run_query("""
        SELECT brand, model, COUNT(*) AS available_count
        FROM vehicles
        WHERE status = 'available'
        GROUP BY brand, model
        HAVING COUNT(*) < %s
    """, (threshold,), fetch="all")

    low_stock_keys = set()
    for ls in low_stock:
        low_stock_keys.add((ls["brand"], ls["model"]))

    # Mark vehicles that belong to low-stock groups
    for v in vehicles:
        v["is_low_stock"] = (v["brand"], v["model"]) in low_stock_keys

    return jsonify({
        "data": {
            "vehicles": vehicles,
            "suppliers": suppliers,
            "supplies": supplies,
            "low_stock_threshold": threshold,
        }
    }), 200


def uploadVehiclePhoto():
    """Handle vehicle photo file upload. Accepts multipart/form-data with file + vehicle_id."""
    if "file" not in request.files:
        return jsonify({"message": "No file provided."}), 400

    file = request.files["file"]
    vehicle_id = request.form.get("vehicle_id")

    if not file.filename:
        return jsonify({"message": "Empty file."}), 400

    if not vehicle_id:
        return jsonify({"message": "vehicle_id is required."}), 400

    # Verify vehicle exists
    vehicle = run_query(
        "SELECT vehicle_id FROM vehicles WHERE vehicle_id = %s",
        (vehicle_id,),
        fetch="one",
    )
    if not vehicle:
        return jsonify({"message": "Vehicle not found."}), 404

    # Ensure upload directory exists
    upload_dir = os.path.join("static", "uploads", "vehicles")
    os.makedirs(upload_dir, exist_ok=True)

    # Save file
    filename = secure_filename(file.filename)
    # Prefix with timestamp to avoid collisions
    unique_name = f"{int(__import__('time').time())}_{filename}"
    filepath = os.path.join(upload_dir, unique_name)
    file.save(filepath)

    photo_url = f"/static/uploads/vehicles/{unique_name}"

    # Create vehicle_photos record
    # Get next sort_order for this vehicle
    max_order = run_query(
        "SELECT COALESCE(MAX(sort_order), 0) + 1 AS next_order FROM vehicle_photos WHERE vehicle_id = %s",
        (vehicle_id,),
        fetch="one",
    )
    sort_order = max_order["next_order"] if max_order else 0

    run_query(
        "INSERT INTO vehicle_photos (vehicle_id, photo_url, sort_order) VALUES (%s, %s, %s)",
        (vehicle_id, photo_url, sort_order),
    )

    return jsonify({
        "message": "Photo uploaded successfully.",
        "photo_url": photo_url,
    }), 201


# users
def get_user():
    result = run_query("""
                       SELECT
                       users.user_id, users.username, users.email, users.role,
                       users.is_active, users.last_login,
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
    is_active = data.get("is_active")

    fields = {
        "username": username,
        "email": email,
        "role": role,
        "is_active": is_active,
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

def createUser():
    """Create a new user (admin, agent, or customer)."""
    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")
    full_name = data.get("full_name")

    if not all([username, email, password, role]):
        return jsonify({"message": "username, email, password, and role are required."}), 400

    if role not in ("admin", "agent", "customer", "service_staff", "service_advisor", "finance_staff"):
        return jsonify({"message": "role must be admin, agent, customer, service_staff, service_advisor, or finance_staff."}), 400

    # Check duplicate
    existing = run_query(
        "SELECT user_id FROM users WHERE username = %s OR email = %s",
        (username, email),
        fetch="one"
    )
    if existing:
        return jsonify({"message": "Username or email already exists."}), 400

    hashed_pw = generate_password_hash(password)
    user_id = run_query(
        "INSERT INTO users (username, email, role, hashed_password) VALUES (%s, %s, %s, %s)",
        (username, email, role, hashed_pw),
    )

    # Create user_profile
    run_query(
        "INSERT INTO user_profile (user_id, full_name) VALUES (%s, %s)",
        (user_id, full_name or username),
    )

    # Create role-specific details
    if role == "agent":
        emp_num = f"EMP-{user_id}"
        run_query(
            "INSERT INTO agent_details (user_id, employee_number) VALUES (%s, %s)",
            (user_id, emp_num),
        )
    elif role == "customer":
        cust_num = f"CUST-{user_id}"
        run_query(
            "INSERT INTO customer_details (user_id, customer_number) VALUES (%s, %s)",
            (user_id, cust_num),
        )

    return jsonify({
        "message": "User created successfully!",
        "user_id": user_id,
        "role": role,
    }), 201


def updateUserProfile(user_id):
    """Update user_profile fields for a user."""
    data = request.get_json()

    allowed_fields = {
        "full_name": data.get("full_name"),
        "phone_number": data.get("phone_number"),
        "address": data.get("address"),
        "city": data.get("city"),
        "province": data.get("province"),
        "zip_code": data.get("zip_code"),
        "date_of_birth": data.get("date_of_birth"),
        "gender": data.get("gender"),
    }

    updates = []
    params = []
    for field, value in allowed_fields.items():
        if value is not None:
            updates.append(f"{field} = %s")
            params.append(value)

    if not updates:
        return jsonify({"message": "No fields to update."}), 400

    # Check user exists
    existing = run_query(
        "SELECT user_id FROM user_profile WHERE user_id = %s",
        (user_id,),
        fetch="one"
    )
    if not existing:
        return jsonify({"message": "User profile not found."}), 404

    params.append(user_id)
    sql = f"UPDATE user_profile SET {', '.join(updates)} WHERE user_id = %s"
    run_query(sql, params)

    return jsonify({
        "message": "Profile updated successfully!",
        "updated_fields": [k for k, v in allowed_fields.items() if v is not None],
    }), 200


def getAgentDetail(agent_id):
    """Return agent details including total sales count."""
    agent = run_query("""
        SELECT
            u.user_id, u.username, u.email, u.is_active,
            a.employee_number, a.hire_date, a.default_commission_rate,
            p.full_name, p.phone_number
        FROM users u
        JOIN agent_details a ON u.user_id = a.user_id
        LEFT JOIN user_profile p ON u.user_id = p.user_id
        WHERE u.user_id = %s AND u.role = 'agent'
    """, (agent_id,), fetch="one")

    if not agent:
        return jsonify({"message": "Agent not found."}), 404

    # Total sales count
    sales_count = run_query(
        "SELECT COUNT(*) AS count FROM sales WHERE agent_id = %s",
        (agent_id,),
        fetch="one"
    )
    agent["total_sales"] = sales_count["count"] if sales_count else 0

    return jsonify({"data": agent}), 200


def getCustomerSalesHistory(customer_id):
    """Return sales history for a customer."""
    sales = run_query("""
        SELECT
            s.sale_id, s.selling_price, s.payment_type, s.sale_date, s.status,
            v.brand, v.model, v.year
        FROM sales s
        JOIN vehicles v ON s.vehicle_id = v.vehicle_id
        WHERE s.customer_id = %s
        ORDER BY s.sale_date DESC
    """, (customer_id,), fetch="all")

    return jsonify({"data": sales}), 200


#agents
def get_agents():
    result = run_query(""" 
                       SELECT users.user_id as _id, users.username, users.role, agent_details.employee_number, 
                       agent_details.hire_date 
                       FROM users 
                       INNER JOIN agent_details ON users.user_id = agent_details.user_id
                       WHERE users.role = 'agent'
                       """,
                       fetch="all")
    
    return jsonify({"data": result})

def update_commission_rate(agent_id):
    """
    [ADMIN ONLY]
    Update hire_date and/or commission rate of an agent.
    """
    # UPDATE -> old_value | new_value

    # Check if agent exists
    existing = run_query(
        "SELECT * FROM agent_details WHERE user_id = %s",
        (agent_id,),
        fetch="one"
    )
    
    if existing is None:
        return jsonify({
            "message": f"agent with id [{agent_id}] not found."
        }), 404

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
        "hire_date": existing.get("hire_date"), #or existing["hire_date"]
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
                         WHERE users.role = 'customer'
                         """,
                         fetch="all")
    
    return jsonify({"data": customer})

def get_customer_with(customer_id):
    customer = run_query("""
                         SELECT * FROM customer_details 
                         JOIN users ON customer_details.user_id = users.user_id
                         JOIN user_profile ON customer_details.user_id = user_profile.user_id 
                         WHERE customer_details.user_id = %s AND users.role = 'customer'
                         """,
                         (customer_id, ),
                         fetch="one")
    
    if not customer:
        return jsonify({"message": f"customer with id[{customer_id}] not found."}), 404

    
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
