from flask import jsonify, request
from conn import run_query
from dateutil.relativedelta import relativedelta

<<<<<<< HEAD
=======

>>>>>>> 3276fd1 (changes in financing/documents)

# ADMIN

def getAllLoans():
    loans = run_query("""
        SELECT loan_details.*, sales.payment_type, sales.selling_price,
            customer_details.customer_number, vehicles.brand, vehicles.model
        FROM loan_details
        JOIN sales ON loan_details.sale_id = sales.sale_id
        JOIN customer_details ON sales.customer_id = customer_details.user_id
        JOIN vehicles ON sales.vehicle_id = vehicles.vehicle_id
    """, fetch="all")

    if not loans:
        return jsonify({"message": "No loans found!"}), 404

    return jsonify({"data": loans}), 200


def getLoanById(loan_id):
    loan = run_query("""
        SELECT loan_details.*
        FROM loan_details
        WHERE loan_details.loan_id = %s
    """, (loan_id,), fetch="one")

    if not loan:
        return jsonify({"message": "Loan not found!"}), 404

    schedule = run_query("""
        SELECT amortization_schedule.*
        FROM amortization_schedule
        WHERE amortization_schedule.loan_id = %s 
        ORDER BY amortization_schedule.due_date ASC
    """, (loan_id,), fetch="all")

    return jsonify({"loan": loan, "schedule": schedule}), 200


