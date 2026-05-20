from flask import request, jsonify, session
from datetime import datetime
from conn import run_query

# public / guest
def getVehicles():
    """
        Retrieves all vehicles from the database, along with their associated photos and supplier information.
    """
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

def searchVehicle(params):
    conditions = []
    values = []

    if params.get("brand"):
        conditions.append("v.brand LIKE %s")
        values.append(f"%{params['brand']}%")

    if params.get("model"):
        conditions.append("v.model LIKE %s")
        values.append(f"%{params['model']}%")

    if params.get("fuel_type"):
        conditions.append("v.fuel_type LIKE %s")
        values.append(f"%{params['fuel_type']}%")

    if params.get("status"):
        conditions.append("v.status LIKE %s")
        values.append(f"%{params['status']}%")

    if params.get("price_min"):
        conditions.append("v.price_min >= %s")
        values.append(f"%{params['price_min']}%")

    if params.get("price_max"):
        conditions.append("v.price_max <= %s")
        values.append(f"%{params['price_max']}%")

    where_clause = []

    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    query = f"""
    SELECT v.*, p.photo_url
    FROM vehicles v
    LEFT JOIN vehicle_photos p
        ON p.vehicle_id = (
            SELECT vehicle_id
            FROM vehicle_photos
            WHERE vehicle_id = v.vehicle_id
            ORDER BY vehicle_id ASC
            LIMIT 1
        )
    {where_clause}
    """

    res = run_query(query, tuple(values), fetch="all")

    if not res:
        return jsonify({"message": "No vehicles found."}), 404
    
    return jsonify(res), 200

def showVehicle(id):
    """
    Retrieves a specific vehicle by its ID from the database, along with its associated photos and supplier information.
    """
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


# admin only 
def createVehicle():
    data = request.get_json(silent=True) or {}

    allowed_fields = {
        "supplier_id": data.get("supplier_id"),
        "body_type": data.get("body_type"),
        "brand": data.get("brand"),
        "color": data.get("color"),
        "fuel_type": data.get("fuel_type"),
        "model": data.get("model"),
        "price": data.get("price"),
        "seating_capacity": data.get("seating_capacity"),
        "specs_json": data.get("specs_json"),
        "status": data.get("status"),
        "transmission": data.get("transmission"),
        "vin": data.get("vin"),
        "year": data.get("year")
    }

    INPUT_FIELDS = []
    PLACEHOLDERS = []
    INPUT_DATA = []

    for field_name, value in allowed_fields.items():
        if value is not None:
            # append the ff input fields
            INPUT_FIELDS.append(field_name)
            PLACEHOLDERS.append("%s")
            INPUT_DATA.append(value)

    if not "supplier_id" in INPUT_FIELDS:
        return jsonify({"message": "supplier_id is required."}), 400
    
    # add photos too, but only if the vehicle is successfully added first, so that we can get the vehicle_id to link the photos to.

    query = f"""
            INSERT INTO vehicles ({", ".join(INPUT_FIELDS)})
            VALUES ({", ".join(PLACEHOLDERS)})
            """
    car = run_query(query, INPUT_DATA)

    if not car: 
        return jsonify({"message": "adding did not execute successfully."}), 400
    
    return jsonify({"message": "vehicle added successfully!"}), 200

def updateVehicleHandler(id): # updating vehicle
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

    allowed_fields = {
        "body_type": body_type,
        "brand": brand,
        "color": color,
        "fuel_type": fuel_type,
        "model": model,
        "price": price,
        "seating_capacity": seating_capacity,
        "specs_json": specs_json,
        "status": status,
        "transmission": transmission,
        "vin": vin,
        "year": year
    }

    update_fields = []
    params = []

    for field_name, value in allowed_fields.items():
        if value is not None:
            update_fields.append(f"{field_name} = %s")
            params.append(value)

    if not update_fields:
        return jsonify({"message": "no fields to update."}), 400

    params.append(id)

    query = f""" 
            UPDATE vehicles SET {", ".join(update_fields)}
            WHERE vehicle_id = %s
            """
    
    car = run_query(query, params)

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

def updateStatus(vehicle_id):
    """
    Change the status of the vehicle
    
    status ['available','reserved','discontinued','delivered']
    """
    options = ['available','reserved','discontinued','delivered']

    data = request.get_json()
    status = data.get("status")

    if status not in options:
        return jsonify({
            "message": "status not found, please use these options.",
            "options": options
            }), 400

    if status is None:
        return jsonify({"message": "no fields to update."}), 400

    run_query("""
              UPDATE vehicles 
              SET status = %s 
              WHERE vehicle_id = %s
              """,
              (status, vehicle_id))
    
    return jsonify({"message": f"vehicle {vehicle_id} - {status} successfully!"}), 200


# vehicle photos
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

def addPhoto():
    """
    ADD VEHICLE PHOTOS
    """
    
    data = request.get_json()

    fields = {
        "vehicle_id": data.get("vehicle_id"), # required
        "photo_url": data.get("photo_url"), 
        "sort_order": data.get("sort_order")
        # uploaded_at datetime.now()
    }

    params = []

    for field_name, value in fields.items():
        if not field_name:
            return jsonify({"message": f"{field_name} is required."}), 400
        
        params.append(value)
    
    # check if vehicle exists
    existing = run_query("""
                        SELECT vehicle_id FROM vehicles 
                        WHERE vehicle_id = %s    
                        """,
                            (data.get("vehicle_id"),),
                            fetch="one")
    if existing is None:
        return jsonify({"message": "can't add photos to non-existing vehicle."}),400

    # pass
    run_query("""
              INSERT INTO vehicle_photos
              (vehicle_id, photo_url, sort_order)
              VALUES (%s,%s,%s)
              """,
              (params))
    
    return jsonify({"message": "vehicle photo added succesfully!"}),200

def removePhoto(photo_id):
    # check if vehicle exists
    photo = run_query("""
                        SELECT * FROM vehicle_photos
                        WHERE photo_id = %s
                        """,
                        (photo_id, ),
                        fetch="one")

    if photo is None:
        return jsonify({"message": "Image not found."}), 404

    # delete photo
    res = run_query("""
                    DELETE FROM vehicle_photos 
                    WHERE vehicle_id = %s
                    """,
                    (photo_id,))
    
    return jsonify({"message": f"vehicle photo {photo_id} deleted successfully!"}), 200

def indexLowStocks(threshold):
    print("hello")
    res = run_query("""
                    SELECT brand, model, COUNT(*) as available_count
                    FROM vehicles
                    WHERE status = 'available'
                    GROUP BY brand,model
                    HAVING COUNT(*) < %s
                    """,
                    (threshold,),
                    fetch="all")
    
    return jsonify({
        "message": "success",
        "data": res
        }), 200