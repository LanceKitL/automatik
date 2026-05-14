from flask import request, jsonify
from conn import run_query

def searchSupplier (params):
    res = run_query('SELECT * FROM suppliers')

    if not res:
        return jsonify ({"message": "Supplier not found"})
    
    return jsonify ({"message": res})

def createSupplier ():
    data = request.get_json()
    supplier_id = data.get("supplier_id")
    company_name = data.get("company_name")
    contact_name = data.get("contact_name")
    contact_email = data.get("contact_email")
    contact_phone = data.get("contact_phone")
    address = data.get("address")
    is_active = data.get("is_active")
    created_at = data.get("created_at")

    supplier = run_query(""" 
                    INSERT INTO suppliers 
                    (supplier_id, company_name, contact_name, contact_email, contact_phone, address, is_active, 
                    created_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    """, 
                    (supplier_id, company_name, contact_name, contact_email, contact_phone, address ,is_active, 
                     created_at ))
    
    if not supplier:
        return jsonify({"message": "Adding did not execute succesfully"}), 400
    
    return jsonify ({"message": "Supplier added succesfully"}), 200

def updateSupplier(id):
    data = request.get_json()
    supplier_id = data.get("supplier_id")
    company_name = data.get("company_name")
    contact_name = data.get("contact_name")
    contact_email = data.get("contact_email")
    contact_phone = data.get("contact_phone")
    address = data.get("address")
    is_active = data.get("is_active")
    created_at = data.get("created_at")

    supplier = run_query(""" 
                    UPDATE INTO suppliers 
                    (supplier_id, company_name, contact_name, contact_email, contact_phone, address, is_active, 
                    created_at
                    WHERE supplier_id = %s)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    """, 
                    (supplier_id, company_name, contact_name, contact_email, contact_phone, address ,is_active, 
                     created_at, id ))
    
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
        return jsonify({"message": "Deleting did not execute succesfully"}), 400
    
    return jsonify ({"message": "Supplier deleted succesfully"}), 200
    