def createLoan(sale_id):
    data = request.get_json(silent=True) or {}
    loan_amount = data.get("loan_amount")
    interest_rate = data.get("interest_rate")
    term_months = data.get("term_months")
    down_payment = data.get("down_payment", 0)
    bank_name = data.get("bank_name", None)
    bank_approval_status = data.get("bank_approval_status", "pending")

    if not loan_amount or not interest_rate or not term_months:
        return jsonify({"message": "loan_amount, interest_rate, and term_months are required."}), 400

    monthly_rate = interest_rate / 100 / 12
    monthly_amortization = loan_amount * monthly_rate / (1 - (1 + monthly_rate) ** -term_months)

    loan_id = run_query("""
        INSERT INTO loan_details 
        (sale_id, down_payment, loan_amount, interest_rate, term_months, monthly_amortization, bank_name, bank_approval_status) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (sale_id, down_payment, loan_amount, interest_rate, term_months, monthly_amortization, bank_name, bank_approval_status))

    sale = run_query("SELECT created_at FROM sales WHERE sale_id = %s", (sale_id,), fetch="one")
    sale_date = sale["created_at"]

    running_balance = loan_amount
    for n in range(1, term_months + 1):
        interest = running_balance * monthly_rate
        principal = monthly_amortization - interest
        running_balance -= principal
        due_date = sale_date + relativedelta(months=n)
        status = "unpaid"

        run_query("""
            INSERT INTO amortization_schedule 
            (loan_id, month_number, due_date, principal, interest, total_due, running_balance, status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (loan_id, n, due_date, principal, interest, monthly_amortization, running_balance, status))

    return jsonify({"message": "Loan created and amortization schedule generated!"}), 201


def updateLoanStatus(loan_id):
    data = request.get_json(silent=True) or {}
    bank_approval_status = data.get("bank_approval_status")

    if not bank_approval_status:
        return jsonify({"message": "bank_approval_status is required."}), 400

    run_query("""
        UPDATE loan_details SET bank_approval_status=%s WHERE loan_id = %s
    """, (bank_approval_status, loan_id))

    return jsonify({"message": "Loan status updated successfully!"}), 200


def getLoanSchedule(loan_id):
    schedule = run_query("""
        SELECT amortization_schedule.*
        FROM amortization_schedule
        WHERE amortization_schedule.loan_id = %s 
        ORDER BY amortization_schedule.due_date ASC
    """, (loan_id,), fetch="all")

    if not schedule:
        return jsonify({"message": "No schedule found!"}), 404

    return jsonify({"data": schedule}), 200


def getMyLoan(customer_id):
    loan = run_query("""
        SELECT loan_details.*
        FROM loan_details
        JOIN sales ON loan_details.sale_id = sales.sale_id
        WHERE sales.customer_id = %s
        ORDER BY loan_details.loan_id DESC
    """, (customer_id,), fetch="one")

    if not loan:
        return jsonify({"message": "No loan found!"}), 404

    schedule = run_query("""
        SELECT amortization_schedule.*
        FROM amortization_schedule
        WHERE amortization_schedule.loan_id = %s
        ORDER BY amortization_schedule.due_date ASC
    """, (loan["loan_id"],), fetch="all")

    return jsonify({"loan": loan, "schedule": schedule}), 200


def updateScheduleStatus(schedule_id):
    data = request.get_json(silent=True) or {}
    status = data.get("status")

    if not status:
        return jsonify({"message": "status is required."}), 400

    schedule = run_query("""
        SELECT amortization_schedule.*, loan_details.sale_id,
               sales.customer_id
        FROM amortization_schedule
        JOIN loan_details ON amortization_schedule.loan_id = loan_details.loan_id
        JOIN sales ON loan_details.sale_id = sales.sale_id
        WHERE amortization_schedule.schedule_id = %s
    """, (schedule_id,), fetch="one")

    if not schedule:
        return jsonify({"message": "Schedule not found!"}), 404

    run_query("""
        UPDATE amortization_schedule SET status=%s WHERE schedule_id = %s
    """, (status, schedule_id))

    from utils.notification import create_notification
    create_notification(
        user_id=schedule["customer_id"],
        title="Payment Schedule Updated",
        message=f"Your payment schedule for month {schedule['month_number']} has been marked as {status}.",
        channel="in_app",
        ref_type="amortization_schedule",
        ref_id=schedule_id
    )

    return jsonify({"message": "Schedule status updated successfully!"}), 200


def getOverdueSchedules():
    overdue = run_query("""
        SELECT amortization_schedule.*, loan_details.loan_amount, loan_details.interest_rate,
               users.email, vehicles.brand, vehicles.model,
               customer_details.customer_number
        FROM amortization_schedule
        JOIN loan_details ON amortization_schedule.loan_id = loan_details.loan_id
        JOIN sales ON loan_details.sale_id = sales.sale_id
        JOIN users ON sales.customer_id = users.user_id
        JOIN customer_details ON sales.customer_id = customer_details.user_id
        JOIN vehicles ON sales.vehicle_id = vehicles.vehicle_id
        WHERE amortization_schedule.status = 'overdue'
        ORDER BY amortization_schedule.due_date ASC
    """, fetch="all")

    if not overdue:
        return jsonify({"message": "No overdue schedules found!"}), 404

    return jsonify({"data": overdue}), 200


def computeAmortization(loan_id):
    data = request.get_json(silent=True) or {}
    interest_rate = data.get("interest_rate")
    term_months = data.get("term_months")

    if not interest_rate or not term_months:
        return jsonify({"message": "interest_rate and term_months are required."}), 400

    loan = run_query("""
        SELECT loan_details.*, sales.created_at as sale_date
        FROM loan_details
        JOIN sales ON loan_details.sale_id = sales.sale_id
        WHERE loan_details.loan_id = %s
    """, (loan_id,), fetch="one")

    if not loan:
        return jsonify({"message": "Loan not found!"}), 404

    monthly_rate = interest_rate / 100 / 12
    monthly_amortization = loan["loan_amount"] * monthly_rate / (1 - (1 + monthly_rate) ** -term_months)

    run_query("""
        UPDATE loan_details SET interest_rate=%s, term_months=%s, monthly_amortization=%s
        WHERE loan_id = %s
    """, (interest_rate, term_months, monthly_amortization, loan_id))

    run_query("""
        DELETE FROM amortization_schedule 
        WHERE loan_id = %s AND status = 'unpaid'
    """, (loan_id,))

    sale_date = loan["sale_date"]
    running_balance = loan["loan_amount"]
    for n in range(1, term_months + 1):
        interest = running_balance * monthly_rate
        principal = monthly_amortization - interest
        running_balance -= principal
        due_date = sale_date + relativedelta(months=n)
        status = "unpaid"

        run_query("""
            INSERT INTO amortization_schedule 
            (loan_id, month_number, due_date, principal, interest, total_due, running_balance, status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (loan_id, n, due_date, principal, interest, monthly_amortization, running_balance, status))

    return jsonify({"message": "Amortization recomputed successfully!"}), 200
<<<<<<< HEAD
=======



# CUSTOMER

def getMyLoan(customer_id):
    loan = run_query("""
        SELECT loan_details.*
        FROM loan_details
        JOIN sales ON loan_details.sale_id = sales.sale_id
        WHERE sales.customer_id = %s
        ORDER BY loan_details.loan_id DESC
    """, (customer_id,), fetch="one")

    if not loan:
        return jsonify({"message": "No loan found!"}), 404

    schedule = run_query("""
        SELECT amortization_schedule.*
        FROM amortization_schedule
        WHERE amortization_schedule.loan_id = %s
        ORDER BY amortization_schedule.due_date ASC
    """, (loan["loan_id"],), fetch="all")

    return jsonify({"loan": loan, "schedule": schedule}), 200
>>>>>>> 3276fd1 (changes in financing/documents)
