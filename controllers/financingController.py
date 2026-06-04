from flask import jsonify, request
from conn import run_query
from dateutil.relativedelta import relativedelta
from utils.notification import fire_notif

# ADMIN

def getAllLoans():
    """
    Get all loans with sale, customer, and vehicle details.
    No request body required.
    Returns:
        200: {"data": [loan objects]}
        404: {"message": "No loans found!"}
    """
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
    """
    Get a single loan by its ID, including its full amortization schedule.
    Args:
        loan_id: path parameter
    Returns:
        200: {"loan": loan_object, "schedule": [schedule_rows]}
        404: {"message": "Loan not found!"}
    """
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
    """
    Create a loan for a sale, generate amortization schedule, and optionally create an agent commission.
    Required fields: loan_amount, interest_rate, term_months
    Optional fields: down_payment (default 0), bank_name, bank_approval_status (default "pending"), agent_commission_rate (default 3.5)
    Args:
        sale_id: path parameter
    Returns:
        201: {"message": "...", "loan_id": int, "monthly_amortization": float}
        400: {"message": "loan_amount must be greater than 0"} or {"message": "term_months must be greater than 0"}
        404: {"message": "Sale not found"}
    """
    data = request.get_json(silent=True) or {}

    loan_amount = float(data.get("loan_amount", 0))
    interest_rate = float(data.get("interest_rate", 0))
    term_months = int(data.get("term_months", 0))
    down_payment = float(data.get("down_payment", 0))
    bank_name = data.get("bank_name")
    bank_approval_status = data.get("bank_approval_status", "pending")

    # Optional commission rate
    commission_rate = float(data.get("agent_commission_rate", 3.5))

    if loan_amount <= 0:
        return jsonify({"message": "loan_amount must be greater than 0"}), 400

    if term_months <= 0:
        return jsonify({"message": "term_months must be greater than 0"}), 400

    # Get sale information
    sale = run_query("""
        SELECT
            sale_id,
            sale_price,
            agent_id,
            created_at
        FROM sales
        WHERE sale_id = %s
    """, (sale_id,), fetch="one")

    if not sale:
        return jsonify({"message": "Sale not found"}), 404

    sale_date = sale["created_at"]

    # Calculate monthly payment
    if interest_rate == 0:
        monthly_amortization = round(
            loan_amount / term_months,
            2
        )
        monthly_rate = 0
    else:
        monthly_rate = interest_rate / 100 / 12

        monthly_amortization = round(
            loan_amount *
            monthly_rate /
            (1 - (1 + monthly_rate) ** (-term_months)),
            2
        )

    # Create loan record
    loan_id = run_query("""
        INSERT INTO loan_details
        (
            sale_id,
            down_payment,
            loan_amount,
            interest_rate,
            term_months,
            monthly_amortization,
            bank_name,
            bank_approval_status
        )
        VALUES
        (
            %s, %s, %s, %s,
            %s, %s, %s, %s
        )
    """, (
        sale_id,
        down_payment,
        loan_amount,
        interest_rate,
        term_months,
        monthly_amortization,
        bank_name,
        bank_approval_status
    ))

    # Generate amortization schedule
    running_balance = loan_amount

    for n in range(1, term_months + 1):

        if interest_rate == 0:
            interest = 0
            principal = monthly_amortization
        else:
            interest = round(
                running_balance * monthly_rate,
                2
            )

            principal = round(
                monthly_amortization - interest,
                2
            )

        running_balance = round(
            running_balance - principal,
            2
        )

        # Avoid negative balance on final payment
        if n == term_months:
            running_balance = 0

        due_date = sale_date + relativedelta(months=n)

        run_query("""
            INSERT INTO amortization_schedule
            (
                loan_id,
                month_number,
                due_date,
                principal,
                interest,
                total_due,
                running_balance,
                status
            )
            VALUES
            (
                %s, %s, %s, %s,
                %s, %s, %s, %s
            )
        """, (
            loan_id,
            n,
            due_date,
            principal,
            interest,
            monthly_amortization,
            running_balance,
            "unpaid"
        ))

    # Create agent commission record
    if sale.get("agent_id"):

        existing_commission = run_query("""
            SELECT commission_id
            FROM agent_commissions
            WHERE sale_id = %s
        """, (sale_id,), fetch="one")

        if not existing_commission:

            commission_amount = round(
                float(sale["sale_price"]) *
                commission_rate / 100,
                2
            )

            run_query("""
                INSERT INTO agent_commissions
                (
                    sale_id,
                    agent_id,
                    rate_applied,
                    commission_amount,
                    is_paid
                )
                VALUES
                (
                    %s, %s, %s, %s, %s
                )
            """, (
                sale_id,
                sale["agent_id"],
                commission_rate,
                commission_amount,
                0
            ))

    return jsonify({
        "message": "Loan created and amortization schedule generated successfully.",
        "loan_id": loan_id,
        "monthly_amortization": monthly_amortization
    }), 201

