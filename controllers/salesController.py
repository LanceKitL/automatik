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


def indexSalesDetails():

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
        vehicle_validation = run_query("SELECT status FROM vehicles WHERE vehicle_id = %s;",
                                            (vehicle, ), fetch="one", conn=conn, cursor=cursor)
        
        if not vehicle_validation:
            conn.rollback()
            return jsonify ({"message": "vehicles are maybe unvailable or reserve or does not exist"}), 400
        
        query = f"""
                INSERT INTO sales ({", ".join(INPUT_FIELDS)}, status ,sale_date, created_at)
                VALUES ({", ".join(PLACEHOLDERS)}, 'pending' ,current_timestamp(), current_timestamp());
                """
        sales = run_query(query, INPUT_DATA, conn=conn, cursor=cursor)

        if not sales: 
            conn.rollback()
            return jsonify({"message": "adding did not execute successfully."}), 400
        
        
        # for updating the vehicles
        if data.get("payment_type") == "installment":
            
            upd = run_query(""" UPDATE vehicles
                            SET status = 'reserved' WHERE vehicle_id = %s;""" ,
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
                VALUES ({", ".join(LOAN_PLACEHOLDERS)}, 'pending', current_timestamp());
                """
            loan = run_query(query, LOAN_INPUT_DATA, conn=conn, cursor=cursor )
            
            if not loan: 
                return jsonify({"message": "adding did not execute successfully."}), 400
            
         
            return jsonify({"message":"executed properly "})
        conn.commit()
        
        audit_log(
            id = session["user"], 
            action="POST", 
            tablename="sales",
            record_id= sales,
            new_value= json.dumps(Sales_fields, default=str),
            conn=conn,
            cursor=cursor
        )
        
        
    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"Transaction failed: {str(e)}"}), 400
    finally:
        cursor.close()
        conn.close()
    return jsonify({"message": "New sales added successfully!"}), 200

    


def updateSales(sale_id):
    conn, cursor = get_db()
    data = request.get_json(silent=True) or {}

    status = data.get("status")

    upd = run_query(""" UPDATE sales
                     SET status = %s WHERE sale_id = %s """,
                     (status, sale_id), conn=conn, cursor=cursor)

    if not upd:
        return jsonify({"message": "execution failed"}), 400

    try:
        conn.commit()

        audit_log(
            id=session["user"],
            action="PUT",
            tablename="sales",
            record_id=sale_id,
            new_value=status,
            conn=conn,
            cursor=cursor,
        )

    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "updated successfully"}), 200


def showMySales():

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

def showMySalesDetail():
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


def createSalesContracts():
    
 data = request.get_json(silent=True) or {}
    
    
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
                VALUES ({", ".join(PLACEHOLDERS)}, 'draft' ,current_timestamp());
                """
 sales = run_query(query, INPUT_DATA)
    
 if not sales:
     return jsonify({"message": "Execution failed"}), 400
 
 audit_log(
            id=session["user"],
            action="POST",
            tablename="sales_contracts",
            record_id=sales,
            new_value=json.dumps(SalesContracts_fields, default=str),
        )
    
 return jsonify({"message": "Creation Complete"})



def updateSalesContracts():
 data = request.get_json(silent=True) or {}
    
 user_id = session["user"]
 
 
 status = data.get("status")
 sale_id = data.get("sale_id")
 
 salescontracts = run_query("""UPDATE sales_contracts SET
                            status = %s, signed_at = current_timestamp(), reviewed_by = %s
                            WHERE sale_id = %s;""",
                            (status,user_id, sale_id ))
 
 if not salescontracts:
     return jsonify({"message": "Execution failed"}), 400
 
 audit_log(
            id=session["user"],
            action="PUT",
            tablename="sales_contracts",
            record_id=sale_id,
            new_value=status
        )

    
 return jsonify({"message": "salescontracts"})


#---------------------------------------INSURANCE_RECORDS------------------------------------------------------

def indexInsuranceRecords():
    insurance_records = run_query("""SELECT insurance.insurance_id, 
								  vehicles.vehicle_id,  vehicles.vin, vehicles.brand, vehicles.model,
								  insurance.sale_id, 
                                  users.user_id, user_profile.full_name, 
                                  insurance.provider_name, insurance.policy_number, insurance.coverage_type 
                                  FROM insurance_records insurance JOIN sales ON insurance.sale_id = sales.sale_id
                                  JOIN vehicles ON sales.vehicle_id = vehicles.vehicle_id
                                  JOIN users ON sales.customer_id = users.user_id
                                  JOIN user_profile ON  users.user_id = user_profile.user_id
                                  ;""", fetch="all")
    return jsonify({"message": insurance_records})

def createInsuranceRecord():
    data = request.get_json(silent=True) or {}
    
    Insurance_fields = {
        "sale_id": data.get("sale_id"),
        "provider_name": data.get("provider_name"),
        "policy_number": data.get("policy_number"),
        "coverage_type": data.get("coverage_type"),
    }
    
    INPUT_FIELDS = []
    PLACEHOLDERS = []
    INPUT_DATA = []

    for field_name, value in Insurance_fields.items():
        if value is not None:
            # append the ff input fields
            INPUT_FIELDS.append(field_name)
            PLACEHOLDERS.append("%s")
            INPUT_DATA.append(value)
    
    
    if not "sale_id" in INPUT_FIELDS:
        return jsonify({"message": "sale_id is required."}), 400
    if not "provider_name" in INPUT_FIELDS:
        return jsonify({"message": "provider_name is required."}), 400
    if not "policy_number" in INPUT_FIELDS:
        return jsonify({"message": "policy_number is required."}), 400
    if not "coverage_type" in INPUT_FIELDS:
        return jsonify({"message": "coverage_type is required."}), 400
   

    sale_row = run_query("SELECT sale_id, vehicle_id, customer_id FROM sales WHERE sale_id = %s", 
                         (Insurance_fields["sale_id"],), fetch="one")
    if not sale_row:
            return jsonify({"message": "Invalid sale_id. The sale does not exist."}), 400

        # ensure that vehicle_id and customer_id are included 
    if "vehicle_id" not in INPUT_FIELDS:
            INPUT_FIELDS.append("vehicle_id")
            PLACEHOLDERS.append("%s")
            INPUT_DATA.append(sale_row.get("vehicle_id"))
    if "customer_id" not in INPUT_FIELDS:
            INPUT_FIELDS.append("customer_id")
            PLACEHOLDERS.append("%s")
            INPUT_DATA.append(sale_row.get("customer_id"))

    query = f"""
                INSERT INTO insurance_records ({", ".join(INPUT_FIELDS)})
                VALUES ({", ".join(PLACEHOLDERS)});
                """
    insurance_record = run_query(query, INPUT_DATA)
    
    if not insurance_record:
        return jsonify({"message": "Execution failed"}), 400
    
    audit_log(
            id=session["user"],
            action="POST",
            tablename="insurance_records",
            record_id=insurance_record,
            new_value=json.dumps(Insurance_fields, default=str),
        )
    
    return jsonify({"message": "Insurance record created successfully!"}), 200

def updateInsuranceRecord(insurance_id):
    data = request.get_json(silent=True) or {}

    status = data.get("status")
    start_date = data.get("start_date")
    end_date = data.get("end_date")

    if not insurance_id:
        return jsonify({"message": "insurance_id is required in URL."}), 400

    existing_record = run_query("SELECT * FROM insurance_records WHERE insurance_id = %s",
                                (insurance_id,), fetch="one")

    if not existing_record:
        return jsonify({"message": "Insurance record not found."}), 404

    update_fields = []
    update_values = []

    if status is not None:
        update_fields.append("status = %s")
        update_values.append(status)
    if start_date is not None:
        update_fields.append("start_date = %s")
        update_values.append(start_date)
    if end_date is not None:
        update_fields.append("end_date = %s")
        update_values.append(end_date)

    if not update_fields:
        return jsonify({"message": "No updatable fields provided. Provide status, start_date or end_date."}), 400

    update_values.append(insurance_id)
    query = f"UPDATE insurance_records SET {', '.join(update_fields)} WHERE insurance_id = %s"
    updated_rows = run_query(query, tuple(update_values))

    if not updated_rows:
        return jsonify({"message": "Update failed."}), 400

    audit_log(
        id=session["user"],
        action="PUT",
        tablename="insurance_records",
        record_id=insurance_id,
        new_value=json.dumps({
            "status": status,
            "start_date": start_date,
            "end_date": end_date
        }, default=str),
    )

    return jsonify({"message": "Insurance record updated successfully!"}), 200