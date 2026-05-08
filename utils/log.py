from flask import jsonify
from conn import run_query


def audit_log(id,action,tablename,old_value=None,new_value=None):
    res = run_query("INSERT INTO audit_logs (user_id,action,table_name,old_value,new_value) VALUES (%s,%s,%s,%s,%s)", (id,action,tablename,old_value,new_value))
    if not res:
        return "failed to log."
    return "added to logs."
    
    