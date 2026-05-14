from flask import request, jsonify, session
from conn import run_query

# index
def getVehicles():
    res = None
    if "vehicle" in session:
        return jsonify({"data": res}), 200

    # save the files on session (cookies) to fetch faster
    res = run_query("SELECT * FROM vehicles", fetch="all")
    
    return jsonify({"data": res}), 200

#show
def showVehicle(id):
    car = run_query("SELECT * FROM vehicles WHERE vehicle_id = %s", (id, ), fetch="one")
    
    if not car:
        return jsonify({"message": "no vehicle found."}), 400    
    
    return jsonify({"data": car}), 200

def showVehiclePhotos(id):
    res = run_query("SELECT * FROM vehicle_photos WHERE vehicle_id = %s",(id, ), fetch="all")
    
    if not res: 
        return jsonify({"message": f"vehicle {id} does not exists."}), 400

    return jsonify({"data": res}), 200

def searchVehicle(params):
    q = f"%{params}%"
    res = None


    res = run_query("""
                    SELECT brand,model,year,body_type,seating_capacity,transmission,status,price FROM vehicles 
                    WHERE 
                        model LIKE %s
                        OR brand LIKE %s
                        OR year LIKE %s
                        OR body_type LIKE %s
                        OR transmission LIKE %s
                        OR STATUS LIKE %s
                    """, 
                    (q,q,q,q,q,q), 
                    fetch="all")
    
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