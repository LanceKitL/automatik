from flask import jsonify, request
from conn import run_query
from dateutil.relativedelta import relativedelta

def getAllLoans():
    loans = run_query("""
        SELECT ld.*, s.payment_type, s.selling_price,
               u.email, v.brand, v.model
        FROM loan_details ld
        JOIN sales s ON ld.sale_id = s.sale_id
        JOIN users u ON s.customer_id = u.user_id
        JOIN vehicles v ON s.vehicle_id = v.vehicle_id
    """, fetch="all")

    if not loans:
        return jsonify({"message": "No loans found!"}), 404

    return jsonify({"data": loans}), 200


def getLoanById(loan_id):
    loan = run_query("""
        SELECT ld.*
        FROM loan_details ld
        WHERE ld.loan_id = %s
    """, (loan_id,), fetch="one")

    if not loan:
        return jsonify({"message": "Loan not found!"}), 404

    schedule = run_query("""
        SELECT sched.*
        FROM amortization_schedule sched
        WHERE sched.loan_id = %s 
        ORDER BY sched.due_date ASC
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
        SELECT sched.*
        FROM amortization_schedule sched
        WHERE sched.loan_id = %s 
        ORDER BY sched.due_date ASC
    """, (loan_id,), fetch="all")

    if not schedule:
        return jsonify({"message": "No schedule found!"}), 404

    return jsonify({"data": schedule}), 200


def getMyLoan(customer_id):
    loan = run_query("""
        SELECT ld.*
        FROM loan_details ld
        JOIN sales s ON ld.sale_id = s.sale_id
        WHERE s.customer_id = %s
        ORDER BY ld.loan_id DESC
    """, (customer_id,), fetch="one")

    if not loan:
        return jsonify({"message": "No loan found!"}), 404

    return jsonify({"data": loan}), 200


def updateScheduleStatus(schedule_id):
    data = request.get_json(silent=True) or {}
    status = data.get("status")

    if not status:
        return jsonify({"message": "status is required."}), 400

    run_query("""
        UPDATE amortization_schedule SET status=%s WHERE schedule_id = %s
    """, (status, schedule_id))

    return jsonify({"message": "Schedule status updated successfully!"}), 200


def getOverdueSchedules():
    overdue = run_query("""
        SELECT sched.*, ld.loan_amount, ld.interest_rate,
               u.email, v.brand, v.model
        FROM amortization_schedule sched
        JOIN loan_details ld ON sched.loan_id = ld.loan_id
        JOIN sales s ON ld.sale_id = s.sale_id
        JOIN users u ON s.customer_id = u.user_id
        JOIN vehicles v ON s.vehicle_id = v.vehicle_id
        WHERE sched.status = 'overdue'
        ORDER BY sched.due_date ASC
    """, fetch="all")

    if not overdue:
        return jsonify({"message": "No overdue schedules found!"}), 404

    return jsonify({"data": overdue}), 200