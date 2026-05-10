from conn import connection
from flask import jsonify, request


#GET - Insurance
def getInsuranceBySale(sale_id):
    conn = connection()
    conn.connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM insurance_records WHERE sale_id = %s", (sale_id,))
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"data": records})
 
# POST - Add insurance
def addInsurance(sale_id):
    data = request.get_json()
    vehicle_id = data["vehicle_id"]
    sale_id = data["sale_id"]
    customer_id = data.get("customer_id", None)
    provider_name = data["provider_name"]
    policy_number = data["policy_number"]
    coverage_type = data.get("coverage_type", None)
    start_date = data["start_date"]
    end_date = data["end_date"]
    status = data.get("status")
 
    conn = connection()
    conn.connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "INSERT INTO insurance_records (vehicle_id, sale_id, customer_id, provider_name, policy_number, coverage_type, start_date, end_date, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (vehicle_id, sale_id, customer_id, provider_name, policy_number, coverage_type, start_date, end_date, status)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": f"Insurance record added for sale {sale_id} successfully!"})