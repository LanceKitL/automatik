from functools import wraps
from flask import session,jsonify,request, redirect,url_for
from conn import run_query


def logged_in_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        
        if "user" not in session:
            return jsonify({
                "message": "Access Denied"
            }), 401
            
        return f(*args, **kwargs)
    return wrapper
    
def role_required(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "user" not in session:
                return jsonify({
                    "message": "Access Denied"
                }), 401
            
            user = run_query("SELECT * FROM users WHERE user_id = %s", (session.get("user"),), fetch="one")
            
            if not user:
                return jsonify({
                    "message": "User not found."
                })
                
            if user["role"] != role:
                return jsonify({"message": "Forbidden Access."}), 401
            
            return f(*args, **kwargs)
        
        return wrapper
    return decorator
        