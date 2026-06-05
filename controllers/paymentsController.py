from flask import jsonify, request, session
from utils.log import audit_log
from utils.notification import fire_notif
from services.mail_service import send_payment_receipt
from conn import run_query, get_db, Error
from datetime import datetime
import json


def listPayments():
    payment_method = request.args.get("payment_method")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")

    query = """
        SELECT p.*, s.sale_id, v.brand, v.model,
               cu.username AS customer_name,
               u.username AS recorded_by_name
        FROM payments p
        JOIN sales s ON p.sale_id = s.sale_id
        JOIN vehicles v ON s.vehicle_id = v.vehicle_id
        JOIN users cu ON s.customer_id = cu.user_id
        JOIN users u ON p.recorded_by = u.user_id
        WHERE 1=1
    """
    params = []

    if payment_method:
        query += " AND p.payment_method = %s"
        params.append(payment_method)
    if date_from:
        query += " AND p.payment_date >= %s"
        params.append(date_from)
    if date_to:
        query += " AND p.payment_date <= %s"
        params.append(date_to)

    query += " ORDER BY p.payment_date DESC"
    result = run_query(query, tuple(params), fetch="all")
    return jsonify({"data": result}), 200


def getPayment(payment_id):
    payment = run_query("""
        SELECT p.*, s.sale_id, v.brand, v.model,
               cu.username AS customer_name,
               u.username AS recorded_by_name
        FROM payments p
        JOIN sales s ON p.sale_id = s.sale_id
        JOIN vehicles v ON s.vehicle_id = v.vehicle_id
        JOIN users cu ON s.customer_id = cu.user_id
        JOIN users u ON p.recorded_by = u.user_id
        WHERE p.payment_id = %s
    """, (payment_id,), fetch="one")

    if not payment:
        return jsonify({"message": "Payment not found."}), 404

    return jsonify({"data": payment}), 200


def recordPayment(sale_id):
    sale = run_query("SELECT * FROM sales WHERE sale_id = %s", (sale_id,), fetch="one")
    if not sale:
        return jsonify({"message": "Sale not found."}), 404

    if sale["status"] == "cancelled":
        return jsonify({"message": "Cannot record payment for a cancelled sale."}), 400

    data = request.get_json(silent=True) or {}
    amount_paid = data.get("amount_paid")
    payment_method = data.get("payment_method")
    schedule_id = data.get("schedule_id")
    reference = data.get("reference")

    if not all([amount_paid, payment_method]):
        return jsonify({"message": "amount_paid and payment_method are required."}), 400

    try:
        amount_paid = float(amount_paid)
    except (TypeError, ValueError):
        return jsonify({"message": "amount_paid must be a number."}), 422

    if amount_paid <= 0:
        return jsonify({"message": "amount_paid must be greater than 0."}), 422

    valid_methods = ("cash", "bank_transfer", "check", "online")
    if payment_method not in valid_methods:
        return jsonify({"message": f"payment_method must be one of {valid_methods}."}), 422

    conn, cursor = get_db()
    try:
        run_query("SELECT sale_id FROM sales WHERE sale_id = %s FOR UPDATE", (sale_id,), conn=conn, cursor=cursor, fetch="one")

        if schedule_id:
            schedule = run_query("""
                SELECT a.status FROM amortization_schedule a
                JOIN loan_details l ON a.loan_id = l.loan_id
                WHERE a.schedule_id = %s AND l.sale_id = %s
            """, (schedule_id, sale_id), fetch="one", conn=conn, cursor=cursor)

            if not schedule:
                return jsonify({"message": "Schedule entry not found for this sale."}), 404

            if schedule["status"] == "paid":
                return jsonify({"message": "This schedule entry is already paid."}), 409

        payment_id = run_query("""
            INSERT INTO payments (sale_id, schedule_id, amount_paid, payment_method, payment_date, recorded_by, reference)
            VALUES (%s,%s,%s,%s,NOW(),%s,%s)
        """, (sale_id, schedule_id, amount_paid, payment_method, session["user"], reference), conn=conn, cursor=cursor)

        if schedule_id:
            run_query("UPDATE amortization_schedule SET status = 'paid' WHERE schedule_id = %s", (schedule_id,), conn=conn, cursor=cursor)

        conn.commit()

        customer = run_query("""
            SELECT u.email, u.user_id FROM users u
            JOIN sales s ON s.customer_id = u.user_id
            WHERE s.sale_id = %s
        """, (sale_id,), fetch="one")

        if customer:
            fire_notif(user_id=customer["user_id"], title="Payment Received", message=f"A payment of {amount_paid} has been recorded for sale #{sale_id}.", channel="in_app", ref_type="payments", ref_id=payment_id)

            customer_name = run_query("SELECT full_name FROM user_profile WHERE user_id = %s", (customer["user_id"],), fetch="one")
            name = customer_name["full_name"] if customer_name else "Customer"

            try:
                send_payment_receipt(customer["email"], name, amount_paid, sale_id, payment_method)
            except Exception:
                pass

        return jsonify({"payment_id": payment_id}), 201

    except Error as e:
        conn.rollback()
        return jsonify({"message": "Transaction failed.", "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


def getMyPayments():
    customer_id = session["user"]
    payments = run_query("""
        SELECT p.*, s.sale_id, v.brand, v.model
        FROM payments p
        JOIN sales s ON p.sale_id = s.sale_id
        JOIN vehicles v ON s.vehicle_id = v.vehicle_id
        WHERE s.customer_id = %s
        ORDER BY p.payment_date DESC
    """, (customer_id,), fetch="all")

    return jsonify({"data": payments}), 200


def getSalePayments(sale_id):
    sale = run_query("SELECT sale_id FROM sales WHERE sale_id = %s", (sale_id,), fetch="one")
    if not sale:
        return jsonify({"message": "Sale not found."}), 404

    payments = run_query("""
        SELECT p.*, u.username AS recorded_by_name
        FROM payments p
        JOIN users u ON p.recorded_by = u.user_id
        WHERE p.sale_id = %s
        ORDER BY p.payment_date DESC
    """, (sale_id,), fetch="all")

    return jsonify({"data": payments}), 200


def getPaymentSummary():
    year = request.args.get("year")

    query = """
        SELECT YEAR(payment_date) AS year, MONTH(payment_date) AS month, SUM(amount_paid) AS total
        FROM payments
        WHERE 1=1
    """
    params = []

    if year:
        query += " AND YEAR(payment_date) = %s"
        params.append(year)

    query += " GROUP BY YEAR(payment_date), MONTH(payment_date) ORDER BY year DESC, month DESC"
    result = run_query(query, tuple(params), fetch="all")
    return jsonify({"data": result}), 200
