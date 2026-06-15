from flask import jsonify, request, session
from utils.log import audit_log, get_local_ip
from utils.notification import fire_notif
from services.mail_service import send_sale_confirmation, send_loan_status
from conn import run_query, get_db, Error
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from dateutil.relativedelta import relativedelta
from controllers.settingsController import get_setting_value
import json


# --- HELPERS ---

def generate_amortization_schedule(cursor, loan_id, loan_amount, interest_rate, term_months, sale_date, start_period=1, remaining_balance=None):
    principal = Decimal(str(remaining_balance if remaining_balance else loan_amount))
    rate = Decimal(str(interest_rate))
    monthly_r = rate / Decimal("100") / Decimal("12")
    n = term_months

    if monthly_r == 0:
        monthly_pay = (principal / Decimal(n)).quantize(Decimal("0.01"), ROUND_HALF_UP)
    else:
        monthly_pay = (principal * monthly_r / (1 - (1 + monthly_r) ** -n)).quantize(Decimal("0.01"), ROUND_HALF_UP)

    running_bal = principal
    rows = []

    for i in range(n):
        period = start_period + i
        interest = (running_bal * monthly_r).quantize(Decimal("0.01"), ROUND_HALF_UP)
        princ = monthly_pay - interest

        if i == n - 1:
            princ = running_bal
            monthly_pay = princ + interest

        running_bal -= princ
        due_date = sale_date + relativedelta(months=period)

        rows.append((loan_id, period, due_date, float(monthly_pay), float(princ), float(interest), float(max(running_bal, Decimal("0"))), "unpaid"))

    cursor.executemany("""
        INSERT INTO amortization_schedule
        (loan_id, month_number, due_date, total_due, principal, interest, running_balance, status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, rows)

    cursor.execute("UPDATE loan_details SET monthly_amortization = %s WHERE loan_id = %s", (float(monthly_pay), loan_id))


def insert_agent_commission(cursor, sale_id, agent_id, selling_price):
    """
    Create the agent commission record for a sale.

    Commission is computed as:
        amount = selling_price * (rate / 100)

    The rate comes from the agent's profile (agent_details.default_commission_rate)
    or falls back to 3.5% if not configured.

    Commission is always based on the original selling price (not interest-inflated).
    """
    agent = run_query("SELECT default_commission_rate FROM agent_details WHERE user_id = %s", (agent_id,), fetch="one", cursor=cursor)
    rate = float(agent["default_commission_rate"]) if agent and agent["default_commission_rate"] else float(get_setting_value("default_commission_rate", default="3.5"))
    amount = float(Decimal(str(selling_price)) * (Decimal(str(rate)) / Decimal("100")))
    cursor.execute("INSERT INTO agent_commissions (sale_id, agent_id, commission_amount, rate_applied) VALUES (%s,%s,%s,%s)", (sale_id, agent_id, amount, rate))


def _create_customer_from_inquiry(inquiry, conn, cursor):
    """
    Create a customer account from an inquiry's guest data.

    The inquiry must have guest_name and guest_email populated.
    Returns (user_id, temp_password_or_None, ctx_or_None).

    Steps:
        1. Check if a user with that email already exists; if so, reuse it.
        2. Otherwise, create a users row with role='customer', email_verified=1,
           generate a random temp password, and create customer_details.
        3. Update the inquiry with the user_id.
        4. Return context dict (username, guest_email, temp_password, user_id)
           so the caller can fire post-commit notifications.
    """
    import random
    import string
    from werkzeug.security import generate_password_hash

    guest_name = inquiry["guest_name"]
    guest_email = inquiry["guest_email"]

    # Check if a user with this email already exists
    cursor.execute("SELECT user_id FROM users WHERE email = %s", (guest_email,))
    existing = cursor.fetchone()
    if existing:
        user_id = existing["user_id"]
        temp_password = None  # already has an account, no new password
        # Ensure customer_details row exists for FK constraint
        cursor.execute("SELECT 1 FROM customer_details WHERE user_id = %s", (user_id,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO customer_details (user_id, customer_number)
                VALUES (%s, %s)
            """, (user_id, f"CUST-{datetime.now().year}-{user_id}"))
    else:
        # Username: CUST-{name}-{random4}
        safe_name = "".join(c for c in guest_name if c.isalnum() or c in "_-").lower()[:12] or "guest"
        username = f"CUST-{safe_name}-{random.randint(1000,9999)}"

        temp_password = "".join(random.choices(string.ascii_letters + string.digits, k=12))
        hashed_password = generate_password_hash(temp_password)

        cursor.execute("""
            INSERT INTO users (username, hashed_password, email, role, email_verified, is_active)
            VALUES (%s, %s, %s, 'customer', 1, 1)
        """, (username, hashed_password, guest_email))
        user_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO customer_details (user_id, customer_number)
            VALUES (%s, %s)
        """, (user_id, f"CUST-{datetime.now().year}-{user_id}"))

    # Update inquiry with user_id
    cursor.execute("UPDATE inquiries SET user_id = %s WHERE inquiry_id = %s", (user_id, inquiry["inquiry_id"]))

    # Return extra context for post-commit actions
    _new_customer_ctx = {
        "username": username if temp_password else None,
        "guest_email": guest_email if temp_password else None,
        "temp_password": temp_password,
        "user_id": user_id,
    } if temp_password else None

    return user_id, temp_password, _new_customer_ctx


# --- SALES ---

def getEligibleSalesForLoan():
    """
    Return all installment sales that do NOT yet have a loan record.

    Queries:
        - sales table (payment_type = 'installment')
        - LEFT JOIN with loan_details to exclude sales that already have a loan.
        - JOIN with users (customer), vehicles for display.

    Returns:
        tuple: (jsonify({"data": [...]}), 200) — each entry includes sale_id,
            customer name, vehicle brand/model/year, selling_price, and sale_date.
    """
    rows = run_query("""
        SELECT
            s.sale_id,
            s.selling_price,
            s.sale_date,
            cu.username AS customer_name,
            cu.user_id AS customer_id,
            v.brand,
            v.model,
            v.year,
            v.vehicle_id
        FROM sales s
        JOIN users cu ON s.customer_id = cu.user_id
        JOIN vehicles v ON s.vehicle_id = v.vehicle_id
        LEFT JOIN loan_details l ON s.sale_id = l.sale_id
        WHERE s.payment_type = 'installment'
          AND l.loan_id IS NULL
        ORDER BY s.sale_date DESC
    """, fetch="all")
    return jsonify({"data": rows}), 200


def listSales():
    """
        This will return the ff:
        
        agent, customer
        - email
        - username
        
        sales
        - payment type
        - sale date
        - sale id
        - status
        
        vehicle
        - id
        - body type
        - brand
        - model
        - price
    """
    status = request.args.get("status")
    payment_type = request.args.get("payment_type")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")

    query = """
        SELECT
            s.*,
            v.vehicle_id,
            v.brand,
            v.model,
            v.body_type,
            v.price,

            cu.username AS customer_name,
            cu.email AS customer_email,

            ag.username AS agent_name,
            ag.email AS agent_email

        FROM sales s
        JOIN vehicles v ON s.vehicle_id = v.vehicle_id
        JOIN users cu ON s.customer_id = cu.user_id
        LEFT JOIN users ag ON s.agent_id = ag.user_id
        WHERE 1=1
    """
    params = []

    if status:
        query += " AND s.status = %s"
        params.append(status)
    if payment_type:
        query += " AND s.payment_type = %s"
        params.append(payment_type)
    if date_from:
        query += " AND s.sale_date >= %s"
        params.append(date_from)
    if date_to:
        query += " AND s.sale_date <= %s"
        params.append(date_to)

    query += " ORDER BY s.sale_date DESC"
    result = run_query(query, tuple(params), fetch="all")
    
    formatted_result = []

    for row in result:
        formatted_result.append({
            "sales": {
                "sale_id": row["sale_id"],
                "payment_type": row["payment_type"],
                "sale_date": row["sale_date"],
                "status": row["status"],
                "inquiry_id": row["inquiry_id"],
                "selling_price": row["selling_price"]
            },

            "customer": {
                "username": row["customer_name"],
                "email": row["customer_email"]
            },

            "agent": {
                "username": row["agent_name"],
                "email": row["agent_email"]
            },

            "vehicle": {
                "vehicle_id": row["vehicle_id"],
                "brand": row["brand"],
                "model": row["model"],
                "body_type": row["body_type"],
                "price": row["price"]
            }
        })
    
    return jsonify({"data": formatted_result}), 200


def getSale(sale_id):
    """
        this will return the ff:
        
        sales
        loan (if payment_type = "installment")
        contract
        payment
        insurance
        
    """
    
    sale = run_query("""
        SELECT s.*, v.brand, v.model, v.body_type, v.price, v.year,
               cu.username AS customer_name, cu.email AS customer_email,
               ag.username AS agent_name
        FROM sales s
        JOIN vehicles v ON s.vehicle_id = v.vehicle_id
        JOIN users cu ON s.customer_id = cu.user_id
        LEFT JOIN users ag ON s.agent_id = ag.user_id
        WHERE s.sale_id = %s
    """, (sale_id,), fetch="one")

    if not sale:
        return jsonify({"message": "Sale not found"}), 404

    contract = run_query(
        "SELECT * FROM sales_contracts WHERE sale_id = %s",
        (sale_id,),
        fetch="one"
    )

    loan = run_query(
        "SELECT * FROM loan_details WHERE sale_id = %s",
        (sale_id,),
        fetch="one"
    )

    payments = run_query(
        """
        SELECT p.payment_id, p.amount_paid, p.payment_method,
               p.payment_date, p.proof_of_payment, u.username AS recorded_by_name
        FROM payments p
        JOIN users u
        ON p.recorded_by = u.user_id
        WHERE sale_id = %s
        ORDER BY payment_date DESC
        """,
        (sale_id,),
        fetch="all"
    )

    insurance = run_query(
        """
        SELECT insurance_id, provider_name,
               policy_number, start_date, end_date
        FROM insurance_records
        WHERE sale_id = %s
        """,
        (sale_id,),
        fetch="all"
    )

    response = {
        "sale": {
            "sale_id": sale["sale_id"],
            "sale_date": sale["sale_date"],
            "status": sale["status"],
            "total_amount": sale["selling_price"],
        },
        "vehicle": {
            "vehicle_id": sale["vehicle_id"],
            "brand": sale["brand"],
            "model": sale["model"],
            "body_type": sale["body_type"],
            "year": sale["year"],
            "price": sale["price"],
        },
        "customer": {
            "customer_id": sale["customer_id"],
            "name": sale["customer_name"],
            "email": sale["customer_email"],
        },
        "agent": {
            "agent_id": sale["agent_id"],
            "name": sale["agent_name"],
        },
        "contract": contract,
        "loan": loan,
        "payments": payments,
        "insurance": insurance,
    }

    return jsonify({
        "data": response
    }), 200


def createSale():
    """
    Create a new sale.

    If the sale originates from an inquiry (optional inquiry_id), the function
    will auto-create a customer account from the inquiry's guest data if no
    customer_id is provided. The inquiry is updated with the new user_id.

    Required fields:
        vehicle_id, agent_id, payment_type, selling_price
        (customer_id OR inquiry_id — if inquiry_id is given and has guest_name/
         guest_email, a customer account is auto-created)

    For installment loans:
        - loan_amount, interest_rate, term_months, down_payment are required
        - bank_name defaults to 'automatik_financing'
        - bank_approval_status starts as 'pending'

    Commission:
        - Agent commission is computed on the selling_price only (no interest)
        - Default rate is 3.5% (overridable per agent in agent_details)
    """
    data = request.get_json(silent=True) or {}
    vehicle_id = data.get("vehicle_id")
    customer_id = data.get("customer_id")
    agent_id = data.get("agent_id")
    payment_type = data.get("payment_type")
    selling_price = data.get("selling_price")
    inquiry_id = data.get("inquiry_id")

    # ── validate required top-level fields ──
    missing = []
    for field in ("vehicle_id", "agent_id", "payment_type", "selling_price"):
        if not data.get(field):
            missing.append(field)
    if not customer_id and not inquiry_id:
        missing.append("customer_id or inquiry_id")
    if missing:
        return jsonify({
            "message": f"Missing required fields: {', '.join(missing)}."
        }), 400

    if payment_type not in ('full_payment', 'installment'):
        return jsonify({"message": "payment_type must be 'full_payment' or 'installment'."}), 400

    try:
        selling_price = float(selling_price)
    except (TypeError, ValueError):
        return jsonify({"message": "selling_price must be a number."}), 422
    if selling_price < 0:
        return jsonify({"message": "selling_price cannot be negative."}), 400

    # ── resolve customer (from id or auto-create from inquiry) ──
    conn, cursor = get_db()
    try:
        # Lock vehicle row
        vehicle = run_query("SELECT * FROM vehicles WHERE vehicle_id = %s FOR UPDATE",
                            (vehicle_id,), fetch="one", conn=conn, cursor=cursor)
        if not vehicle:
            return jsonify({"message": "Vehicle not found."}), 404

        if vehicle["status"] not in ("available", "reserved"):
            return jsonify({
                "message": f"Vehicle status is '{vehicle['status']}'; only 'available' or 'reserved' vehicles can be sold."
            }), 409

        agent = run_query("SELECT * FROM users WHERE user_id = %s AND role = 'agent'",
                          (agent_id,), fetch="one", conn=conn, cursor=cursor)
        if not agent:
            return jsonify({"message": "Agent not found."}), 404

        temp_password = None
        _new_customer_ctx = None

        if customer_id:
            customer = run_query("SELECT * FROM users WHERE user_id = %s AND role = 'customer'",
                                 (customer_id,), fetch="one", conn=conn, cursor=cursor)
            if not customer:
                return jsonify({"message": "Customer not found."}), 404
        else:
            # ── auto-create customer from inquiry ──
            inquiry = run_query("""
                SELECT * FROM inquiries WHERE inquiry_id = %s
            """, (inquiry_id,), fetch="one", conn=conn, cursor=cursor)
            if not inquiry:
                return jsonify({"message": "Inquiry not found."}), 404
            if not inquiry.get("guest_name") or not inquiry.get("guest_email"):
                return jsonify({
                    "message": "Inquiry has no guest data. Provide customer_id instead."
                }), 400
            if inquiry["status"] not in ("open", "assigned"):
                return jsonify({"message": f"Inquiry status must be 'open' or 'assigned', got '{inquiry['status']}'."}), 400

            # Check if inquiry already linked to a user
            if inquiry.get("user_id"):
                customer = run_query("SELECT * FROM users WHERE user_id = %s AND role = 'customer'",
                                     (inquiry["user_id"],), fetch="one", conn=conn, cursor=cursor)
                if not customer:
                    return jsonify({"message": "Linked inquiry user is not a customer."}), 400
                customer_id = customer["user_id"]
            else:
                # Create customer from guest info
                new_user_id, temp_password, _new_customer_ctx = _create_customer_from_inquiry(inquiry, conn, cursor)
                customer = run_query("SELECT * FROM users WHERE user_id = %s",
                                     (new_user_id,), fetch="one", conn=conn, cursor=cursor)
                customer_id = new_user_id

        # ── create sale ──
        cursor.execute("""
            INSERT INTO sales (vehicle_id, customer_id, agent_id, selling_price, payment_type, status, inquiry_id)
            VALUES (%s, %s, %s, %s, %s, 'pending', %s)
        """, (vehicle_id, customer_id, agent_id, selling_price, payment_type, inquiry_id))
        sale_id = cursor.lastrowid

        # Mark inquiry as resolved (if coming from inquiry)
        if inquiry_id:
            cursor.execute("""
                UPDATE inquiries SET status = 'resolved', resolved_at = NOW(), user_id = %s
                WHERE inquiry_id = %s
            """, (customer_id, inquiry_id))

        # Agent commission
        insert_agent_commission(cursor, sale_id, agent_id, selling_price)

        # Mark vehicle as sold
        cursor.execute("UPDATE vehicles SET status = 'delivered' WHERE vehicle_id = %s", (vehicle_id,))

        # Audit log
        audit_log(
            session["user"],
            "POST",
            "sales",
            sale_id, None, json.dumps({
                "vehicle_id": vehicle_id,
                "customer_id": customer_id,
                "agent_id": agent_id,
                "payment_type": payment_type,
                "selling_price": selling_price,
                "status": "pending",
            }, default=str),
            conn=conn, cursor=cursor
        )

        # Draft contract
        cursor.execute("INSERT INTO sales_contracts (sale_id, status) VALUES (%s, 'draft')", (sale_id,))

        # ── installment handling ──
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
            if term_months < 6 or term_months > int(get_setting_value("max_loan_term_months", default="60")):
                return jsonify({"message": f"term_months must be between 6 and {int(get_setting_value('max_loan_term_months', default='60'))}."}), 422
            if interest_rate < 0 or interest_rate > 30:
                return jsonify({"message": "interest_rate must be between 0 and 30."}), 422

            # Pre-compute monthly amortisation with PMT formula
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

            loan_id = cursor.lastrowid
            sale_date = datetime.now()
            generate_amortization_schedule(cursor, loan_id, loan_amount, interest_rate, term_months, sale_date)

        conn.commit()

        # ── post-commit notifications ──

        # Welcome email + in-app notification for newly auto-created customers
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

        # Sale confirmation email
        try:
            from flask import copy_current_request_context
            import threading
            vehicle_name = f"{vehicle['brand']} {vehicle['model']}"

            @copy_current_request_context
            def _send_sale_confirm():
                send_sale_confirmation(customer["email"], customer["username"], sale_id, vehicle_name, selling_price)

            threading.Thread(target=_send_sale_confirm, daemon=True).start()
        except Exception:
            pass

        # Sale created in-app notification
        fire_notif(
            user_id=customer_id,
            title="Sale Created",
            message=f"Sale #{sale_id} has been created for {vehicle['brand']} {vehicle['model']}.",
            channel="in_app",
            ref_type="sales",
            ref_id=sale_id
        )

        response = {
            "message": "Sale created successfully.",
            "sale_id": sale_id,
            "customer_id": customer_id,
        }
        if temp_password:
            response["temp_password"] = temp_password

        return jsonify(response), 201

    except Error as e:
        conn.rollback()
        return jsonify({"message": "Transaction failed.", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

def updateSaleStatus(sale_id):
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")

    if not new_status:
        return jsonify({"message": "status is required."}), 400

    valid_transitions = {"pending": ["completed", "cancelled"], "completed": [], "cancelled": []}
    sale = run_query("SELECT * FROM sales WHERE sale_id = %s", (sale_id,), fetch="one")

    if not sale:
        return jsonify({"message": "Sale not found."}), 404

    if new_status not in valid_transitions:
        return jsonify({"message": f"'{new_status}' is not a valid status."}), 422

    if new_status not in valid_transitions[sale["status"]]:
        return jsonify({"message": f"Cannot transition from '{sale['status']}' to '{new_status}'."}), 400

    old_value = sale["status"]
    run_query("UPDATE sales SET status = %s WHERE sale_id = %s", (new_status, sale_id))

    if new_status == "cancelled":
        run_query("UPDATE vehicles SET status = 'available' WHERE vehicle_id = %s", (sale["vehicle_id"],))

    audit_log(session["user"], "PUT", "sales", sale_id, json.dumps(old_value, default=str), json.dumps({"status": new_status}, default=str))

    # Notify customer of sale status change
    try:
        fire_notif(user_id=sale["customer_id"], title="Sale Status Updated",
                   message=f"Sale #{sale_id} status changed to '{new_status}'.",
                   channel="in_app", ref_type="sales", ref_id=sale_id)
    except Exception:
        pass

    return jsonify({"message": f"Sale status updated to '{new_status}'."}), 200


def getMySales():
    customer_id = session["user"]
    result = run_query("""
        SELECT s.*, v.brand, v.model, v.body_type, v.price
        FROM sales s
        JOIN vehicles v ON s.vehicle_id = v.vehicle_id
        WHERE s.customer_id = %s
        ORDER BY s.sale_date DESC
    """, (customer_id,), fetch="all")

    return jsonify({"data": result}), 200


def getMySale(sale_id):
    customer_id = session["user"]
    sale = run_query("""
        SELECT s.*, v.brand, v.model, v.body_type, v.price, v.year
        FROM sales s
        JOIN vehicles v ON s.vehicle_id = v.vehicle_id
        WHERE s.sale_id = %s AND s.customer_id = %s
    """, (sale_id, customer_id), fetch="one")

    if not sale:
        return jsonify({"message": "Sale not found."}), 404

    contract = run_query("SELECT * FROM sales_contracts WHERE sale_id = %s", (sale_id,), fetch="one")
    loan = run_query("SELECT * FROM loan_details WHERE sale_id = %s", (sale_id,), fetch="one")
    payments = run_query("SELECT * FROM payments WHERE sale_id = %s ORDER BY payment_date DESC", (sale_id,), fetch="all")

    sale["contract"] = contract
    sale["loan"] = loan
    sale["payments"] = payments

    return jsonify({"data": sale}), 200


# --- CONTRACTS ---

def getSaleContract(sale_id):
    sale = run_query("SELECT sale_id FROM sales WHERE sale_id = %s", (sale_id,), fetch="one")
    if not sale:
        return jsonify({"message": "Sale not found."}), 404

    contract = run_query("SELECT * FROM sales_contracts WHERE sale_id = %s", (sale_id,), fetch="one")
    if not contract:
        return jsonify({"message": "Contract not found."}), 404

    return jsonify({"data": contract}), 200


def createContract(sale_id):
    sale = run_query("SELECT * FROM sales WHERE sale_id = %s", (sale_id,), fetch="one")
    if not sale:
        return jsonify({"message": "Sale not found."}), 404

    existing = run_query("SELECT contract_id FROM sales_contracts WHERE sale_id = %s", (sale_id,), fetch="one")
    if existing:
        return jsonify({"message": "Contract already exists for this sale."}), 409

    contract_id = run_query("INSERT INTO sales_contracts (sale_id, status) VALUES (%s,'draft')", (sale_id,))

    audit_log(session["user"], "POST", "sales_contracts", contract_id, None, json.dumps({"sale_id": sale_id, "status": "draft"}, default=str))

    return jsonify({"contract_id": contract_id}), 201


def signContract(sale_id):
    sale = run_query("SELECT sale_id, status FROM sales WHERE sale_id = %s", (sale_id,), fetch="one")
    if not sale:
        return jsonify({"message": "Sale not found."}), 404

    contract = run_query("SELECT * FROM sales_contracts WHERE sale_id = %s", (sale_id,), fetch="one")
    if not contract:
        return jsonify({"message": "Contract not found. Create it first."}), 404

    if contract["status"] == "signed":
        return jsonify({"message": "Contract is already signed."}), 400

    old_value = contract["status"]
    now = datetime.now()
    run_query("UPDATE sales_contracts SET status = 'signed', signed_at = %s, reviewed_by = %s WHERE sale_id = %s", (now, session["user"], sale_id))

    audit_log(session["user"], "PUT", "sales_contracts", contract["contract_id"], json.dumps(old_value, default=str), json.dumps({"status": "signed"}, default=str))

    return jsonify({"message": "Contract signed successfully."}), 200


def updateContract(sale_id):
    """
    Update contract URL and/or status for a sale.
    Accepts 'contract_url' (optional) and 'status' (optional).
    Valid status transitions: draft → pending_signature → signed → cancelled.
    """
    sale = run_query("SELECT sale_id, status FROM sales WHERE sale_id = %s", (sale_id,), fetch="one")
    if not sale:
        return jsonify({"message": "Sale not found."}), 404

    contract = run_query("SELECT * FROM sales_contracts WHERE sale_id = %s", (sale_id,), fetch="one")
    if not contract:
        return jsonify({"message": "Contract not found. Create it first."}), 404

    data = request.get_json(silent=True) or {}
    contract_url = data.get("contract_url")
    new_status = data.get("status")

    if not contract_url and not new_status:
        return jsonify({"message": "Provide at least 'contract_url' or 'status' to update."}), 400

    allowed_statuses = ("draft", "pending_signature", "signed", "cancelled")
    if new_status and new_status not in allowed_statuses:
        return jsonify({"message": f"Invalid status. Must be one of {', '.join(allowed_statuses)}."}), 400

    updates = []
    values = []
    if contract_url is not None:
        updates.append("contract_url = %s")
        values.append(contract_url)
    if new_status:
        updates.append("status = %s")
        values.append(new_status)
        if new_status == "signed":
            updates.append("signed_at = %s")
            values.append(datetime.now())
            updates.append("reviewed_by = %s")
            values.append(session["user"])

    if not updates:
        return jsonify({"message": "No changes to apply."}), 400

    values.append(sale_id)
    run_query(f"UPDATE sales_contracts SET {', '.join(updates)} WHERE sale_id = %s", tuple(values))

    audit_log(
        session["user"],
        "PUT",
        "sales_contracts",
        contract["contract_id"],
        None,
        json.dumps(data, default=str)
    )

    return jsonify({"message": "Contract updated successfully."}), 200


# --- INSURANCE ---

def listInsurance():
    result = run_query("""
        SELECT i.*, s.sale_id, v.brand, v.model, cu.username AS customer_name
        FROM insurance_records i
        JOIN sales s ON i.sale_id = s.sale_id
        JOIN vehicles v ON s.vehicle_id = v.vehicle_id
        JOIN users cu ON s.customer_id = cu.user_id
        ORDER BY i.start_date DESC
    """, fetch="all")

    return jsonify({"data": result}), 200


def getInsurance(insurance_id):
    result = run_query("""
        SELECT i.*, s.sale_id, v.brand, v.model, v.year, cu.username AS customer_name
        FROM insurance_records i
        JOIN sales s ON i.sale_id = s.sale_id
        JOIN vehicles v ON s.vehicle_id = v.vehicle_id
        JOIN users cu ON s.customer_id = cu.user_id
        WHERE i.insurance_id = %s
    """, (insurance_id,), fetch="one")
    if not result:
        return jsonify({"message": "Insurance record not found."}), 404
    return jsonify({"data": result}), 200


def addInsurance(sale_id):
    sale = run_query("SELECT sale_id, vehicle_id, customer_id FROM sales WHERE sale_id = %s", (sale_id,), fetch="one")
    if not sale:
        return jsonify({"message": "Sale not found."}), 404

    data = request.get_json(silent=True) or {}
    provider_name = data.get("provider") or data.get("provider_name")
    policy_number = data.get("policy_number")
    start_date = data.get("coverage_start") or data.get("start_date")
    end_date = data.get("coverage_end") or data.get("end_date")
    coverage_type = data.get("coverage_type")

    if not all([provider_name, policy_number, start_date, end_date]):
        return jsonify({"message": "provider (or provider_name), policy_number, coverage_start (or start_date), and coverage_end (or end_date) are required."}), 400

    insurance_id = run_query("""
        INSERT INTO insurance_records (sale_id, vehicle_id, customer_id, provider_name, policy_number, coverage_type, start_date, end_date)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (sale_id, sale["vehicle_id"], sale["customer_id"], provider_name, policy_number, coverage_type, start_date, end_date))

    audit_log(session["user"], "POST", "insurance_records", insurance_id, None, json.dumps(data, default=str))

    # Notify customer
    try:
        fire_notif(user_id=sale["customer_id"], title="Insurance Added",
                   message=f"Insurance policy {policy_number} added to sale #{sale_id}.",
                   channel="in_app", ref_type="insurance_records", ref_id=insurance_id)
    except Exception:
        pass

    return jsonify({"insurance_id": insurance_id}), 201


