from flask import jsonify, request, session
from utils.log import audit_log
from conn import run_query, get_db, pool ,Error
import json

#-------------------------------------SALES------------------------------------------------------------------
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
    data = request.get_json(silent=True) or {}
    
    Sales_fields = {
        "vehicle_id": data.get("vehicle_id"),
        "customer_id": data.get("customer_id"),
        "agent_id": data.get("agent_id"),
        "inquiry_id": data.get("inquiry_id"),
        "selling_price": data.get("selling_price"),
        "payment_type": data.get("payment_type")
    }
    INPUT_FIELDS = []
    PLACEHOLDERS = []
    INPUT_DATA = []

    for field_name, value in Sales_fields.items():
        if value is not None:
            # append the ff input fields
            INPUT_FIELDS.append(field_name)
            PLACEHOLDERS.append("%s")
            INPUT_DATA.append(value)
    
    
    # The vehicle, customer, agent id's are required, also the selling price
    if not "vehicle_id" in INPUT_FIELDS:
        return jsonify({"message": "vehicle_id is required."}), 400
    if not "customer_id" in INPUT_FIELDS:
        return jsonify({"message": "customer_id is required."}), 400
    if not "agent_id" in INPUT_FIELDS:
        return jsonify({"message": "agent_id is required."}), 400
    if not "selling_price" in INPUT_FIELDS:
        return jsonify({"message": "selling_price is required."}), 400
 
    conn = pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    
    
    
    try:
        vehicle = data.get("vehicle_id")
        vehicle_validation = run_query("SELECT status FROM vehicles WHERE vehicle_id = %s",
                                            (vehicle, ), fetch="one", conn=conn, cursor=cursor)
        
        if not vehicle_validation:
            conn.rollback()
            return jsonify ({"message": "vehicles are maybe unvailable or reserve or does not exist"}), 400
        
        query = f"""
                INSERT INTO sales ({", ".join(INPUT_FIELDS)}, status ,sale_date, created_at)
                VALUES ({", ".join(PLACEHOLDERS)}, 'pending' ,current_timestamp(), current_timestamp())
                """
        sales = run_query(query, INPUT_DATA, conn=conn, cursor=cursor)

        if not sales: 
            conn.rollback()
            return jsonify({"message": "adding did not execute successfully."}), 400
        
        
        # for updating the vehicles
        if data.get("payment_type") == "installment":
            
            upd = run_query(""" UPDATE vehicles
                            SET status = 'reserved' WHERE vehicle_id = %s""" ,
                            (vehicle,), conn=conn, cursor=cursor)
            
            
            
            
            loan_fields = {
                "sale_id": data.get("sale_id"),
                "down_payment": data.get("down_payment"),
                "loan_amount": data.get("loan_amount"),
                "interest_rate": data.get("interest_rate"),
                "terms_months": data.get("terms_months"),
                "monthly_amortization": data.get("monthly_amortization"),
                "bank_name": data.get("bank_name")
                
            }
            
            LOAN_INPUT_FIELDS = []
            LOAN_PLACEHOLDERS = []
            LOAN_INPUT_DATA = []
            
            for field_name, value in loan_fields.items():
                if value is not None:
                    # append the ff input fields
                    LOAN_INPUT_FIELDS.append(field_name)
                    LOAN_PLACEHOLDERS.append("%s")
                    LOAN_INPUT_DATA.append(value)
            
            # The sale id, down payments, loan ammount are required, not sure about the banks
            if not "sale_id" in LOAN_INPUT_FIELDS:
                conn.rollback()
                return jsonify({"message": "sale_id is required."}), 400
            if not "down_payment" in LOAN_INPUT_FIELDS:
                conn.rollback()
                return jsonify({"message": "down_payment is required."}), 400
            if not "loan_amount" in LOAN_INPUT_FIELDS:
                conn.rollback()
                return jsonify({"message": "loan_amount is required."}), 400
            if not "bank_name" in LOAN_INPUT_FIELDS:
                conn.rollback()
                return jsonify({"message": "bank_name is required."}), 400
            
            query = f"""
                INSERT INTO loan_details ({", ".join(LOAN_INPUT_FIELDS)}, bank_approval_status, created_at)
                VALUES ({", ".join(LOAN_PLACEHOLDERS)}, 'pending', current_timestamp())
                """
            loan = run_query(query, LOAN_INPUT_DATA, conn=conn, cursor=cursor )
            
            if not loan: 
                return jsonify({"message": "adding did not execute successfully."}), 400
            
         
            return jsonify({"message":"executed properly "})
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"Transaction failed: {str(e)}"}), 400
    finally:
        cursor.close()
        conn.close()
    return jsonify({"message": "New sales added successfully!"}), 200

    


def updateSales(id):
    conn,cursor = get_db()
    data = request.get_json(silent=True) or {}
    
    sale_id = data.get("sale_id")
    status = data.get("status")
    
    upd = run_query(""" UPDATE sales
                     SET status = %s WHERE sale_id = %s """,
                     (status, sale_id))
    
    if not upd:
        return jsonify({"message": "execution failed"})
    
 
    audit_log(
        id = session["user"], 
        action="PUT", 
        tablename="sales",
        record_id= sale_id,
        new_value= status,
        conn=conn,
        cursor=cursor
    )
    
    return jsonify({"message": "updated succesfully"})


