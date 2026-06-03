from flask import jsonify, request, session
from utils.log import audit_log
from utils.notification import fire_notif
from services.mail_service import send_sale_confirmation, send_loan_status
from conn import run_query, get_db, Error
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from dateutil.relativedelta import relativedelta
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
        (loan_id, period_number, due_date, amount_due, principal_component, interest_component, remaining_balance, status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, rows)

    cursor.execute("UPDATE loan_details SET monthly_amortization = %s WHERE loan_id = %s", (float(monthly_pay), loan_id))


def insert_agent_commission(cursor, sale_id, agent_id, selling_price):
    agent = run_query("SELECT default_commission_rate FROM agent_details WHERE user_id = %s", (agent_id,), fetch="one")
    rate = float(agent["default_commission_rate"]) if agent and agent["default_commission_rate"] else 3.0
    amount = float(Decimal(str(selling_price)) * Decimal(str(rate)) / Decimal("100"))
    cursor.execute("INSERT INTO agent_commissions (sale_id, agent_id, amount, commission_rate) VALUES (%s,%s,%s,%s)", (sale_id, agent_id, amount, rate))


# --- SALES ---

def listSales():
    status = request.args.get("status")
    payment_type = request.args.get("payment_type")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")

    query = """
        SELECT s.*, v.brand, v.model, v.body_type, v.price,
               cu.username AS customer_name, cu.email AS customer_email,
               ag.username AS agent_name
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
    return jsonify({"data": result}), 200


def getSale(sale_id):
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
        return jsonify({"message": "Sale not found."}), 404

    contract = run_query("SELECT * FROM sales_contracts WHERE sale_id = %s", (sale_id,), fetch="one")
    loan = run_query("SELECT * FROM loan_details WHERE sale_id = %s", (sale_id,), fetch="one")
    payments = run_query("SELECT * FROM payments WHERE sale_id = %s ORDER BY payment_date DESC", (sale_id,), fetch="all")
    insurance = run_query("SELECT * FROM insurance_records WHERE sale_id = %s", (sale_id,), fetch="all")

    sale["contract"] = contract
    sale["loan"] = loan
    sale["payments"] = payments
    sale["insurance"] = insurance

    return jsonify({"data": sale}), 200


def createSale():
    data = request.get_json(silent=True) or {}
    vehicle_id = data.get("vehicle_id")
    customer_id = data.get("customer_id")
    agent_id = data.get("agent_id")
    payment_type = data.get("payment_type")
    selling_price = data.get("selling_price")

    if not all([vehicle_id, customer_id, payment_type, selling_price]):
        return jsonify({"message": "vehicle_id, customer_id, payment_type, and selling_price are required."}), 400

    if payment_type not in ("cash", "installment"):
        return jsonify({"message": "payment_type must be 'cash' or 'installment'."}), 422

    try:
        selling_price = float(selling_price)
    except (TypeError, ValueError):
        return jsonify({"message": "selling_price must be a number."}), 422

    if selling_price <= 0:
        return jsonify({"message": "selling_price must be greater than 0."}), 422

    conn, cursor = get_db()

    try:
        vehicle = run_query("SELECT status FROM vehicles WHERE vehicle_id = %s FOR UPDATE", (vehicle_id,), fetch="one", conn=conn, cursor=cursor)
        if not vehicle:
            return jsonify({"message": "Vehicle not found."}), 404
        if vehicle["status"] != "available":
            return jsonify({"message": "Vehicle is not available."}), 409

        customer = run_query("SELECT user_id, role, is_active FROM users WHERE user_id = %s", (customer_id,), fetch="one", conn=conn, cursor=cursor)
        if not customer or customer["role"] != "customer":
            return jsonify({"message": "Customer not found."}), 404
        if not customer["is_active"]:
            return jsonify({"message": "Customer account is inactive."}), 400

        if agent_id:
            agent = run_query("SELECT user_id, role, is_active FROM users WHERE user_id = %s", (agent_id,), fetch="one", conn=conn, cursor=cursor)
            if not agent or agent["role"] != "agent":
                return jsonify({"message": "Agent not found."}), 404
            if not agent["is_active"]:
                return jsonify({"message": "Agent account is inactive."}), 400

        if payment_type == "installment":
            loan_amount = data.get("loan_amount")
            term_months = data.get("term_months")
            interest_rate = data.get("interest_rate")
            if not all([loan_amount, term_months, interest_rate]):
                return jsonify({"message": "loan_amount, term_months, and interest_rate are required for installment."}), 422
            try:
                loan_amount = float(loan_amount)
                term_months = int(term_months)
                interest_rate = float(interest_rate)
            except (TypeError, ValueError):
                return jsonify({"message": "loan_amount, term_months, and interest_rate must be numbers."}), 422
            if loan_amount <= 0 or loan_amount > selling_price:
                return jsonify({"message": "loan_amount must be > 0 and <= selling_price."}), 422
            if term_months < 6 or term_months > 60:
                return jsonify({"message": "term_months must be between 6 and 60."}), 422
            if interest_rate < 0 or interest_rate > 30:
                return jsonify({"message": "interest_rate must be between 0 and 30."}), 422

        sale_id = run_query("""
            INSERT INTO sales (vehicle_id, customer_id, agent_id, payment_type, selling_price, status, sale_date)
            VALUES (%s,%s,%s,%s,%s,'pending',NOW())""",
            (vehicle_id, customer_id, agent_id, payment_type, selling_price), conn=conn, cursor=cursor)

        run_query("UPDATE vehicles SET status = 'reserved' WHERE vehicle_id = %s", (vehicle_id,), conn=conn, cursor=cursor)

        sale_date = datetime.now()

        if payment_type == "installment":
            loan_id = run_query("""
                INSERT INTO loan_details (sale_id, loan_amount, interest_rate, term_months, bank_approval_status)
                VALUES (%s,%s,%s,%s,'pending')""",
                (sale_id, loan_amount, interest_rate, term_months), conn=conn, cursor=cursor)
            generate_amortization_schedule(cursor, loan_id, loan_amount, interest_rate, term_months, sale_date)

        run_query("INSERT INTO sales_contracts (sale_id, status) VALUES (%s,'draft')", (sale_id,), conn=conn, cursor=cursor)

        if agent_id:
            try:
                insert_agent_commission(cursor, sale_id, agent_id, selling_price)
            except Exception:
                pass

        conn.commit()

        customer_email = customer["email"]
        customer_name = run_query("SELECT full_name FROM user_profile WHERE user_id = %s", (customer_id,), fetch="one", conn=conn, cursor=cursor)
        name = customer_name["full_name"] if customer_name else "Customer"
        vehicle_info = run_query("SELECT brand, model FROM vehicles WHERE vehicle_id = %s", (vehicle_id,), fetch="one", conn=conn, cursor=cursor)
        vehicle_name = f"{vehicle_info['brand']} {vehicle_info['model']}" if vehicle_info else "Vehicle"

        fire_notif(user_id=customer_id, title="Sale Created", message=f"Your sale #{sale_id} for {vehicle_name} has been created.", channel="in_app", ref_type="sales", ref_id=sale_id)

        try:
            send_sale_confirmation(customer_email, name, sale_id, vehicle_name, selling_price)
        except Exception:
            pass

        return jsonify({"sale_id": sale_id}), 201

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


def addInsurance(sale_id):
    sale = run_query("SELECT sale_id FROM sales WHERE sale_id = %s", (sale_id,), fetch="one")
    if not sale:
        return jsonify({"message": "Sale not found."}), 404

    data = request.get_json(silent=True) or {}
    provider = data.get("provider")
    policy_number = data.get("policy_number")
    coverage_start = data.get("coverage_start")
    coverage_end = data.get("coverage_end")

    if not all([provider, policy_number, coverage_start, coverage_end]):
        return jsonify({"message": "provider, policy_number, coverage_start, and coverage_end are required."}), 400

    insurance_id = run_query("""
        INSERT INTO insurance_records (sale_id, provider, policy_number, coverage_start, coverage_end)
        VALUES (%s,%s,%s,%s,%s)
    """, (sale_id, provider, policy_number, coverage_start, coverage_end))

    audit_log(session["user"], "POST", "insurance_records", insurance_id, None, json.dumps(data, default=str))

    return jsonify({"insurance_id": insurance_id}), 201


def updateInsurance(insurance_id):
    data = request.get_json(silent=True) or {}
    existing = run_query("SELECT * FROM insurance_records WHERE insurance_id = %s", (insurance_id,), fetch="one")

    if not existing:
        return jsonify({"message": "Insurance record not found."}), 404

    provider = data.get("provider")
    coverage_start = data.get("coverage_start")
    coverage_end = data.get("coverage_end")
    status = data.get("status")

    updates = []
    params = []

    if provider is not None:
        updates.append("provider = %s")
        params.append(provider)
    if coverage_start is not None:
        updates.append("coverage_start = %s")
        params.append(coverage_start)
    if coverage_end is not None:
        updates.append("coverage_end = %s")
        params.append(coverage_end)
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

    return jsonify({"message": "Insurance record updated."}), 200


# --- LOANS ---

def listLoans():
    bank_approval_status = request.args.get("bank_approval_status")
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
        SELECT * FROM amortization_schedule
        WHERE loan_id = %s
        ORDER BY period_number
    """, (loan_id,), fetch="all")

    loan["amortization_schedule"] = schedule
    return jsonify({"data": loan}), 200