def updateInsurance(insurance_id):
    data = request.get_json(silent=True) or {}
    existing = run_query("SELECT * FROM insurance_records WHERE insurance_id = %s", (insurance_id,), fetch="one")

    if not existing:
        return jsonify({"message": "Insurance record not found."}), 404

    provider_name = data.get("provider") or data.get("provider_name")
    start_date = data.get("coverage_start") or data.get("start_date")
    end_date = data.get("coverage_end") or data.get("end_date")
    status = data.get("status")
    coverage_type = data.get("coverage_type")

    updates = []
    params = []

    if provider_name is not None:
        updates.append("provider_name = %s")
        params.append(provider_name)
    if start_date is not None:
        updates.append("start_date = %s")
        params.append(start_date)
    if end_date is not None:
        updates.append("end_date = %s")
        params.append(end_date)
    if coverage_type is not None:
        updates.append("coverage_type = %s")
        params.append(coverage_type)
    if status is not None:
        if status not in ("active", "expired", "cancelled"):
            return jsonify({"message": "status must be 'active', 'expired', or 'cancelled'."}), 422
        updates.append("status = %s")
        params.append(status)

    if not updates:
        return jsonify({"message": "No fields to update."}), 400

    params.append(insurance_id)
    run_query(f"UPDATE insurance_records SET {', '.join(updates)} WHERE insurance_id = %s", tuple(params))

    audit_log(session["user"], "PUT", "insurance_records", insurance_id, json.dumps(existing, default=str), json.dumps(data, default=str))

    # Notify customer
    try:
        sale = run_query("SELECT customer_id FROM sales WHERE sale_id = %s", (existing["sale_id"],), fetch="one")
        if sale:
            fire_notif(user_id=sale["customer_id"], title="Insurance Updated",
                       message=f"Insurance policy {existing['policy_number']} updated.",
                       channel="in_app", ref_type="insurance_records", ref_id=insurance_id)
    except Exception:
        pass

    return jsonify({"message": "Insurance record updated."}), 200