def showMySales(id):

    user_id = session["user"]
    sales = run_query("""SELECT sales.sale_id, 
                         vehicles.vehicle_id, vehicles.brand, vehicles.model, vehicles.color, vehicles.body_type
                         ,sales_contracts.contract_id, sales_contracts.contract_url, sales_contracts.status
                         FROM users JOIN sales ON users.user_id = sales.customer_id
                         JOIN vehicles ON sales.vehicle_id = vehicles.vehicle_id
                         JOIN sales_contracts ON sales.sale_id = sales_contracts.sale_id
                          WHERE users.user_id = %s GROUP BY sales.sale_id;""",
                          (user_id, ), fetch="all")


    return jsonify({"message": sales})

def showMySalesDetail(id):
    user_id = session["user"]
    sales = run_query("""SELECT 
                        sales.*, 
                        
                        -- These will now all automatically be NULL if the sale is 'pending'
                        sales_contracts.contract_id, 
                        sales_contracts.contract_url, 
                        sales_contracts.status AS contract_status,
                        
                        loan_details.loan_id,
                        loan_details.down_payment,
                        loan_details.loan_amount,
                        
                        payment_totals.Totals_paid, 
                        
                        ins.insurance_id, 
                        ins.provider_name, 
                        ins.coverage_type,
                        
                        doc.document_id,
                        doc.document_type, 
                        doc.file_url

                        FROM sales 


                        LEFT JOIN sales_contracts 
                            ON sales.sale_id = sales_contracts.sale_id 
                            AND sales.status != 'pending'


                        LEFT JOIN loan_details 
                            ON loan_details.sale_id = sales.sale_id 
                            AND sales.status != 'pending'
                            AND sales.payment_type != 'Cash'


                        LEFT JOIN (
                            SELECT sale_id, SUM(amount_paid) AS Totals_paid
                            FROM payments
                            GROUP BY sale_id
                        ) AS payment_totals 
                            ON sales.sale_id = payment_totals.sale_id 
                            AND sales.status != 'pending'


                        LEFT JOIN (
                            SELECT sale_id, 
                                MAX(insurance_id) AS insurance_id, 
                                MAX(provider_name) AS provider_name, 
                                MAX(coverage_type) AS coverage_type
                            FROM insurance_records
                            GROUP BY sale_id
                        ) AS ins 
                            ON sales.sale_id = ins.sale_id 
                            AND sales.status != 'pending'


                        LEFT JOIN (
                            SELECT sale_id, 
                                MAX(document_id) AS document_id, 
                                MAX(document_type) AS document_type, 
                                MAX(file_url) AS file_url
                            FROM documents
                            GROUP BY sale_id
                        ) AS doc 
                            ON sales.sale_id = doc.sale_id 
                            AND sales.status != 'pending'


                        JOIN users ON sales.customer_id = users.user_id

                        WHERE users.user_id = %s;""",
                        (user_id, ), fetch="all")
    
    return jsonify({"messsage": sales})

#---------------------------------------SALES_CONTRACTS------------------------------------------------------   
def indexSalesContracts():
    
    run_query("""SELECT sales_contracts.contract_id, sales_contracts.contract_url, sales_contracts.status
                    FROM sales_contracts GROUP BY  sales_contracts.contract_id;
                    """, fetch="all")
    
    return ""



def createSalesContracts(id):
    
 data = request.get_json(silent=True) or {}
    
 user_id = session["user"]
    
 SalesContracts_fields = {
       
        "sale_id": data.get("sale_id"),
        "contracts_url": data.get("contracts_url")
    }
 
 INPUT_FIELDS = []
 PLACEHOLDERS = []
 INPUT_DATA = []

 for field_name, value in SalesContracts_fields.items():
        if value is not None:
            # append the ff input fields
            INPUT_FIELDS.append(field_name)
            PLACEHOLDERS.append("%s")
            INPUT_DATA.append(value)
    
    
 if not "sale_id" in INPUT_FIELDS:
        return jsonify({"message": "sale_id is required."}), 400
 
 if not "contracts_url" in INPUT_FIELDS:
        return jsonify({"message": "contracts_url is required."}), 400

 query = f"""
                INSERT INTO sales_contracts ({", ".join(INPUT_FIELDS)}, status, created_at  )
                VALUES ({", ".join(PLACEHOLDERS)}, 'draft' ,current_timestamp())
                """
 sales = run_query(query, INPUT_DATA)
    
 if not sales:
     return jsonify({"message": "Execution failed"}), 400
    
 return jsonify({"message": "Creation Complete"})



def updateSalesContracts():
 data = request.get_json(silent=True) or {}
    
 user_id = session["user"]
 
 
 status = data.get("status")
 sale_id = data.get("sale_id")
 
 salescontracts = run_query("""UPDATE sales_contracts SET
                            status = %s, signed_at = current_timestamp(), reviewed_by = %s
                            WHERE sale_id = %s""",
                            (status,user_id, sale_id ))
 
 if not salescontracts:
     return jsonify({"message": "Execution failed"}), 400  
    
 return jsonify({"message": "salescontracts"})

