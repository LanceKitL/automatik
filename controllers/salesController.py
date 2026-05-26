from flask import jsonify, request, session
from utils.log import audit_log
from conn import run_query
import json


def getAllSales():
    
    sales = run_query("""
                        SELECT 	sales.sale_id,
                        vehicles.vehicle_id, vehicles.brand, vehicles.model,
                        sales.customer_id, customer_name.full_name AS customer_name,
                        sales.agent_id, agent_name.full_name AS agent_name, 
                        sales.inquiry_id, sales.payment_type, sales.status, sales.created_at
                        FROM sales JOIN vehicles ON sales.vehicle_id = vehicles.vehicle_id

                        JOIN users c_user ON sales.customer_id =  c_user.user_id
                        JOIN user_profile customer_name ON c_user.user_id = customer_name.user_id

                        JOIN users a_user ON sales.agent_id = a_user.user_id
                        JOIN user_profile agent_name ON a_user.user_id = agent_name.user_id
                        
                        GROUP BY sales.sale_id;""",
                        fetch="all")
    
    return jsonify({"result": sales})


def getSaleDetails():
    sales = run_query()
    
    return jsonify({"result": sales})
