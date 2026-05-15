from datetime import datetime
from flask import request, jsonify
from conn import run_query

def searchSupplier (params):
    if not params:
        return jsonify({"message": "search parameter is required."}), 400

    res = run_query(
        """
        SELECT * FROM suppliers
        WHERE company_name LIKE %s
           OR contact_name LIKE %s
           OR contact_email LIKE %s
           OR contact_phone LIKE %s
        """,
        (f"%{params}%", f"%{params}%", f"%{params}%", f"%{params}%"),
        fetch="all"
    )

    if not res:
        return jsonify ({"message": "Supplier not found"})
    
    return jsonify ({"message": res})

def createSupplier ():
    data = request.get_json(silent=True) or {}
    company_name = data.get("company_name")
    contact_name = data.get("contact_name")
    contact_email = data.get("contact_email")
    contact_phone = data.get("contact_phone")
    address = data.get("address")
    is_active = data.get("is_active")
    created_at = datetime.now()

    if not company_name:
        return jsonify({"message": "company_name is required."}), 400

    supplier = run_query(
        """ 
        INSERT INTO suppliers 
        (company_name, contact_name, contact_email, contact_phone, address, is_active, created_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """,
        (company_name, contact_name, contact_email, contact_phone, address, is_active, created_at)
    )
    
    if not supplier:
        return jsonify({"message": "Adding did not execute succesfully"}), 400
    
    return jsonify ({"message": "Supplier added succesfully"}), 200

def updateSupplier(id):
    data = request.get_json(silent=True) or {}

    fields = {
        "company_name": data.get("company_name"),
        "contact_name": data.get("contact_name"),
        "contact_email": data.get("contact_email"),
        "contact_phone": data.get("contact_phone"),
        "address": data.get("address"),
        "is_active": data.get("is_active")
    }

    update_fields = []
    params = []

    for field_name, value in fields.items():
        if value is not None:
            update_fields.append(f"{field_name} = %s")
            params.append(value)

    if not update_fields:
        return jsonify({"message": "No fields to update."}), 400

    params.append(id)

    supplier = run_query(
        f""" 
        UPDATE suppliers 
        SET {', '.join(update_fields)}
        WHERE supplier_id = %s
        """,
        params
    )
    
    if not supplier:
        return jsonify({"message": "Updating did not execute succesfully"}), 400
    
    return jsonify ({"message": "Supplier updated succesfully"}), 200

def deleteSupplier(id):
    supplier = run_query("""
                    DELETE FROM suppliers 
                    WHERE supplier_id = %s 
                    """, 
                    (id, ))
    
    if not supplier:
        return jsonify({"message": "supplier not found."}), 404
    
    return jsonify ({"message": "Supplier deleted succesfully"}), 200
    