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
    
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            
            if session["role"].lower() not in [r.lower() for r in roles]:
                return jsonify({"message": "Forbidden Access."}), 401
            
            return f(*args, **kwargs)
        
        return wrapper
    return decorator
        