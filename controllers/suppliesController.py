from flask import request, jsonify
from conn import run_query

#get all supplies with supplier details
def getSupplies():

    supplies = run_query("""
                         SELECT * FROM supplies
                         JOIN suppliers ON supplies.supplier_id = suppliers.supplier_id
                         """, fetch="all")


    if not supplies:    
        return jsonify({"message": "No supplies found."}), 404
    
    return jsonify({"data": supplies})

#get supply details
def getSuppliesDetail():
    supplies = run_query("SELECT * FROM supplies", fetch="all")

    if not supplies:
        return jsonify({"message": "No supplies found."}), 404
    
    return jsonify({"data": supplies})


#create supply
def createSupplies():
    data = request.get_json(silent=True) or {}
    supply_id = data.get("supply_id")
    part_name = data.get("part_name")
    part_number = data.get("part_number")
    unit_cost = data.get("unit_cost")
    stock_qty = data.get("stock_qty")
    reorder_level = data.get("reorder_level")
    supplier_id = data.get("supplier_id")

    if not part_name or stock_qty is None or supplier_id is None:
        return jsonify({"message": "part_name, stock_qty, and supplier_id are required."}), 400

    run_query(
        "INSERT INTO supplies (part_name, part_number, unit_cost, stock_qty, reorder_level, supplier_id) VALUES (%s, %s, %s, %s, %s, %s)",
        (part_name, part_number, unit_cost, stock_qty, reorder_level, supplier_id)
    )

    return jsonify({"message": "Supply created successfully."}), 201

#update supply
def updateSupplies(supply_id):
    data = request.get_json(silent=True) or {}

    params = {
        "part_name": data.get("part_name"),
        "part_number": data.get("part_number"),
        "unit_cost": data.get("unit_cost"),
        "stock_qty": data.get("stock_qty"),
        "reorder_level": data.get("reorder_level"),
        "supplier_id": data.get("supplier_id")
    }

    fields = []
    values = []
    for key,value in params.items():
        if value is not None:
            fields.append(f"{key} = %s")
            values.append(value)
    if not fields:
        return jsonify({"message": "At least one field is required to update."}), 400
    values.append(supply_id)
    run_query(f"UPDATE supplies SET {', '.join(fields)} WHERE supply_id = %s", tuple(values))
    return jsonify({"message": "Supply updated successfully."}), 200


#delete supply
def deleteSupplies(supply_id):
    run_query("DELETE FROM supplies WHERE supply_id=%s", (supply_id,))

    return jsonify({"message": "Supply deleted successfully."}), 200        

#get supplies that are below reorder level
def getLowStockSupplies():
    supplies = run_query("SELECT * FROM supplies WHERE stock_qty <= reorder_level", fetch="all")

    if not supplies:
        return jsonify({"message": "No low stock supplies found."}), 404
    
    return jsonify({"data": supplies})