def updateLoanStatus(loan_id):
    """
    Update the bank approval status of a loan.
    Required fields: bank_approval_status
    Args:
        loan_id: path parameter
    Returns:
        200: {"message": "Loan status updated successfully!"}
        400: {"message": "bank_approval_status is required."}
    """
    data = request.get_json(silent=True) or {}
    bank_approval_status = data.get("bank_approval_status")

    if not bank_approval_status:
        return jsonify({"message": "bank_approval_status is required."}), 400

    run_query("""
        UPDATE loan_details SET bank_approval_status=%s WHERE loan_id = %s
    """, (bank_approval_status, loan_id))

    return jsonify({"message": "Loan status updated successfully!"}), 200


def getLoanSchedule(loan_id):
    """
    Get the full amortization schedule for a loan, ordered by due date ascending.
    No request body required.
    Args:
        loan_id: path parameter
    Returns:
        200: {"data": [schedule_rows]}
        404: {"message": "No schedule found!"}
    """
    schedule = run_query("""
        SELECT amortization_schedule.*
        FROM amortization_schedule
        WHERE amortization_schedule.loan_id = %s 
        ORDER BY amortization_schedule.due_date ASC
    """, (loan_id,), fetch="all")

    if not schedule:
        return jsonify({"message": "No schedule found!"}), 404

    return jsonify({"data": schedule}), 200


def updateScheduleStatus(schedule_id):
    """
    Mark an amortization schedule row as paid/overdue and notify the customer.
    Required fields: status
    Args:
        schedule_id: path parameter
    Returns:
        200: {"message": "Schedule status updated successfully!"}
        400: {"message": "status is required."}
        404: {"message": "Schedule not found!"}
    """
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

    fire_notif(
        user_id=schedule["customer_id"],
        title="Payment Schedule Updated",
        message=f"Your payment schedule for month {schedule['month_number']} has been marked as {status}.",
        channel="in_app",
        ref_type="amortization_schedule",
        ref_id=schedule_id
    )

    return jsonify({"message": "Schedule status updated successfully!"}), 200


def getOverdueSchedules():
    """
    Get all overdue amortization schedule rows with joined loan, sale, customer, and vehicle details.
    No request body required.
    Returns:
        200: {"data": [overdue_rows]}
        404: {"message": "No overdue schedules found!"}
    """
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
    """
    Recompute amortization schedule after rate/term change, preserving paid periods.
    Uses remaining_balance and start_period to avoid regenerating already-paid rows.
    Required fields: interest_rate, term_months
    Args:
        loan_id: path parameter
    Returns:
        200: {"message": "Amortization recomputed successfully!"}
        400: {"message": "interest_rate and term_months are required."}
             or {"message": "All periods are already paid."}
        404: {"message": "Loan not found!"}
    """
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

    paid = run_query("""
        SELECT COALESCE(SUM(principal), 0) AS paid_principal,
               COUNT(*) AS paid_count,
               MAX(month_number) AS last_paid_period
        FROM amortization_schedule
        WHERE loan_id = %s AND status = 'paid'
    """, (loan_id,), fetch="one")

    remaining_balance = float(loan["loan_amount"]) - float(paid["paid_principal"])
    start_period = int(paid["last_paid_period"] or 0) + 1
    remaining_months = term_months - int(paid["paid_count"])

    if remaining_months <= 0:
        return jsonify({"message": "All periods are already paid."}), 400

    monthly_rate = interest_rate / 100 / 12
    monthly_amortization = remaining_balance * monthly_rate / (1 - (1 + monthly_rate) ** -remaining_months)

    run_query("""
        UPDATE loan_details SET interest_rate=%s, term_months=%s, monthly_amortization=%s
        WHERE loan_id = %s
    """, (interest_rate, term_months, monthly_amortization, loan_id))

    run_query("""
        DELETE FROM amortization_schedule 
        WHERE loan_id = %s AND status = 'unpaid'
    """, (loan_id,))

    sale_date = loan["sale_date"]
    running_balance = remaining_balance

    for i in range(remaining_months):
        period = start_period + i
        interest = running_balance * monthly_rate
        principal = monthly_amortization - interest
        running_balance -= principal
        due_date = sale_date + relativedelta(months=period)

        run_query("""
            INSERT INTO amortization_schedule 
            (loan_id, month_number, due_date, principal, interest, total_due, running_balance, status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (loan_id, period, due_date, principal, interest, monthly_amortization, running_balance, "unpaid"))

    return jsonify({"message": "Amortization recomputed successfully!"}), 200


# CUSTOMER

def getMyLoan(customer_id):
    """
    Get the current customer's most recent loan with its full amortization schedule.
    No request body required — customer_id comes from the session.
    Args:
        customer_id: from session (set by middleware)
    Returns:
        200: {"loan": loan_object, "schedule": [schedule_rows]}
        404: {"message": "No loan found!"}
    """
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
