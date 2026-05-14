from flask import request, jsonify
from conn import run_query

def searchVehicle(params):
    res = run_query("""
                    SELECT * FROM vehicles 
                    WHERE model LIKE %s OR fuel_type LIKE %s OR year LIKE %s OR CAST(year as CHAR) LIKE %s 
                    """, 
                    (f"%{params}%", f"%{params}%", f"%{params}%", f"%{params}%"), 
                    fetch="all")
    #sample search query: http://localhost:5000/vehicles/search?param=2020
    
    if not res:
        return jsonify({"message": f"vehicle with attribute {params} not found."}), 400
    
    return jsonify({"message": res})

def createVehicle():
    data = request.get_json()
    body_type = data.get("body_type")
    brand = data["brand"]
    color = data.get("color")
    fuel_type = data.get("fuel_type")
    model = data["model"]
    price = data["price"]
    seating_capacity = data.get("seating_capacity")# int
    specs_json = data.get("specs_json")
    status = data["status"]
    transmission = data.get("transmission")
    vin = data["vin"]
    year = data["year"]
    
    car = run_query(""" 
                    INSERT INTO vehicles 
                    (body_type, brand, color, fuel_type, model, price, seating_capacity, 
                    specs_json, status, transmission, vin, year)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """, 
                    (body_type, brand, color, fuel_type, model, price ,seating_capacity, 
                     specs_json, status, transmission, vin, year ))

    if not car: 
        return jsonify({"message": "adding did not execute successfully."}), 400
    
    return jsonify({"message": "vehicle added successfully!"}), 200

def updateVehicleHandler(id):
    data = request.get_json()
    body_type = data.get("body_type")
    brand = data["body"]
    color = data.get("color")
    fuel_type = data.get("fuel_type")
    model = data["model"]
    price = data["price"]
    seating_capacity = data.get("seating_capacity")# int
    specs_json = data.get("specs_json")
    status = data["status"]
    transmission = data.get("transmission")
    vin = data["vin"]
    year = data["year"]
    
    car = run_query(""" 
                    UPDATE vehicles SET 
                    body_type = %s, brand = %s, color = %s, fuel_type = %s, model = %s, price = %s,
                    seating_capacity = %s, specs_json = %s, status = %s, transmission = %s,
                    vin = %s, year = %s 
                    WHERE vehicle_id = %s
                    """, 
                    (body_type, brand, color, fuel_type, model, price, 
                     seating_capacity, specs_json, status, transmission, vin, year, id ))

    if not car: 
        return jsonify({"message": "update did not execute successfully."}), 400
    
    return jsonify({"message": f"vehicle {id} updated successfully!"}), 200

def deleteVehicleHandler(id):
    car = run_query("""
                    DELETE FROM vehicles 
                    WHERE vehicle_id = %s 
                    """, 
                    (id, ))

    if not car: 
        return jsonify({"message": "deletion did not execute successfully."}), 400
    
    return jsonify({"message": f"vehicle {id} deleted successfully!"}), 200

def updateVehiclePhoto(id):
    data = request.get_json()
    photo_url = data["photo_url"]
    sort_order = data["sort_order"]
    uploaded_at = data["uploaded_at"]
    
    res = run_query("""
                    UPDATE vehicle_photos 
                    SET photo_url = %s, sort_order = %s, uploaded_at = %s 
                    WHERE vehicle_id = %s
                    """,
                    (photo_url,sort_order,uploaded_at, id))
    
    if not res: 
        return jsonify({"message": f"updating vehicle {id} unsuccessful."}), 400
    
    return jsonify({"message": "vehicle updated successfully!"}), 200