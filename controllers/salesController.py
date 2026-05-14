from flask import request, jsonify
from conn import run_query

def searchSales (params):
    res = run_query('SELECT * FROM sales'
    'WHERE payment_type LIKE %s OR status LIKE %s',)

    if not res:
        return jsonify ({"message": "Sale not found"})
    
    return jsonify ({"message": res})

def createSale():
    data = request.get_json()
    sale_id = data.get("sale_id")
    vehicle_id = data.get("vehicle_id")
    customer_id = data.get("customer_id")
    agent_id = data.get("agent_id")
    inquiry_id = data.get("inquiry_id")
    selling_price = data.get("selling_price")
    payment_type = data.get("payment_type")
    sale_date = data.get("sale_date")
    status = data.get("status")
    created_at = data.get("created_at")

    sale = run_query(""" 
                    INSERT INTO sales 
                    (sale_id, vehicle_id, customer_id, agent_id, inquiry_id, selling_price,payment_type, sale_date, status, 
                    created_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """, 
                    (sale_id, vehicle_id, customer_id, agent_id, inquiry_id, selling_price, payment_type,sale_date,status, 
                     created_at ))
    
    if not sale:
        return jsonify({"message": "Adding did not execute succesfully"}), 400
    
    return jsonify ({"message": "Sale added succesfully"}), 200

def updateSale(id):
    data = request.get_json()

    vehicle_id = data.get("vehicle_id")
    customer_id = data.get("customer_id")
    agent_id = data.get("agent_id")
    inquiry_id = data.get("inquiry_id")
    selling_price = data.get("selling_price")
    payment_type = data.get("payment_type")
    sale_date = data.get("sale_date")
    status = data.get("status")

    sale = run_query(""" 
                    UPDATE sales 
                    SET vehicle_id = %s, customer_id = %s, agent_id = %s, inquiry_id = %s, selling_price = %s, payment_type = %s, 
                    sale_date = %s, status = %s
                    WHERE sale_id = %s
                    """, 
                    (vehicle_id, customer_id, agent_id, inquiry_id, selling_price, payment_type,sale_date,status, id))
    
    if not sale:
        return jsonify({"message": "Updating did not execute succesfully"}), 400
    
    return jsonify ({"message": "Sale updated succesfully"}), 200

def deleteSale(id):
    sale = run_query("""
                    DELETE FROM sales 
                    WHERE sale_id = %s 
                    """, (id, ))
    
    if not sale:
        return jsonify({"message": "Deleting did not execute succesfully"}), 400
    
    return jsonify ({"message": "Sale deleted succesfully"}), 200