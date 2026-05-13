from werkzeug.security import check_password_hash, generate_password_hash
from flask import session, jsonify, request
from utils.log import audit_log
from datetime import datetime
from conn import run_query
import random
import string

def loginHandler():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data["password"]
    
    if not username and not email:
        return jsonify({"message": "use your username or email."}) 
    
    user = run_query("""
                     SELECT * FROM users 
                     WHERE username = %s 
                     OR email = %s 
                     """, 
                     (username, email), 
                     fetch="one")
    
    if not user:
        return jsonify({"message": "user not found."}), 403
    
    # check if email is verified
    if user["email_verified"] != 1:
        return jsonify({"message": "Account is not verified. Please log in to your email and verify your account."}), 404
    
    # check if the password match
    if not check_password_hash(user["hashed_password"], password):
        return jsonify({"message": "Invalid Credentials."}),403
    
    # user logs in successfull!
    session["user"] = user["user_id"] # stores the user id
    session["role"] = user["role"] # store the user role
    session.permanent = True # activate the expiration time


    # update to active
    run_query(""" 
              UPDATE users SET is_active = %s 
              WHERE user_id = %s 
              """, 
              (1,session["user"]))
    
    return jsonify({"message": "Logged in successfull!"}), 200
    
def customerAccountHandler(email):
    if not email:
        return jsonify({"message": "customer email is required."}), 400

    characters = string.ascii_letters + string.digits + string.punctuation

    username = 'CUST'.join(random.choice(characters) for _ in range(3))
    password = ''.join(random.choice(characters) for _ in range(8)) # insert the raw not hashed password to the email for the customer to know their password and later change it.
    role = 'customer'
    query = """ 
            INSERT INTO users 
            (username, hashed_password, email,role) 
            VALUES (%s,%s,%s,%s) 
            """
    param = (username,password,email,role)
    res = run_query(query,param)
    audit = audit_log(session["user"],"Create Customer Account", "users,customer_details")
    
    if not res and not audit:
        return jsonify({"message": "customer account creation failed."}), 400
    
    return jsonify({"message": "customer account, created successfully!"}), 200

def AgentAccountHandler():
    data = request.get_json()
    fields = [data["username"],data["email"],data["password"],data["confirmPassword"]]
    
    # simple validation if empty!
    for field in fields:
        if not field:
            return jsonify({"message": f"{field} is required."}), 400
    # check if matched
    if data["password"] != data["confirmPassword"]:
        return jsonify({"message": "password does not match."}), 400
    # generate the hashed password
    hashedPassword = generate_password_hash(data["password"])
    print(hashedPassword)
        
    result = run_query(""" 
                       INSERT INTO users 
                       (username,email,hashed_password, role, email_verified) 
                       VALUES (%s,%s,%s,%s,%s)
                       """, 
                       (data["username"], data["email"], hashedPassword, 'agent', 0))
    
    return jsonify({"message": "success!", 
                    "data": result}), 200
    
def logoutHandler():
    user = session["user"]
    last_login = datetime.now()
    run_query("""
              UPDATE users SET last_login = %s, is_active = %s 
              WHERE user_id = %s 
              """, 
              (last_login,0, user))
    
    session.clear()
    return jsonify({"message": "Logged out success."}), 200