def createLoan(sale_id):
    sale = run_query("SELECT * FROM sales WHERE sale_id = %s", (sale_id,), fetch="one")
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
    if term_months < 6 or term_months > 60:
        return jsonify({"message": "term_months must be between 6 and 60."}), 422
    if interest_rate < 0 or interest_rate > 30:
        return jsonify({"message": "interest_rate must be between 0 and 30."}), 422

    conn, cursor = get_db()
    try:
        loan_id = run_query("""
            INSERT INTO loan_details (sale_id, loan_amount, interest_rate, term_months, bank_approval_status)
            VALUES (%s,%s,%s,%s,'pending')
        """, (sale_id, loan_amount, interest_rate, term_months), conn=conn, cursor=cursor)

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
    data = request.get_json(silent=True) or {}
    bank_approval_status = data.get("bank_approval_status")

    if not bank_approval_status:
        return jsonify({"message": "bank_approval_status is required."}), 400

    if bank_approval_status not in ("approved", "rejected"):
        return jsonify({"message": "bank_approval_status must be 'approved' or 'rejected'."}), 422

    loan = run_query("""
        SELECT l.*, s.customer_id, s.sale_id
        FROM loan_details l
        JOIN sales s ON l.sale_id = s.sale_id
        WHERE l.loan_id = %s
    """, (loan_id,), fetch="one")

    if not loan:
        return jsonify({"message": "Loan not found."}), 404

    old_value = loan["bank_approval_status"]
    run_query("UPDATE loan_details SET bank_approval_status = %s WHERE loan_id = %s", (bank_approval_status, loan_id))

    audit_log(session["user"], "PUT", "loan_details", loan_id, json.dumps(old_value, default=str), json.dumps({"bank_approval_status": bank_approval_status}, default=str))

    customer = run_query("SELECT email FROM users WHERE user_id = %s", (loan["customer_id"],), fetch="one")
    customer_name = run_query("SELECT full_name FROM user_profile WHERE user_id = %s", (loan["customer_id"],), fetch="one")
    name = customer_name["full_name"] if customer_name else "Customer"

    fire_notif(user_id=loan["customer_id"], title="Loan Status Updated", message=f"Your loan for sale #{loan['sale_id']} has been {bank_approval_status}.", channel="in_app", ref_type="loan_details", ref_id=loan_id)

    if customer:
        try:
            send_loan_status(customer["email"], name, bank_approval_status, loan["sale_id"])
        except Exception:
            pass

    return jsonify({"message": f"Loan status updated to '{bank_approval_status}'."}), 200


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
            ORDER BY period_number
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
        SELECT a.*, l.sale_id
        FROM amortization_schedule a
        JOIN loan_details l ON a.loan_id = l.loan_id
        WHERE a.schedule_id = %s
    """, (schedule_id,), fetch="one")

    if not schedule:
        return jsonify({"message": "Amortization schedule entry not found."}), 404

    if schedule["status"] != "unpaid":
        return jsonify({"message": f"Entry is already '{schedule['status']}'."}), 409

    old_value = schedule["status"]
    run_query("UPDATE amortization_schedule SET status = %s WHERE schedule_id = %s", (status, schedule_id))

    fire_notif(user_id=schedule.get("user_id"), title="Amortization Updated", message=f"Amortization period #{schedule['period_number']} marked as {status}.", channel="in_app", ref_type="amortization_schedule", ref_id=schedule_id)

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

    if new_term < 6 or new_term > 60:
        return jsonify({"message": "term_months must be between 6 and 60."}), 422
    if new_rate < 0 or new_rate > 30:
        return jsonify({"message": "interest_rate must be between 0 and 30."}), 422

    conn, cursor = get_db()
    try:
        paid = run_query("""
            SELECT COALESCE(SUM(principal_component), 0) AS paid_principal,
                   COUNT(*) AS paid_count,
                   MAX(period_number) AS last_paid_period
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
