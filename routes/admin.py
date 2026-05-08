from flask import Blueprint,jsonify,request
from conn import run_query
from validators.middleware import role_required, logged_in_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users')
@role_required("admin")
def get_users():
    result = run_query("SELECT * FROM users", fetch="all")
    return jsonify({"data": result})

@admin_bp.route("/users/<id>")
@role_required("admin")
def get_user_with(id):
    result = run_query("SELECT * FROM users WHERE user_id = %s", (id, ), fetch="one")
    return jsonify({"data": result})

@admin_bp.route("/users/<int:user_id>/profile")
@role_required("admin")
def get_user_profile_with(user_id):
    result = run_query("SELECT * FROM user_profile WHERE user_id = %s", (user_id, ), fetch="one")
    return jsonify({"data": result})

# for admin control, everything can be changed.
@admin_bp.route("/users/<int:user_id>/")
@role_required("admin")
def update_user_with(id):
    data = request.json()
    result = run_query("UPDATE users SET fullName = %s, phone_number = %s, address=%s,city=%s,provice=%s,zip_code=%s,date_of_birth=%s,gender=%s,profile_picture_url=%s WHERE user_id = %s", 
    (data["fullName"], data["phone_number"], data["address"], data["city"], data["province"], data["zip_code"], data["date_of_birth"], data["gender"], data["profile_picture_url"], id))
    
    return jsonify({"data": result})

@admin_bp.route("/agents")
@role_required("admin")
def get_agents():
    result = run_query("SELECT users.username, users.role, agent_details.employee_number, agent_details.hire_date FROM users INNER JOIN agent_details ON users.user_id = agent_details.user_id;", fetch="all")
    return jsonify({"data": result})

@admin_bp.route("/customers")
@role_required("admin")
def get_customers():
    result = run_query("SELECT users.username, users.role, users.email, customer_details.customer_number, customer_details.notes, customer_details.preferred_payment_method, customer_details.preferred_contact_method FROM users INNER JOIN customer_details ON users.user_id = customer_details.user_id;", fetch="all")
    return jsonify({"data": result})

