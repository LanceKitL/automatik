from flask import jsonify, request, session
from utils.log import audit_log
from conn import run_query
import json


def getAllPayments():
    
    payments = run_query("""
                        SELECT pay.payment_id, pay.sale_id, pay.schedule_id, pay.amount_paid, 
                         pay.payment_date, pay.payment_method, pay.reference, pay.recorded_by, pay.created_at 
                         from payments pay join users us on pay.recorded_by = us.user_id
                         join sales sale on pay.sale_id = sale.sale_id
                         join amortization_schedule amor_sched on pay.schedule_id = amor_sched.schedule_id
                         order by pay.payment_date asc;         
                         """, fetch="all")
    
        
    return jsonify({f"data": payments})


def getPayments(id):
    
    
    payments = run_query("""
                         SELECT * FROM payments WHERE payment_id = %s         
                         """,(id, ) ,fetch="all")   
    
    if not payments:
        return jsonify({"error":f"No data of id ({id}. Does not Exist)"}), 404
    
    return jsonify({"data": payments}), 200
    
    # unfinished
def recordPayments():
    data = request.get_json()
    
    sale_id = data.get("sale_id")
    schedule = data.get("schedule_id")
    amount_paid = data.get("amount_paid")
    payment_method = data.get("payment_method")
    recorded_by = data.get("record_by")
    
    payments = run_query("""
                          INSERT INTO payments (sale_id, schedule_id,
                          amount_paid, payment_method, recorded_by)
                          VALUES (%s, %s, %s, %s, %s)""",
                          (sale_id,schedule,amount_paid,payment_method,recorded_by))
    
    
    if not payments:
        return jsonify({"Error": "NO data has been added. Excecution failed"}), 400
    
    result = run_query ("""SELECT sales.payment_type FROM sales 
                        JOIN payments ON sales.sale_id = payments.sale_id
                        WHERE payments.sale_id = %s LIMIT 1""", (sale_id, ), fetch="one")
    
    if result == "installment":
        paid = "paid"
        upd = run_query("""UPDATE amortization_schedule
                         SET staus = %s WHERE schedule_id = %s"""
                         ,(paid,schedule))
        
    
    return


def getMyPayments(id):
    
    payments = run_query("""
                         SELECT pay.payment_id, pay.sale_id, pay.schedule_id, pay.amount_paid, 
                         pay.payment_date, pay.payment_method, pay.reference,  pay.created_at 
                         from payments pay join users us on pay.recorded_by = us.user_id
                         join sales sale on pay.sale_id = sale.sale_id
                         join amortization_schedule amor_sched on pay.schedule_id = amor_sched.schedule_id
                         where sale.customer_id = %s
                         order by  pay.payment_date asc; """
                         ,(id, ), fetch="all")
    
    if not payments:
        return({"message":f"no record for this customer id({id})"}), 400
    
    return jsonify({"data": payments}), 200


def getSalesPayments(id):
    
    payments = run_query("""
                         SELECT pay.payment_id, pay.sale_id, pay.schedule_id, pay.amount_paid, 
                         pay.payment_date, pay.payment_method, pay.reference, pay.recorded_by, pay.created_at 
                         from payments pay join users us on pay.recorded_by = us.user_id
                         join sales sale on pay.sale_id = sale.sale_id
                         join amortization_schedule amor_sched on pay.schedule_id = amor_sched.schedule_id
                         where sale.sale_id = %s
                         order by  pay.payment_date asc; """
                         ,(id, ), fetch="all")
    
    if not payments:
        return({"message":f"no record for this customer id({id})"})
    
    return jsonify({"data": payments})