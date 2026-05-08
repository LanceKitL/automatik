from werkzeug.security import generate_password_hash, check_password_hash
from validators.middleware import role_required, logged_in_required
from flask import Blueprint, jsonify, request, session
from utils.log import audit_log
from datetime import datetime
from conn import run_query
from mysql.connector import Error
import random
import string

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data["password"]
    
    if not username and not email:
        return jsonify({"message": "use your username or email."}) 
    
    user = run_query("SELECT * FROM users WHERE username = %s OR email = %s", (username, email), fetch="one")
    
    if not user:
        return jsonify({"message": "user not found."}), 401
    
    # check if email is verified
    if user["email_verified"] != 1:
        return jsonify({"message": "Account is not verified. Please log in to your email and verify your account."}), 404
    
    # check if the password match
    if not check_password_hash(user["hashed_password"], password):
        return jsonify({"message": "Invalid Credentials."})
    
    # user logs in successfull!
    session["user"] = user["user_id"] # stores the user id
    session.permanent = True # activate the expiration time
    print(session.get("user"))
    # update to active
    run_query("UPDATE users SET is_active = %s WHERE user_id = %s", (1,session["user"]))
    
    return jsonify({"message": "Logged in successfull!"})

# log this to audit logs!
@auth_bp.route("/createCustomerAcc/<email>", methods=["POST"])
@logged_in_required
@role_required("admin", "agent")
def create_customer(email):
    if not email:
        return jsonify({"message": "customer email is required."})
    # for password
    characters = string.ascii_letters + string.digits + string.punctuation

    # fields 
    username = 'CUST'.join(random.choice(characters) for _ in range(3))
    password = ''.join(random.choice(characters) for _ in range(8))
    role = 'customer'
    query = "INSERT INTO users (username, hashed_password, email,role) VALUES (%s,%s,%s,%s)"
    param = (username,password,email,role)
    res = run_query(query,param)
    audit_log(session["user"],"Create Customer Account", "users,customer_details")

        
    return jsonify({"message": "customer account, created successfully!"}), 200
    

# 
@auth_bp.route('/register', methods=["POST"])
def register():
    data = request.get_json()
    fields = [data["username"],data["email"],data["password"],data["confirmPassword"]]
    
    # simple validation if empty!
    for field in fields:
        if not field:
            return jsonify({"message": f"{field} is required."})
    # check if matched
    if data["password"] != data["confirmPassword"]:
        return jsonify({"message": "password does not match."})
    # generate the hashed password
    hashedPassword = generate_password_hash(data["password"])
    print(hashedPassword)
        
    result = run_query("INSERT INTO users (username,email,hashed_password, role, email_verified) VALUES (%s,%s,%s,%s,%s)", (data["username"], data["email"], hashedPassword, 'agent', 0))
    
    return jsonify({"message": "success!", 
                    "data": result}), 200
    
    
@auth_bp.route("/logout", methods=["POST"])
def logout():
    print(session.get("user"))
    if "user" not in session:
        return jsonify({"message": "Access Denied."})
 
    user = session["user"]
    last_login = datetime.now()
    run_query("UPDATE users SET last_login = %s, is_active = %s WHERE user_id = %s", (last_login,0, user))
    session.clear()
    return jsonify({"message": "Logged out success."})