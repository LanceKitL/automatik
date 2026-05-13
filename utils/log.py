from flask import jsonify
from conn import run_query


def audit_log(id,action,tablename,old_value=None,new_value=None):
    res = run_query("INSERT INTO audit_logs (user_id,action,table_name,old_value,new_value) VALUES (%s,%s,%s,%s,%s)", (id,action,tablename,old_value,new_value))
    if not res:
        return jsonify({"message": "logging failed."}), 400
    return jsonify({"message": "action logged successfully!"}), 200
    
    