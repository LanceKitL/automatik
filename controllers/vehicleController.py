from flask import request, jsonify, session
from datetime import datetime
from conn import run_query

# public / guest
def getVehicles():
    """
        Retrieves all vehicles from the database, along with their associated photos and supplier information.
    """
    car = run_query(
        """SELECT * FROM vehicles WHERE status = 'available'""",
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

    # Brand
    if params.get("brand"):
        conditions.append("v.brand LIKE %s")
        values.append(f"%{params['brand']}%")

    # Model
    if params.get("model"):
        conditions.append("v.model LIKE %s")
        values.append(f"%{params['model']}%")

    # Fuel Type
    if params.get("fuel_type"):
        conditions.append("v.fuel_type LIKE %s")
        values.append(f"%{params['fuel_type']}%")

    # Status
    if params.get("status"):
        conditions.append("v.status LIKE %s")
        values.append(f"%{params['status']}%")

    # Minimum Price
    if params.get("price_min"):
        conditions.append("v.price >= %s")
        values.append(params["price_min"])

    # Maximum Price
    if params.get("price_max"):
        conditions.append("v.price <= %s")
        values.append(params["price_max"])

    # Build WHERE clause
    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    query = f"""
        SELECT 
            v.*,
            p.photo_url
        FROM vehicles v
        LEFT JOIN vehicle_photos p
            ON p.photo_id = (
                SELECT vp.photo_id
                FROM vehicle_photos vp
                WHERE vp.vehicle_id = v.vehicle_id
                ORDER BY vp.photo_id ASC
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


def createVehicle():
    data = request.get_json(silent=True)
    TRANSMISSION_TYPES = ["manual","automatic"]
    FUEL_TYPES = ["gasoline","diesel","electric","hybrid"]

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON object"
        }), 400

    # required fields
    supplier_id = data.get("supplier_id")
    vin = data.get("vin")
    brand = data.get("brand")
    model = data.get("model")
    year = data.get("year")
    price = data.get("price")
    
    # other fields
    color = data.get("color")
    body_type = data.get("body_type")
    seating_capacity = data.get("seating_capacity")
    transmission = data.get("transmission")
    fuel_type = data.get("fuel_type")
    specs_json = data.get("specs_json")
    
    if not all([supplier_id, vin, model, year, price, color, body_type, seating_capacity, transmission, fuel_type, specs_json]):
        return jsonify({
            "message": "supplier_id, vin, model, year, price, color, body_type, seating_capacity, transmission, fuel_type, specs_json are required."
        }), 400
        
    if transmission not in TRANSMISSION_TYPES:
        return jsonify({
            "message": "invalid transmission type",
            "fields": TRANSMISSION_TYPES
        }), 400
    
    if fuel_type not in FUEL_TYPES:
        return jsonify({
            "message": "invalid fuel type",
            "fields": FUEL_TYPES
        }), 400
    
    # check if supplier exists
    supplier = run_query("SELECT * FROM suppliers WHERE supplier_id =%s", (supplier_id,), fetch="one")
    
    # automatically get the supplier company (assuming that the company of the supplier = brand)
    brand = supplier["company_name"].split(" ")[0] 
    
    # check if vin exists already
    vehicle = run_query("SELECT * FROM vehicles WHERE vin =%s", (vin,), fetch="one")
    
    if vehicle:
        return jsonify({
            "message": f"vehicle {vin} already exists"
        }), 400
    
    if not supplier:
        return jsonify({
            "message": "supplier not found."
        }), 404
        
    res = run_query("""
              INSERT INTO vehicles (supplier_id,vin,brand,model,year,price,color,body_type,seating_capacity,transmission,fuel_type,specs_json)
              VALUE (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
              """,
              (supplier_id,vin,brand,model,year,price,color,body_type,seating_capacity,transmission,fuel_type,specs_json))
    
    if not res:
        return jsonify({
            "message": "creation failed."
        }), 500
    
    return jsonify({"message": f"vehicle #{res} created successfully!"}),200
        

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
    
    # check if vehicle exists first
    existing = run_query("""
                        SELECT vehicle_id FROM vehicles
                        WHERE vehicle_id = %s
                        """,
                        (id,),
                        fetch="one")

    if not existing:
        return jsonify({"message": "vehicle not found."}), 404

    run_query(query, params)

    return jsonify({"message": f"vehicle {id} updated successfully!"}), 200

def deleteVehicleHandler(id):
    # check if vehicle exists first
    existing = run_query("""
                        SELECT vehicle_id FROM vehicles
                        WHERE vehicle_id = %s
                        """,
                        (id,),
                        fetch="one")

    if not existing:
        return jsonify({"message": "vehicle not found."}), 404

    run_query("""
              DELETE FROM vehicles 
              WHERE vehicle_id = %s 
              """,
              (id,))

    return jsonify({"message": f"vehicle {id} deleted successfully!"}), 200

def updateStatus(vehicle_id):
    """
    Change the status of the vehicle
    
    status ['available','reserved','discontinued','delivered']
    """
    options = ['available','reserved','discontinued','delivered']

    data = request.get_json(silent=True) or {} # if body not a valid JSON return None instead of raising Error
    status = data.get("status")

    if status is None: # check first if the status is empty.
        return jsonify({"message": "no fields to update."}), 400
    
    if status not in options: # check if the status is valid
        return jsonify({
            "message": "status not found, please use these options.",
            "options": options
            }), 400

    run_query("""
              UPDATE vehicles 
              SET status = %s 
              WHERE vehicle_id = %s
              """,
              (status, vehicle_id))
    
    return jsonify({"message": f"vehicle {vehicle_id} - {status} successfully!"}), 200


# vehicle photos
def updateVehiclePhoto(photo_id):
    data = request.get_json(silent=True) or {}
    photo_url = data.get("photo_url")
    sort_order = data.get("sort_order")
    uploaded_at = data.get("uploaded_at")

    if not photo_url:
        return jsonify({"message": "photo_url is required."}), 400
    
    existing = run_query("""
                        SELECT photo_id FROM vehicle_photos
                        WHERE photo_id = %s
                        """,
                        (photo_id,),
                        fetch="one")

    if not existing:
        return jsonify({"message": "photo not found."}), 404

    run_query("""
              UPDATE vehicle_photos 
              SET photo_url = %s, sort_order = %s, uploaded_at = %s 
              WHERE photo_id = %s
              """,
              (photo_url, sort_order, uploaded_at, photo_id))

    return jsonify({"message": f"vehicle photo {photo_id} updated successfully!"}), 200

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
        if value is None:
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
    run_query("""
        DELETE FROM vehicle_photos 
        WHERE photo_id = %s
        """,
        (photo_id,))

    return jsonify({"message": f"vehicle photo {photo_id} deleted successfully!"}), 200

def indexLowStocks(threshold):
    if threshold is None:
        return jsonify({
            "message": "Please define the threshold parameter."
        }), 400

    try:
        threshold = int(threshold)

        res = run_query(
            """
            SELECT brand, model, COUNT(*) AS available_count
            FROM vehicles
            WHERE status = 'available'
            GROUP BY brand, model
            HAVING COUNT(*) < %s
            """,
            (threshold,),
            fetch="all"
        )

        return jsonify({
            "message": "success",
            "data": res
        }), 200

    except ValueError:
        return jsonify({
            "message": "Threshold must be a valid integer."
        }), 400

    except Exception as e:
        return jsonify({
            "message": "Internal server error.",
            "error": str(e)
        }), 500