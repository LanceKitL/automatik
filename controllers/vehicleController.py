from flask import request, jsonify, session
from conn import run_query

# index
def getVehicles():

    car = run_query(
        """SELECT * FROM vehicles""",
        fetch="all"
    )

    photos = run_query(
        """SELECT * FROM vehicle_photos""",
        fetch="all"
    )

    supplier = run_query("""
        SELECT
            vehicles.vehicle_id,
            suppliers.company_name,
            suppliers.contact_name,
            suppliers.contact_email,
            suppliers.contact_phone,
            suppliers.address
        FROM suppliers
        JOIN vehicles
            ON suppliers.supplier_id = vehicles.supplier_id
    """, fetch="all")

    if not car:
        return jsonify({"data": []}), 200

    for c in car:

        c["photos"] = [
            p for p in photos
            if p["vehicle_id"] == c["vehicle_id"]
        ]

        supplier_match = next(
            (
                s for s in supplier
                if s["vehicle_id"] == c["vehicle_id"]
            ),
            None
        )

        c["supplier"] = supplier_match

    return jsonify({"data": car}), 200
#show
def showVehicle(id):

    car = run_query(""" 
                    SELECT * FROM vehicles 
                    WHERE vehicle_id = %s
                    """,
                    (id,),
                    fetch="one")
    
    photos = run_query("""
                        SELECT * FROM vehicle_photos
                        WHERE vehicle_id = %s
                        """,
                        (id,),
                        fetch="all")
    
    supplier = run_query("""
                        SELECT suppliers.company_name,suppliers.contact_name,suppliers.contact_email,suppliers.contact_phone,suppliers.address FROM suppliers
                        JOIN vehicles
                        ON suppliers.supplier_id = vehicles.supplier_id 
                        WHERE vehicles.vehicle_id = %s
                        """,
                        (id,),
                        fetch="one")
    
    if not car:
        return jsonify({"message": "no vehicle found."}), 404

    car["photos"] = photos
    car["supplier"] = supplier

    return jsonify({"data": car}), 200

def showVehiclePhotos(id):
    res = run_query("SELECT * FROM vehicle_photos WHERE vehicle_id = %s",(id, ), fetch="all")
    
    if not res: 
        return jsonify({"message": f"vehicle {id} does not exist."}), 404

    return jsonify({"data": res}), 200

def searchVehicle(params):
    if params is None:
        return jsonify({"message": "no search parameters."}), 400
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
    data = request.get_json(silent=True) or {}
    body_type = data.get("body_type")
    brand = data.get("brand")
    color = data.get("color")
    fuel_type = data.get("fuel_type")
    model = data.get("model")
    price = data.get("price")
    seating_capacity = data.get("seating_capacity")
    specs_json = data.get("specs_json")
    status = data.get("status")
    transmission = data.get("transmission")
    vin = data.get("vin")
    year = data.get("year")

    required_fields = {
        "brand": brand,
        "model": model,
        "price": price,
        "status": status,
        "vin": vin,
        "year": year
    }

    for field_name, value in required_fields.items():
        if value is None:
            return jsonify({"message": f"{field_name} is required."}), 400
    
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
    data = request.get_json(silent=True) or {}
    body_type = data.get("body_type")
    brand = data.get("brand")
    color = data.get("color")
    fuel_type = data.get("fuel_type")
    model = data.get("model")
    price = data.get("price")
    seating_capacity = data.get("seating_capacity")
    specs_json = data.get("specs_json")
    status = data.get("status")
    transmission = data.get("transmission")
    vin = data.get("vin")
    year = data.get("year")

    required_fields = {
        "brand": brand,
        "model": model,
        "price": price,
        "status": status,
        "vin": vin,
        "year": year
    }

    for field_name, value in required_fields.items():
        if value is None:
            return jsonify({"message": f"{field_name} is required."}), 400
    
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
    data = request.get_json(silent=True) or {}
    photo_url = data.get("photo_url")
    sort_order = data.get("sort_order")
    uploaded_at = data.get("uploaded_at")

    if not photo_url:
        return jsonify({"message": "photo_url is required."}), 400
    
    res = run_query("""
                    UPDATE vehicle_photos 
                    SET photo_url = %s, sort_order = %s, uploaded_at = %s 
                    WHERE vehicle_id = %s
                    """,
                    (photo_url,sort_order,uploaded_at, id))
    
    if not res: 
        return jsonify({"message": f"updating vehicle {id} unsuccessful."}), 400
    
    return jsonify({"message": "vehicle updated successfully!"}), 200