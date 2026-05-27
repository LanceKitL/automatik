from flask import jsonify, request, session
from utils.log import audit_log
from conn import run_query
import json


def indexSales():
    
    sales = run_query("""
                        SELECT sales.sale_id,
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


def indexSalesDetails(id):

    sales = run_query("""
                    SELECT 
                    sales.*, 
                    sales_contracts.contract_id, 
                    sales_contracts.contract_url, 
                    sales_contracts.status,
                    

                    CASE WHEN sales.payment_type = 'Cash' THEN NULL ELSE loan_details.loan_id END AS loan_id,
                    CASE WHEN sales.payment_type = 'Cash' THEN NULL ELSE loan_details.down_payment END AS down_payment,
                    CASE WHEN sales.payment_type = 'Cash' THEN NULL ELSE loan_details.loan_amount END AS loan_amount,
                    

                    payment_totals.Totals_paid, 
                    
                
                    ins.insurance_id, 
                    ins.provider_name, 
                    ins.coverage_type,
                    doc.document_id,
                    doc.document_type, 
                    doc.file_url

                    FROM sales 
                    JOIN sales_contracts ON sales.sale_id = sales_contracts.sale_id
                    LEFT JOIN loan_details ON loan_details.sale_id = sales.sale_id


                    LEFT JOIN (
                        SELECT sale_id, SUM(amount_paid) AS Totals_paid
                        FROM payments
                        GROUP BY sale_id
                    ) AS payment_totals ON sales.sale_id = payment_totals.sale_id


                    LEFT JOIN (
                        SELECT sale_id, 
                            MAX(insurance_id) AS insurance_id, 
                            MAX(provider_name) AS provider_name, 
                            MAX(coverage_type) AS coverage_type
                        FROM insurance_records
                        GROUP BY sale_id
                    ) AS ins ON sales.sale_id = ins.sale_id

                    LEFT JOIN (
                        SELECT sale_id, 
                            MAX(document_id) AS document_id, 
                            MAX(document_type) AS document_type, 
                            MAX(file_url) AS file_url
                        FROM documents
                        GROUP BY sale_id
                    ) AS doc ON sales.sale_id = doc.sale_id;""", fetch="all")
    
    return jsonify({"result": sales})


def createSales():
    pass

def updateSales(id):
    pass

def deleteSales(id):
    pass
