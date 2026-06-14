from conn import run_query, get_db, Error
from flask import session, jsonify, request
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from utils.log import audit_log, get_local_ip
from utils.notification import fire_notif, broadcast_notif
from services.mail_service import inquiry_received, send_sale_confirmation, send_custom_email
from controllers.salesController import insert_agent_commission, generate_amortization_schedule, _create_customer_from_inquiry
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
            id=user, 
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
        try:
            from flask import copy_current_request_context
            import threading

            @copy_current_request_context
            def _send_inquiry_received():
                inquiry_received(email)

            threading.Thread(target=_send_inquiry_received, daemon=True).start()
        except Exception:
            pass
        
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
    
    formatted_data = []
    
    if res:
        for row in res:
            formatted_data.append({
                "inquiry_id": row["inquiry_id"],
                "agent_assigned": row["agent_id"],
                "message": row["message"],
                "status": row["status"],
                "created_at": row["created_at"].isoformat() if hasattr(row["created_at"], "isoformat") else str(row["created_at"]),
                "resolved_at": row["resolved_at"].isoformat() if row["resolved_at"] and hasattr(row["resolved_at"], "isoformat") else str(row["resolved_at"]) if row["resolved_at"] else None,
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
            from flask import copy_current_request_context
            import threading

            @copy_current_request_context
            def _send_inquiry_assigned():
                inquiry_assigned(customer_email, customer_name, agent_user["username"], inquiry_id)

            threading.Thread(target=_send_inquiry_assigned, daemon=True).start()
        except Exception:
            pass

    return jsonify({"message": "Inquiry assigned successfully!"}), 200

def selfAssignInquiry(inquiry_id):
    """
    AGENT PORTAL

    Agent self-assigns an open inquiry to themselves.
    No request body needed — agent_id comes from session.
    """
    if not inquiry_id:
        return jsonify({"message": "inquiry_id is required."}), 400

    inquiry = run_query("SELECT * FROM inquiries WHERE inquiry_id = %s",
                        (inquiry_id,), fetch="one")
    if not inquiry:
        return jsonify({"message": "Inquiry not found."}), 404

    if inquiry["status"] != "open":
        return jsonify({"message": f"Inquiry is already '{inquiry['status']}'. Only 'open' inquiries can be assigned."}), 400

    if inquiry.get("agent_id"):
        return jsonify({"message": "Inquiry already has an agent assigned."}), 409

    agent_id = session["user"]
    old_value = inquiry["status"]

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

    agent = run_query("SELECT username FROM users WHERE user_id = %s",
                      (agent_id,), fetch="one")

    broadcast_notif(
        role="admin",
        title="Inquiry Self-Assigned",
        message=f"Agent {agent['username'] if agent else agent_id} has self-assigned inquiry #{inquiry_id}.",
        channel="in_app",
        ref_type="inquiries",
        ref_id=inquiry_id
    )

    customer_name = inquiry.get("guest_name") or "Customer"
    customer_email = inquiry.get("guest_email")

    if inquiry.get("user_id"):
        fire_notif(
            user_id=inquiry["user_id"],
            title="Inquiry Assigned",
            message=f"Your inquiry #{inquiry_id} has been assigned to {agent['username'] if agent else 'an agent'}. They will contact you soon.",
            channel="in_app",
            ref_type="inquiries",
            ref_id=inquiry_id
        )
        if not customer_email:
            user = run_query("SELECT email FROM users WHERE user_id = %s",
                             (inquiry["user_id"],), fetch="one")
            customer_email = user["email"] if user else None

    if customer_email:
        try:
            from services.mail_service import inquiry_assigned
            from flask import copy_current_request_context
            import threading

            @copy_current_request_context
            def _send_inquiry_assigned():
                inquiry_assigned(customer_email, customer_name,
                                 agent["username"] if agent else "Agent", inquiry_id)

            threading.Thread(target=_send_inquiry_assigned, daemon=True).start()
        except Exception:
            pass

    return jsonify({"message": "Inquiry assigned to you successfully!"}), 200

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
            from flask import copy_current_request_context
            import threading
            msg = Message(
                sender=("AutoMatik", "AutoMatik@services.com"),
                subject="Your Inquiry Has Been Resolved",
                recipients=[customer_email]
            )
            msg.body = f"Hi {customer_name},\n\nYour inquiry #{inquiry_id} has been marked as resolved by {agent['username'] if agent else 'your agent'}. If you have further questions, please submit a new inquiry.\n\nThank you for choosing AutoMatik!"

            @copy_current_request_context
            def _send_resolve_email():
                mail.send(msg)

            threading.Thread(target=_send_resolve_email, daemon=True).start()
        except Exception:
            pass

    # ── Notify admin ──
    broadcast_notif(
        role="admin",
        title="Inquiry Resolved",
        message=f"Inquiry #{inquiry_id} has been resolved by {agent['username'] if agent else 'an agent'}.",
        channel="in_app",
        ref_type="inquiries",
        ref_id=inquiry_id
    )

    return jsonify({"message": "Inquiry resolved successfully."}), 200

def convertInquiryToSale(inquiry_id):
    """
    AGENT PORTAL

    Convert an assigned inquiry into a sale. Requires selling_price and
    payment_type. The agent, vehicle, and customer are resolved from
    the inquiry itself. Creates a sale, resolves the inquiry, and
    handles installment loan setup if applicable.
    """
    if not inquiry_id:
        return jsonify({"message": "inquiry_id is required."}), 400

    inquiry = run_query("""
        SELECT i.*, v.brand, v.model FROM inquiries i
        JOIN vehicles v ON i.vehicle_id = v.vehicle_id
        WHERE i.inquiry_id = %s AND i.agent_id = %s
    """, (inquiry_id, session["user"]), fetch="one")

    if not inquiry:
        return jsonify({"message": "Inquiry not found or not assigned to you."}), 404

    if inquiry["status"] != "assigned":
        return jsonify({"message": f"Inquiry is '{inquiry['status']}'; only 'assigned' inquiries can be converted."}), 400

    data = request.get_json(silent=True) or {}
    selling_price = data.get("selling_price")
    payment_type = data.get("payment_type")

    if not selling_price or not payment_type:
        return jsonify({"message": "selling_price and payment_type are required."}), 400

    if payment_type not in ("full_payment", "installment"):
        return jsonify({"message": "payment_type must be 'full_payment' or 'installment'."}), 400

    try:
        selling_price = float(selling_price)
    except (TypeError, ValueError):
        return jsonify({"message": "selling_price must be a number."}), 422
    if selling_price < 0:
        return jsonify({"message": "selling_price cannot be negative."}), 400

    conn, cursor = get_db()
    try:
        vehicle_id = inquiry["vehicle_id"]
        agent_id = session["user"]

        vehicle = run_query("SELECT * FROM vehicles WHERE vehicle_id = %s FOR UPDATE",
                            (vehicle_id,), fetch="one", conn=conn, cursor=cursor)
        if not vehicle:
            return jsonify({"message": "Vehicle not found."}), 404
        if vehicle["status"] not in ("available", "reserved"):
            return jsonify({"message": f"Vehicle status is '{vehicle['status']}'; cannot sell."}), 409

        temp_password = None
        _new_customer_ctx = None
        if inquiry.get("user_id"):
            customer = run_query("SELECT * FROM users WHERE user_id = %s AND role = 'customer'",
                                 (inquiry["user_id"],), fetch="one", conn=conn, cursor=cursor)
            if not customer:
                return jsonify({"message": "Linked inquiry user is not a customer."}), 400
            customer_id = customer["user_id"]
        else:
            if not inquiry.get("guest_name") or not inquiry.get("guest_email"):
                return jsonify({"message": "Inquiry has no guest data. Cannot create customer."}), 400
            new_user_id, temp_password, _new_customer_ctx = _create_customer_from_inquiry(inquiry, conn, cursor)
            customer = run_query("SELECT * FROM users WHERE user_id = %s",
                                 (new_user_id,), fetch="one", conn=conn, cursor=cursor)
            customer_id = new_user_id

        cursor.execute("""
            INSERT INTO sales (vehicle_id, customer_id, agent_id, selling_price, payment_type, status, inquiry_id)
            VALUES (%s, %s, %s, %s, %s, 'pending', %s)
        """, (vehicle_id, customer_id, agent_id, selling_price, payment_type, inquiry_id))
        sale_id = cursor.lastrowid

        cursor.execute("""
            UPDATE inquiries SET status = 'resolved', resolved_at = NOW(), user_id = %s
            WHERE inquiry_id = %s
        """, (customer_id, inquiry_id))

        insert_agent_commission(cursor, sale_id, agent_id, selling_price)
        cursor.execute("UPDATE vehicles SET status = 'reserved' WHERE vehicle_id = %s", (vehicle_id,))

        audit_log(session["user"], "POST", "sales", sale_id, None,
                  json.dumps({"vehicle_id": vehicle_id, "customer_id": customer_id,
                              "agent_id": agent_id, "payment_type": payment_type,
                              "selling_price": selling_price, "status": "pending",
                              "inquiry_id": inquiry_id}, default=str),
                  conn=conn, cursor=cursor)

        cursor.execute("INSERT INTO sales_contracts (sale_id, status) VALUES (%s, 'draft')", (sale_id,))

        if payment_type == "installment":
            term_months = data.get("term_months")
            interest_rate = data.get("interest_rate")
            loan_amount = data.get("loan_amount")
            down_payment = data.get("down_payment", 0)

            if not all([term_months, interest_rate, loan_amount]):
                return jsonify({"message": "term_months, interest_rate, and loan_amount are required for installment."}), 400

            try:
                term_months = int(term_months)
                interest_rate = float(interest_rate)
                loan_amount = float(loan_amount)
                down_payment = float(down_payment)
            except (TypeError, ValueError):
                return jsonify({"message": "term_months, interest_rate, loan_amount must be numbers."}), 422

            if loan_amount <= 0 or loan_amount > selling_price:
                return jsonify({"message": "loan_amount must be > 0 and <= selling_price."}), 422
            if term_months < 6 or term_months > 60:
                return jsonify({"message": "term_months must be between 6 and 60."}), 422
            if interest_rate < 0 or interest_rate > 30:
                return jsonify({"message": "interest_rate must be between 0 and 30."}), 422

            monthly_amortization = float(
                Decimal(str(loan_amount))
                * (Decimal(str(interest_rate)) / Decimal("100") / Decimal("12"))
                / (1 - (1 + Decimal(str(interest_rate)) / Decimal("100") / Decimal("12")) ** -term_months)
            ).__round__(2)

            cursor.execute("""
                INSERT INTO loan_details
                    (sale_id, down_payment, loan_amount, interest_rate, term_months,
                     monthly_amortization, bank_name, bank_approval_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending')
            """, (sale_id, down_payment, loan_amount, interest_rate, term_months,
                  monthly_amortization, 'automatik_financing'))

        conn.commit()

        # ── Notify finance staff (installment) or admin (full_payment) ──
        agent_user = run_query("SELECT username FROM users WHERE user_id = %s",
                               (agent_id,), fetch="one")
        agent_name = agent_user["username"] if agent_user else f"Agent #{agent_id}"
        if payment_type == "installment":
            broadcast_notif(
                role="finance_staff",
                title="New Sale for Review",
                message=f"{agent_name} created Sale #{sale_id} for {vehicle['brand']} {vehicle['model']} — ₱{selling_price:,.2f} ({payment_type}). Pending processing.",
                channel="in_app",
                ref_type="sales",
                ref_id=sale_id
            )
        else:
            broadcast_notif(
                role="admin",
                title="New Sale Completed",
                message=f"{agent_name} completed Sale #{sale_id} for {vehicle['brand']} {vehicle['model']} — ₱{selling_price:,.2f} (full payment).",
                channel="in_app",
                ref_type="sales",
                ref_id=sale_id
            )

        # ── post-commit notifications ──

        if _new_customer_ctx:
            try:
                from services.mail_service import welcome_user
                from flask import copy_current_request_context
                import threading
                portal_url = f"http://{get_local_ip()}:5173"

                @copy_current_request_context
                def _send_welcome():
                    welcome_user(_new_customer_ctx["guest_email"], "email/welcome.html",
                                 username=_new_customer_ctx["username"],
                                 temp_password=_new_customer_ctx["temp_password"],
                                 portal_url=portal_url)

                threading.Thread(target=_send_welcome, daemon=True).start()
            except Exception:
                pass
            try:
                fire_notif(user_id=_new_customer_ctx["user_id"], title="Account Created",
                           message=f"Your AutoMatik account ({_new_customer_ctx['username']}) has been created. Welcome!",
                           channel="in_app", ref_type="users", ref_id=_new_customer_ctx["user_id"])
            except Exception:
                pass

        try:
            from flask import copy_current_request_context
            import threading
            vehicle_name = f"{vehicle['brand']} {vehicle['model']}"

            @copy_current_request_context
            def _send_sale_confirm():
                send_sale_confirmation(customer["email"], customer["username"], sale_id,
                                       vehicle_name, selling_price)

            threading.Thread(target=_send_sale_confirm, daemon=True).start()
        except Exception:
            pass

        fire_notif(
            user_id=customer_id,
            title="Sale Created",
            message=f"Sale #{sale_id} has been created for {vehicle['brand']} {vehicle['model']}.",
            channel="in_app",
            ref_type="sales",
            ref_id=sale_id
        )

        return jsonify({"message": "Sale created successfully.", "sale_id": sale_id}), 201

    except Error as e:
        conn.rollback()
        return jsonify({"message": "Transaction failed.", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

def sendEmailForInquiry(inquiry_id):
    """
    AGENT PORTAL

    Send a custom email to the inquiry's customer, then auto-resolve
    the inquiry. Accepts 'subject' and 'body' in the request JSON.
    """
    if not inquiry_id:
        return jsonify({"message": "inquiry_id is required."}), 400

    inquiry = run_query("""
        SELECT * FROM inquiries
        WHERE inquiry_id = %s AND agent_id = %s
    """, (inquiry_id, session["user"]), fetch="one")

    if not inquiry:
        return jsonify({"message": "Inquiry not found or not assigned to you."}), 404

    data = request.get_json(silent=True) or {}
    subject = data.get("subject")
    body = data.get("body")

    if not subject or not body:
        return jsonify({"message": "subject and body are required."}), 400

    to_email = inquiry.get("guest_email")
    if inquiry.get("user_id") and not to_email:
        user = run_query("SELECT email FROM users WHERE user_id = %s",
                         (inquiry["user_id"],), fetch="one")
        to_email = user["email"] if user else None

    if not to_email:
        return jsonify({"message": "No customer email address available."}), 400

    try:
        from flask import copy_current_request_context
        import threading

        @copy_current_request_context
        def _send_custom():
            send_custom_email(to_email, subject, body)

        threading.Thread(target=_send_custom, daemon=True).start()
    except Exception:
        pass

    old_value = inquiry["status"]
    now = datetime.now()
    run_query("""
        UPDATE inquiries SET status = 'resolved', resolved_at = %s
        WHERE inquiry_id = %s
    """, (now, inquiry_id))

    audit_log(
        session["user"],
        "PUT",
        "inquiries",
        inquiry_id,
        json.dumps(old_value, default=str),
        json.dumps({"status": "resolved"}, default=str)
    )

    customer_name = inquiry.get("guest_name") or "Customer"
    agent = run_query("SELECT username FROM users WHERE user_id = %s",
                      (session["user"],), fetch="one")

    if inquiry.get("user_id"):
        fire_notif(
            user_id=inquiry["user_id"],
            title="Inquiry Resolved",
            message=f"Your inquiry #{inquiry_id} has been resolved. Thank you!",
            channel="in_app",
            ref_type="inquiries",
            ref_id=inquiry_id
        )

    return jsonify({"message": "Email sent and inquiry resolved."}), 200


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
                i.inquiry_id,
                i.created_at,
                agent_u.username AS agent_name

            FROM inquiries i

            JOIN vehicles v
                ON i.vehicle_id = v.vehicle_id

            LEFT JOIN user_profile up
                ON i.user_id = up.user_id
            
            LEFT JOIN users u
                ON i.user_id = u.user_id

            LEFT JOIN users agent_u
                ON i.agent_id = agent_u.user_id

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
                i.inquiry_id,
                i.created_at,
                agent_u.username AS agent_name

            FROM inquiries i

            JOIN vehicles v
                ON i.vehicle_id = v.vehicle_id

            LEFT JOIN user_profile up
                ON i.user_id = up.user_id
            
            LEFT JOIN users u
                ON i.user_id = u.user_id

            LEFT JOIN users agent_u
                ON i.agent_id = agent_u.user_id

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
            "agent_name": row["agent_name"],
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

    if res.get("agent_id"):
        fire_notif(
            user_id=res["agent_id"],
            title="Inquiry Closed",
            message=f"Inquiry #{inquiry_id} has been closed by admin.",
            channel="in_app",
            ref_type="inquiries",
            ref_id=inquiry_id
        )

    return jsonify({
        "message": "inquiry marked as 'closed'."
    }), 200

# admin
def deleteInquiry(inquiry_id):
    """
    ADMIN PORTAL

    Force-delete an inquiry from the database.
    This bypasses status checks — any inquiry can be deleted.
    """
    if not inquiry_id:
        return jsonify({"message": "inquiry_id is required."}), 400

    inquiry = run_query(
        "SELECT * FROM inquiries WHERE inquiry_id = %s",
        (inquiry_id,), fetch="one"
    )

    if not inquiry:
        return jsonify({"message": "Inquiry not found."}), 404

    run_query("DELETE FROM inquiries WHERE inquiry_id = %s", (inquiry_id,))

    audit_log(
        session["user"],
        "DELETE",
        "inquiries",
        inquiry_id,
        json.dumps(dict(inquiry), default=str),
        None
    )

    if inquiry.get("user_id"):
        fire_notif(
            user_id=inquiry["user_id"],
            title="Inquiry Deleted",
            message=f"Your inquiry #{inquiry_id} has been removed by an admin.",
            channel="in_app",
            ref_type="inquiries",
            ref_id=inquiry_id
        )

    return jsonify({"message": "Inquiry deleted successfully."}), 200