# --- LOANS ---

def listLoans():
    bank_approval_status = request.args.get("bank_approval_status")
    without_insurance = request.args.get("without_insurance")
    query = """
        SELECT l.*, s.sale_id, v.brand, v.model, cu.username AS customer_name
        FROM loan_details l
        JOIN sales s ON l.sale_id = s.sale_id
        JOIN vehicles v ON s.vehicle_id = v.vehicle_id
        JOIN users cu ON s.customer_id = cu.user_id
        WHERE 1=1
    """
    params = []
    if bank_approval_status:
        query += " AND l.bank_approval_status = %s"
        params.append(bank_approval_status)
    if without_insurance:
        query += """ AND s.sale_id NOT IN (
            SELECT sale_id FROM insurance_records WHERE sale_id IS NOT NULL
        )"""
    query += " ORDER BY l.loan_id DESC"
    result = run_query(query, tuple(params), fetch="all")
    return jsonify({"data": result}), 200


def getLoan(loan_id):
    loan = run_query("""
        SELECT l.*, s.sale_id, v.brand, v.model, cu.username AS customer_name
        FROM loan_details l
        JOIN sales s ON l.sale_id = s.sale_id
        JOIN vehicles v ON s.vehicle_id = v.vehicle_id
        JOIN users cu ON s.customer_id = cu.user_id
        WHERE l.loan_id = %s
    """, (loan_id,), fetch="one")

    if not loan:
        return jsonify({"message": "Loan not found."}), 404

    schedule = run_query("""
        SELECT a.*, p.proof_of_payment, p.payment_id, p.review_status
        FROM amortization_schedule a
        LEFT JOIN payments p ON a.schedule_id = p.schedule_id AND p.payment_allocation = 'amortization'
        WHERE a.loan_id = %s
        ORDER BY a.month_number
    """, (loan_id,), fetch="all")

    loan["amortization_schedule"] = schedule
    return jsonify({"data": loan}), 200


