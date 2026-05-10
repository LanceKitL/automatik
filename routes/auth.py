from werkzeug.security import generate_password_hash, check_password_hash
from validators.middleware import role_required, logged_in_required
from flask import Blueprint, jsonify, request, session
from utils.log import audit_log
from datetime import datetime
from conn import run_query
import random
import string

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/me")
def me():
    if "user" not in session:
        return jsonify({"message": "user not found."}), 400
    
    return jsonify({"message": session["user"]})

@auth_bp.route("/login", methods=["POST"])
def login():
    # if user in session exists
    if "user" in session:
        return jsonify({"message": "Already logged in"})
    
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data["password"]
    
    if not email and not username:
        return jsonify({"message": "use your username or email."}), 400
        

    user = run_query("SELECT * FROM users WHERE username = %s OR email = %s", (username, email), fetch="one")
    
    if not user:
        return jsonify({"message": "user not found."}), 400
    
    # check if email is verified
    if user["email_verified"] != 1:
        return jsonify({"message": "Account is not verified. Please log in to your email and verify your account."}), 400
    
    # check if the password match
    if not check_password_hash(user["hashed_password"], password):
        return jsonify({"message": "Invalid Credentials."}), 400
    
    # user logs in successfull!
    session["user"] = user["user_id"] # stores the user id
    session.permanent = True # activate the expiration time

    # update to active
    run_query("UPDATE users SET is_active = %s WHERE user_id = %s", (1,session["user"]))
    
    return jsonify({"message": "Logged in successfull!"})

# log this to audit logs!
@auth_bp.route("/createCustomerAcc", methods=["POST"])
@logged_in_required
@role_required("admin", "agent")
def create_customer():
    data = request.get_json()
    email = data["email"]
    
    if not email:
        return jsonify({"message": "customer email is required."})
    # for password
    characters = string.ascii_letters + string.digits + string.punctuation

    # fields x
    username = 'USER-' + ''.join(random.choice(characters) for _ in range(3))
    password = ''.join(random.choice(characters) for _ in range(8))
    role = 'customer'
    query = "INSERT INTO users (username, hashed_password, email,role) VALUES (%s,%s,%s,%s)"
    param = (username,password,email,role)
    
    if run_query("SELECT * FROM users WHERE email = %s", (email,), fetch="one"):
        return jsonify({"message": "Email already exists."}), 400
    
    run_query(query,param)
    audit_log(session["user"],"Create Customer Account", "users,customer_details")
    
        
    return jsonify({"message": "customer account, created successfully!"}), 200
    

# 
@auth_bp.route('/register', methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    confirmPassword = data.get("confirmPassword")

    # check if email exists
    check_credentials = run_query("SELECT * FROM users WHERE email = %s OR username = %s LIMIT 1", (email,username), fetch="one")
    if check_credentials:
        return jsonify({
            "message": "Duplicate email or username. Please use another."
        }), 409
        
    # check if password match
    if password != confirmPassword:
        return jsonify({
            "message": "Password does not match."
        }), 400
        
    user_id = run_query("INSERT INTO users (username, hashed_password, email, role) VALUES (%s, %s, %s, %s)",
    (username, generate_password_hash(password), email, "customer"))
 
    if user_id:
        # email_verify set to False by default
        # send email
        # email will be sent there and verify-email will catch the sent email
                
        return jsonify({
            "message": "User registered successfully."
        }), 201   
    else:
        return jsonify({
            "message": "User registration failed."
        }), 500
    
@auth_bp.route("/logout", methods=["POST"])
def logout():

    if "user" not in session:
        return jsonify({"message": "Access Denied."}), 401
 
    user = session["user"]
    last_login = datetime.now()
    run_query("UPDATE users SET last_login = %s, is_active = %s WHERE user_id = %s", (last_login,0, user))
    session.clear()
    return jsonify({"message": "Logged out success."})

@auth_bp.route("/verify-email", methods=["POST"])
def verify_email():
    data = request.get_json()
    email = data["email"]
    if not email:
        return jsonify({
            "message": "please fill the necessary field."
        })
    # email?
    # check if the email_verification is true 
    # check if the email exists
    user = run_query("SELECT * FROM users WHERE email = %s LIMIT 1", (email,), fetch="one")
    
    if not user:
        return jsonify({
            "message": "user doesn't exists."
        }), 403
    
    if user["email_verified"] == 1:
        return jsonify({
            "message": "email is already verified."
        }), 403

    # if the email passed this conditions, then update the email to verified
    verify = run_query("UPDATE users SET email_verified = %s", (1, ))
    
    if not verify:
        return jsonify({
            "message": "verification failed."
        }), 401
    
    return jsonify({
        "message": f"{email} verified successfully."
    }), 200
    

@auth_bp.route("/change_password", methods=["POST"])
@logged_in_required
def change_password():
    # get the current logged in user
    # get the last password and type new password & confirmPassword
    data = request.get_json()
    user_id = session["user"]
    
    user = run_query("SELECT * FROM users WHERE user_id = %s", (user_id, ), fetch="one")
    
    if not user:
        return jsonify({"message", "user does not exists."}), 403
    
    # get the request.
    oldPassword = data["oldPassword"]
    newPassword = data["newPassword"]
    confirmPassword = data["confirmPassword"]

    fields = [oldPassword, newPassword, confirmPassword]
    
    for field in fields:
        if not field:
            return jsonify({"message", "please fill the following field."}), 400

    if not check_password_hash(user["hashed_password"], oldPassword):
        return jsonify({"message": "password does not match."}), 400
    
    if user["hashed_password"] == generate_password_hash(oldPassword):
        return jsonify({"message": "You already used this password."}), 400
    # if it satisfies the json body, its passed
    
    if newPassword != confirmPassword:
        return jsonify({"message": "password does not match."}), 400
    
    hashed_password = generate_password_hash(newPassword)
    
    # insert to database
    update_password = run_query("UPDATE users SET hashed_password = %s WHERE user_id = %s", (hashed_password, user_id ))
    
    if not update_password:
        return jsonify({
            "message": "updating password failed."
        }), 400
    
    return jsonify({
        "message": f"password for {user_id} updated successfully!"
    }), 200