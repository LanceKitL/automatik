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


def showPayments(id):
    
    
    payments = run_query("""
                         SELECT * FROM payments WHERE payment_id = %s         
                         """,(id, ) ,fetch="all")   
    
    if not payments:
        return jsonify({"error":f"No data of id ({id}. Does not Exist)"}), 404
    
    return jsonify({"data": payments}), 200



# unfinished no notification yet
def recordPayments(id):
    user = session["user"]
    data = request.get_json()
    
    sale_id = data.get("sale_id")
    schedule = data.get("schedule_id")
    amount_paid = data.get("amount_paid")
    payment_method = data.get("payment_method")

    
    payments = run_query("""
                          INSERT INTO payments (sale_id, schedule_id,
                          amount_paid, payment_method, recorded_by)
                          VALUES (%s, %s, %s, %s, %s)""",
                          (sale_id,schedule,amount_paid,payment_method,id))
    
    
    if not payments:
        return jsonify({"Error": "NO data has been added. Excecution failed"}), 400
    
    result = run_query ("""SELECT sales.payment_type FROM sales 
                         JOIN payments ON sales.sale_id = payments.sale_id
                         WHERE payments.sale_id = %s LIMIT 1""", (sale_id, ), fetch="one")
    
    if result["installment"]:
        paid = "paid"
        upd = run_query("""UPDATE amortization_schedule
                         SET staus = %s WHERE schedule_id = %s"""
                         ,(paid,schedule))
        
        loan_id = run_query("""
                             SELECT amor_sched.loan_id FROM payments 
                             JOIN amortization_schedule amor_sched 
                             ON payments.schedule_id = amor_sched.schedule_id
                             JOIN sales ON payments.sale_id = sales.sale_id
                             WHERE payments.sale_id = %s limit 1;"""
                             ,(sale_id, ), fetch="one")
        
        total_loan = run_query("""
                                 SELECT (loan.term_months * loan.monthly_amortization) AS total
                                 FROM loan_details loan JOIN amortization_schedule amor_sched
                                 ON loan.loan_id = amor_sched.loan_id
                                 JOIN sales sale ON sale.sale_id = loan.sale_id
                                 WHERE loan.loan_id = %s LIMIT 1;"""
                                 , (loan_id, ), fetch="one")
        
        total_paid = run_query("""
                                 SELECT SUM(pay.amount_paid) as total FROM payments pay
                                 JOIN sales sale ON pay.sale_id = sale.sale_id
                                 where pay.sale_id = %s LIMIT 1"""
                                 ,(sale_id, ),fetch="one")
        if (total_paid - total_loan) >= 0:
            upd = run_query("""
                             UPDATE sales sale 
                             JOIN payments pay ON pay.sale_id = sale.sale_id 
                             SET sale.status = 'completed' 
                             WHERE pay.sale_id = %s"""
                            ,(sale_id, ))
            
            upd = run_query("""
                             UPDATE vehicles JOIN sales 
                             ON vehicles.vehicle_id = sales.vehicle_id
                             SET vehicles.status = 'delivered'
                             WHERE sales.status = 'completed'; """)
            
         #   notification = run_query("""""")
        
        
    
    return


def showMyPayments(id):
    
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


def showSalesPayments(id):
    
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

def getPaymentsSummarry():
    
    payments = run_query("""
                         SELECT 
		                 IFNULL(amor_sched.month_number, 'Grand Total') AS month, 
                         IF(amor_sched.month_number IS NULL, '', GROUP_CONCAT(DISTINCT amor_sched.status)) AS schedule_statuses,
                         IF(amor_sched.month_number IS NULL, '', GROUP_CONCAT(DISTINCT sale.status)) AS sale_statuses,
                         
                         SUM(CASE WHEN amor_sched.status = 'paid' THEN pay.amount_paid ELSE 0 END) AS total_collected,
                         SUM(CASE WHEN amor_sched.status = 'unpaid' THEN amor_sched.total_due ELSE 0 END) AS total_pending,
                         SUM(CASE WHEN amor_sched.status = 'overdue' THEN amor_sched.total_due ELSE 0 END) AS total_overdue

                         FROM amortization_schedule amor_sched LEFT JOIN payments pay 
                         ON pay.schedule_id = amor_sched.schedule_id 
                         JOIN loan_details loan ON amor_sched.loan_id = loan.loan_id
                         JOIN sales sale ON loan.sale_id = sale.sale_id
                         JOIN users us ON sale.customer_id = us.user_id
                         GROUP BY amor_sched.month_number WITH ROLLUP;""")
    
    return jsonify({"data":payments})