def createLoan(sale_id):
    if not sale:
        return jsonify({"message": "Sale not found."}), 404

    if sale["payment_type"] != "installment":
        return jsonify({"message": "Sale is not an installment sale."}), 400

    existing = run_query("SELECT loan_id FROM loan_details WHERE sale_id = %s", (sale_id,), fetch="one")
    if existing:
        return jsonify({"message": "Loan already exists for this sale."}), 409

    data = request.get_json(silent=True) or {}
    loan_amount = data.get("loan_amount")
    interest_rate = data.get("interest_rate")
    term_months = data.get("term_months")
    down_payment = data.get("down_payment", 0)

    if not all([loan_amount, interest_rate, term_months]):
        return jsonify({"message": "loan_amount, interest_rate, and term_months are required."}), 400

    try:
        loan_amount = float(loan_amount)
        interest_rate = float(interest_rate)
        term_months = int(term_months)
    except (TypeError, ValueError):
        return jsonify({"message": "loan_amount, interest_rate, and term_months must be numbers."}), 422

    if loan_amount <= 0 or loan_amount > float(sale["selling_price"]):
        return jsonify({"message": "loan_amount must be > 0 and <= selling_price."}), 422
    if term_months < 6 or term_months > int(get_setting_value("max_loan_term_months", default="60")):
        return jsonify({"message": f"term_months must be between 6 and {int(get_setting_value('max_loan_term_months', default='60'))}."}), 422
    if interest_rate < 0 or interest_rate > 30:
        return jsonify({"message": "interest_rate must be between 0 and 30."}), 422

    conn, cursor = get_db()
    try:
        loan_id = run_query("""
            INSERT INTO loan_details (sale_id, loan_amount, interest_rate, term_months, down_payment, bank_name, bank_approval_status)
            VALUES (%s,%s,%s,%s,%s,'automatik_financing','pending')
        """, (sale_id, loan_amount, interest_rate, term_months, down_payment), conn=conn, cursor=cursor)

        sale_date = sale["sale_date"] if sale["sale_date"] else datetime.now()
        generate_amortization_schedule(cursor, loan_id, loan_amount, interest_rate, term_months, sale_date)
        conn.commit()

        return jsonify({"loan_id": loan_id}), 201
    except Error as e:
        conn.rollback()
        return jsonify({"message": "Transaction failed.", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


def updateLoanStatus(loan_id):
    """
    Update the bank_approval_status of a loan.

    When a loan is approved:
        - If no amortization schedule rows exist yet (i.e. the loan was created
          via createSale without a full schedule), generate them now.
        - Notify the customer via in-app + email.

    When a loan is rejected:
        - Notify the customer.
    """
    data = request.get_json(silent=True) or {}
    bank_approval_status = data.get("bank_approval_status")

    if not bank_approval_status:
        return jsonify({"message": "bank_approval_status is required."}), 400

    if bank_approval_status not in ("approved", "rejected"):
        return jsonify({"message": "bank_approval_status must be 'approved' or 'rejected'."}), 422

    conn, cursor = get_db()
    try:
        loan = run_query("""
            SELECT l.*, s.customer_id, s.sale_id, s.sale_date, s.selling_price
            FROM loan_details l
            JOIN sales s ON l.sale_id = s.sale_id
            WHERE l.loan_id = %s FOR UPDATE
        """, (loan_id,), fetch="one", conn=conn, cursor=cursor)

        if not loan:
            return jsonify({"message": "Loan not found."}), 404

        if loan["bank_approval_status"] == bank_approval_status:
            return jsonify({"message": f"Loan is already '{bank_approval_status}'."}), 409

        old_value = loan["bank_approval_status"]

        # ── On approval: generate amortization schedule if missing ──
        if bank_approval_status == "approved":
            existing_schedule = run_query(
                "SELECT COUNT(*) AS cnt FROM amortization_schedule WHERE loan_id = %s",
                (loan_id,), fetch="one", conn=conn, cursor=cursor
            )
            if existing_schedule and existing_schedule["cnt"] == 0:
                sale_date = loan["sale_date"] if loan["sale_date"] else datetime.now()
                generate_amortization_schedule(
                    cursor, loan_id,
                    float(loan["loan_amount"]),
                    float(loan["interest_rate"]),
                    int(loan["term_months"]),
                    sale_date
                )

        run_query(
            "UPDATE loan_details SET bank_approval_status = %s WHERE loan_id = %s",
            (bank_approval_status, loan_id), conn=conn, cursor=cursor
        )

        audit_log(
            session["user"], "PUT", "loan_details", loan_id,
            json.dumps(old_value, default=str),
            json.dumps({"bank_approval_status": bank_approval_status}, default=str),
            conn=conn, cursor=cursor
        )

        conn.commit()

        # ── Notifications ──
        customer = run_query(
            "SELECT email, username FROM users WHERE user_id = %s",
            (loan["customer_id"],), fetch="one"
        )
        customer_name = run_query(
            "SELECT full_name FROM user_profile WHERE user_id = %s",
            (loan["customer_id"],), fetch="one"
        )
        name = customer_name["full_name"] if customer_name else (customer["username"] if customer else "Customer")

        fire_notif(
            user_id=loan["customer_id"],
            title="Loan Status Updated",
            message=f"Your loan for sale #{loan['sale_id']} has been {bank_approval_status}.",
            channel="in_app",
            ref_type="loan_details",
            ref_id=loan_id
        )

        if customer:
            try:
                from flask import copy_current_request_context
                import threading

                @copy_current_request_context
                def _send_loan_status():
                    send_loan_status(customer["email"], name, bank_approval_status, loan["sale_id"])

                threading.Thread(target=_send_loan_status, daemon=True).start()
            except Exception:
                pass

        return jsonify({"message": f"Loan status updated to '{bank_approval_status}'."}), 200

    except Error as e:
        conn.rollback()
        return jsonify({"message": "Transaction failed.", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


def getLoanSchedule(loan_id):
    loan = run_query("SELECT loan_id FROM loan_details WHERE loan_id = %s", (loan_id,), fetch="one")
    if not loan:
        return jsonify({"message": "Loan not found."}), 404

    schedule = run_query("""
        SELECT * FROM amortization_schedule
        WHERE loan_id = %s
        ORDER BY month_number
    """, (loan_id,), fetch="all")

    return jsonify({"data": schedule}), 200


def getMyLoans():
    customer_id = session["user"]
    loans = run_query("""
        SELECT l.*, s.sale_id, v.brand, v.model
        FROM loan_details l
        JOIN sales s ON l.sale_id = s.sale_id
        JOIN vehicles v ON s.vehicle_id = v.vehicle_id
        WHERE s.customer_id = %s
        ORDER BY l.loan_id DESC
    """, (customer_id,), fetch="all")

    for loan in loans:
        schedule = run_query("""
            SELECT * FROM amortization_schedule
            WHERE loan_id = %s
            ORDER BY month_number
        """, (loan["loan_id"],), fetch="all")
        loan["amortization_schedule"] = schedule

    return jsonify({"data": loans}), 200


# --- AMORTIZATION ---

def updateAmortizationStatus(schedule_id):
    data = request.get_json(silent=True) or {}
    status = data.get("status")

    if not status:
        return jsonify({"message": "status is required."}), 400

    if status not in ("paid", "overdue"):
        return jsonify({"message": "status must be 'paid' or 'overdue'."}), 422

    schedule = run_query("""
        SELECT a.*, l.sale_id, s.customer_id
        FROM amortization_schedule a
        JOIN loan_details l ON a.loan_id = l.loan_id
        JOIN sales s ON l.sale_id = s.sale_id
        WHERE a.schedule_id = %s
    """, (schedule_id,), fetch="one")

    if not schedule:
        return jsonify({"message": "Amortization schedule entry not found."}), 404

    if schedule["status"] != "unpaid":
        return jsonify({"message": f"Entry is already '{schedule['status']}'."}), 409

    old_value = schedule["status"]
    run_query("UPDATE amortization_schedule SET status = %s WHERE schedule_id = %s", (status, schedule_id))

    fire_notif(user_id=schedule.get("customer_id"), title="Amortization Updated", message=f"Amortization period #{schedule['month_number']} marked as {status}.", channel="in_app", ref_type="amortization_schedule", ref_id=schedule_id)

    return jsonify({"message": f"Amortization status updated to '{status}'."}), 200


def getOverdueAmortizations():
    result = run_query("""
        SELECT a.*, l.sale_id, cu.user_id AS customer_id, cu.username AS customer_name
        FROM amortization_schedule a
        JOIN loan_details l ON a.loan_id = l.loan_id
        JOIN sales s ON l.sale_id = s.sale_id
        JOIN users cu ON s.customer_id = cu.user_id
        WHERE a.status = 'unpaid' AND a.due_date < CURDATE()
        ORDER BY a.due_date
    """, fetch="all")

    return jsonify({"data": result}), 200


def recomputeAmortization(loan_id):
    data = request.get_json(silent=True) or {}
    new_rate = data.get("interest_rate")
    new_term = data.get("term_months")

    if not all([new_rate, new_term]):
        return jsonify({"message": "interest_rate and term_months are required."}), 400

    try:
        new_rate = float(new_rate)
        new_term = int(new_term)
    except (TypeError, ValueError):
        return jsonify({"message": "interest_rate and term_months must be numbers."}), 422

    if new_term < 6 or new_term > int(get_setting_value("max_loan_term_months", default="60")):
        return jsonify({"message": f"term_months must be between 6 and {int(get_setting_value('max_loan_term_months', default='60'))}."}), 422
    if new_rate < 0 or new_rate > 30:
        return jsonify({"message": "interest_rate must be between 0 and 30."}), 422

    conn, cursor = get_db()
    try:
        paid = run_query("""
            SELECT COALESCE(SUM(principal), 0) AS paid_principal,
                   COUNT(*) AS paid_count,
                   MAX(month_number) AS last_paid_period
            FROM amortization_schedule
            WHERE loan_id = %s AND status = 'paid'
        """, (loan_id,), fetch="one", conn=conn, cursor=cursor)

        loan = run_query("SELECT loan_amount, sale_id FROM loan_details WHERE loan_id = %s", (loan_id,), fetch="one", conn=conn, cursor=cursor)
        if not loan:
            return jsonify({"message": "Loan not found."}), 404

        sale = run_query("SELECT sale_date FROM sales WHERE sale_id = %s", (loan["sale_id"],), fetch="one", conn=conn, cursor=cursor)
        sale_date = sale["sale_date"] if sale else datetime.now()

        remaining = float(loan["loan_amount"]) - float(paid["paid_principal"])
        start_p = int(paid["last_paid_period"] or 0) + 1
        new_n = new_term - int(paid["paid_count"])

        if new_n <= 0:
            return jsonify({"message": "New term must exceed already paid periods."}), 422

        run_query("DELETE FROM amortization_schedule WHERE loan_id = %s AND status = 'unpaid'", (loan_id,), conn=conn, cursor=cursor)

        generate_amortization_schedule(cursor, loan_id, loan["loan_amount"], new_rate, new_n, sale_date, start_period=start_p, remaining_balance=remaining)

        run_query("UPDATE loan_details SET interest_rate = %s, term_months = %s WHERE loan_id = %s", (new_rate, new_term, loan_id), conn=conn, cursor=cursor)

        conn.commit()
        return jsonify({"message": "Amortization schedule recomputed."}), 200

    except Error as e:
        conn.rollback()
        return jsonify({"message": "Transaction failed.", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
