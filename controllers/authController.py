from werkzeug.security import check_password_hash, generate_password_hash
from utils.token_helper import EmailVerificationToken
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
from flask import session, jsonify, request, render_template, abort
=======
<<<<<<< HEAD
=======
<<<<<<< HEAD
=======
>>>>>>> f27b11c (completed the email_verification, designed email response and dynamic IP binding)
>>>>>>> fe4172f (completed the email_verification, designed email response and dynamic IP binding)
from flask import session, jsonify, request, render_template, abort, flash
>>>>>>> 36bf98c (customer_portal)
=======
from flask import session, jsonify, request, render_template, abort, flash
>>>>>>> refs/remotes/origin/feature/customer-portal-api
from services.mail_service import send_email_verification, welcome_user
from datetime import datetime, timezone
from conn import run_query, get_db, Error
from utils.log import audit_log, get_local_ip
import hashlib
<<<<<<< HEAD
=======
from services.mail_service import send_email_verification
from flask import session, jsonify, request
from datetime import datetime, timezone
import hashlib
from utils.log import audit_log
from conn import run_query
>>>>>>> 2f24da0 (added email service / verification)
=======
>>>>>>> refs/remotes/origin/feature/customer-portal-api
import random
import string

def me():
    user = session["user"]
    role = session["role"]

    response = run_query("""
                        SELECT user_id,username,email,role FROM users 
                         WHERE user_id = %s
                         AND role = %s
                        """,
                        (user,role),
                        fetch="one")
    
    if not response:
        return jsonify({"message": "no user found."}), 404

    return jsonify({
        "message": response,
        "current_ip": get_local_ip()
        })

def seedAdmin():
    # create a default admin account
    username = "admin"
    email = "admin@gmail.com"
    password = "admin123"
    hashed_password = generate_password_hash(password)
    role = 'admin'
    existing = run_query(
        """
        SELECT user_id
        FROM users
        WHERE username = %s OR email = %s
        """,
        (username, email),
        fetch="one"
    )
    if existing:
        return jsonify({"message": "admin user is already registered!"}), 400
    query = """
            INSERT INTO users
            (username, hashed_password, email, role, email_verified)
            VALUES (%s,%s,%s,%s,%s)
            """
    param = (username, hashed_password, email, role, 1)
    res = run_query(query, param)
    if not res:
        return jsonify({"message": "admin user creation failed."}), 400
    
    return jsonify({
        "message": "admin user created successfully!",
        }), 200

def loginHandler():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    
    if not username and not email:
        return jsonify({"message": "use your username or email."}), 400

    if not password:
        return jsonify({"message": "password is required."}), 400
    
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
        return jsonify({"message": "Account is not verified. Please verify your email."}), 403
    
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
    
def customerAccountHandler():
    data = request.get_json(silent=True) or {}

    email = data.get("email")

    if not email:
        return jsonify({"message": "customer email is required."}), 400

    # generate a temporary password for the customer
    username = f"CUST-{email.split('@')[0]}"
    temp_password = "".join(random.choices(string.ascii_letters + string.digits, k=12))
    password = temp_password
    hashed_password = generate_password_hash(password)
    role = 'customer'
    existing = run_query(
        """
        SELECT user_id
        FROM users
        WHERE username = %s OR email = %s
        """,
        (username, email),
        fetch="one"
    )

    if existing:
        return jsonify({"message": "user is already registered!"}), 400

    query = """ 
            INSERT INTO users 
            (username, hashed_password, email, role, email_verified) 
            VALUES (%s,%s,%s,%s,%s) 
            """
    param = (username, hashed_password, email, role, 0)
    res = run_query(query,param)

    # create customer_details too
    customer_created = run_query("""
              INSERT INTO customer_details (user_id, customer_number) 
              VALUES (%s,%s) 
              """,
              (res, f"CUST-{datetime.now().year}-{res}"))

<<<<<<< HEAD
    audit_log(
=======
    audit = audit_log(
>>>>>>> refs/remotes/origin/feature/customer-portal-api
        session["user"],
        "POST", 
        "customer", 
        res
        )
    
    # Check both inserts succeeded; audit_log always returns True so it's excluded from the condition
    if not res or not customer_created:
        return jsonify({"message": "customer account creation failed."}), 400
    
    return jsonify({
        "message": "customer account, created successfully!",
        "temp_password": temp_password
    }), 200

def AgentAccountHandler():
    conn,cursor = get_db()

    try:
        data = request.get_json()
        
        # fields
        full_name = data.get("full_name") # -> user_profile table    
        username = data.get("username")    
        email = data.get("email")
        password = data.get("password")
        confirmPassword = data.get("confirmPassword")

        fields = {
            "full_name": full_name,
            "username": username,
            "email": email,
            "password": password,
            "confirmPassword": confirmPassword 
            }

        for field, value in fields.items():
            if not value:
                return jsonify({"message": f"{field} is required."}), 400
        # check if matched
        if data["password"] != data["confirmPassword"]:
            return jsonify({"message": "password does not match."}), 400
        
        # check for duplicate entry!
        is_existing = run_query("""
                                SELECT user_id FROM users 
                                WHERE username = %s 
                                OR email = %s 
                                """,
                                (username, email),
                                fetch="one",
                                conn=conn,
                                cursor=cursor)
        
        # check if is_existing = True
        if is_existing:
            return jsonify({"message": "username or email already exists."}), 400
        # generate the hashed password
        hashedPassword = generate_password_hash(data["password"])

        result = run_query(""" 
                        INSERT INTO users 
                        (username,email,hashed_password, role, email_verified) 
                        VALUES (%s,%s,%s,%s,%s)
                        """, 
                        (data["username"], 
                         data["email"], 
                         hashedPassword, 
                         'agent', 
                         0),
                         conn=conn,
                         cursor=cursor)

        if not result:
            return jsonify({"message": "Agent Account Creation Failed."}), 500

<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> refs/remotes/origin/feature/customer-portal-api
        # for user_profile -> full name is the only not nullable
        run_query("""
                INSERT INTO user_profile (user_id, full_name) VALUES (%s,%s) 
                """,
                (result, 
                 full_name,
                 ),
                 conn=conn,
                 cursor=cursor)
<<<<<<< HEAD
=======
    # create agent details too T-T
    run_query("""
              INSERT INTO agent_details (user_id, employee_number) VALUES (%s,%s)
              """,
              (result, f"EMP-{datetime.now().year}-{result}"))
    
    token = EmailVerificationToken(result)

    if not token:
        return jsonify({"message": "Token generation failed."}), 400
=======

        # create agent details too T-T
        run_query("""
                INSERT INTO agent_details (user_id, employee_number) VALUES (%s,%s)
                """,
                (result, f"EMP-{datetime.now().year}-{result}"),
                conn=conn,
                cursor=cursor)
        
        token = EmailVerificationToken(result,conn=conn,cursor=cursor)

        if not token:
            return jsonify({"message": "Token generation failed."}), 400

        # if everything is success

        # prepare the link dedicated for 'verifyEmail' function
        link = f"http://{get_local_ip()}:5000/auth/verify?token_id={token['token_id']}&raw_token={token['raw_token']}"
        #print("token_id", token["token_id"]) # ENDPOINT TESTING
        #print("raw_token", token["raw_token"]) # for endpoint testing || delete this before pushing
        send_email_verification(email,full_name.split(" ")[0], link)
>>>>>>> refs/remotes/origin/feature/customer-portal-api

    
    link = f"http://127.0.0.1:5000/auth/verify?token_id={token["token_id"]}&token={token["token_hash"]}"
    send_email_verification(email,full_name.split(" ")[0], link)

<<<<<<< HEAD
>>>>>>> 2f24da0 (added email service / verification)
=======
        # log the creation of user
        audit_log(
            session["user"], 
            "POST", 
            "users, access_tokens, agent_details",
            result,
            conn=conn,
            cursor=cursor
            )
        
        conn.commit()
        return jsonify({
            "message": "Agent Account Created Successfully!",
            "note": f"Email verification sent to {email}"
            }), 201

    except Error as e:
        conn.rollback()
        return jsonify({
            "message": "Transaction Failed.",
            "error": str(e)
        }), 500
    finally:
        cursor.close()
        conn.close()
>>>>>>> refs/remotes/origin/feature/customer-portal-api

        # create agent details too T-T
        run_query("""
                INSERT INTO agent_details (user_id, employee_number) VALUES (%s,%s)
                """,
                (result, f"EMP-{datetime.now().year}-{result}"),
                conn=conn,
                cursor=cursor)
        
        token = EmailVerificationToken(result,conn=conn,cursor=cursor)

        if not token:
            return jsonify({"message": "Token generation failed."}), 400

        # if everything is success

        # prepare the link dedicated for 'verifyEmail' function
        link = f"http://{get_local_ip()}:5000/auth/verify?token_id={token['token_id']}&raw_token={token['raw_token']}"
        #print("token_id", token["token_id"]) # ENDPOINT TESTING
        #print("raw_token", token["raw_token"]) # for endpoint testing || delete this before pushing
        send_email_verification(email,full_name.split(" ")[0], link)

<<<<<<< HEAD

        # log the creation of user
        audit_log(
            session["user"], 
            "POST", 
            "users, access_tokens, agent_details",
            result,
            conn=conn,
            cursor=cursor
            )
        
        conn.commit()
        return jsonify({
            "message": "Agent Account Created Successfully!",
            "note": f"Email verification sent to {email}"
            }), 201

    except Error as e:
        conn.rollback()
        return jsonify({
            "message": "Transaction Failed.",
            "error": str(e)
        }), 500
    finally:
        cursor.close()
        conn.close()

=======
>>>>>>> 2f24da0 (added email service / verification)
def changePassword():
    """
        [LOGIN REQUIRED]
        CHANGE PASSWORD.
    """
    user_id = session["user"]

    data = request.get_json()

    old_password = data.get("old_password")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    required_fields = {
        "old_password": old_password,
        "new_password": new_password,
        "confirm_password": confirm_password
    }

    for field_name, value in required_fields.items():
        if not value:
            return jsonify({"message": f"{field_name} is required."}), 400

    # get the current password
    user = run_query("SELECT hashed_password FROM users WHERE user_id = %s", (user_id,), fetch="one")

    #check if old_password is equal to the current password
    if check_password_hash(user['hashed_password'], new_password):
        return jsonify({"message": "New password cannot be the same as the old password."}), 400
    
    #check if new_password is equal to the confirm_password\
    if new_password != confirm_password:
        return jsonify({"message": "password doesn't match."}), 400
    
    # check if the old_password matched
    if not check_password_hash(user["hashed_password"], old_password):
        return jsonify({"message": "Current password does not match."}), 400

    # hash the new password
    hashed_password = generate_password_hash(new_password)

    sql = f"""
            UPDATE users SET hashed_password = %s WHERE user_id = %s              
            """
    
    run_query(sql,(hashed_password, user_id))

    return jsonify({"message": "Password Updated Successfully!"})

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


def resendVerification(email):
<<<<<<< HEAD
    # Return JSON instead of HTML for API consistency
    if not email:
        return jsonify({"message": "Email is required."}), 400

    user_row = run_query("""
                        SELECT user_id FROM users 
                        WHERE email = %s
=======
    #generates new token and a link to send
    if not email:
        abort(403)
    
    # first -> get the user with the that email
    # verify if there's actually a user with that email
    # use the user_id for generating new token
    user_id = run_query("""
                        SELECT user_id FROM users 
                        WHERE email =%s
>>>>>>> refs/remotes/origin/feature/customer-portal-api
                        """,
                        (email,),
                        fetch="one")

<<<<<<< HEAD
    if not user_row:
        return jsonify({"message": "User with that email not found."}), 404

    user_id = user_row["user_id"]
    token = EmailVerificationToken(user_id)

    if not token:
        return jsonify({"message": "Token generation failed."}), 500

    link = f"http://{get_local_ip()}:5000/auth/verify?token_id={token['token_id']}&raw_token={token['raw_token']}"
    send_email_verification(email, email.split('@')[0], link)

    return jsonify({"message": "Verification email resent successfully."}), 200
=======
    if not user_id:
        abort(404) 
        
    token = EmailVerificationToken(user_id)
    
    if not token:
        abort(500)
    
    link = f"http://{get_local_ip()}:5000/auth/verify?token_id={token['token_id']}&raw_token={token['raw_token']}"

    send_email_verification(email,email.split('@')[0],link)
    
    flash("Verification email has been resent successfully.", "success")
    
    return render_template('email_verification_error.html')
>>>>>>> refs/remotes/origin/feature/customer-portal-api
    

def verifyEmail():
    token_id = request.args.get("token_id")
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> refs/remotes/origin/feature/customer-portal-api
    raw_token = request.args.get("raw_token")

    response = run_query("""
                         SELECT * FROM access_tokens 
                         WHERE token_id = %s 
                         AND token_type = 'email_verify'
                         """,
                         (token_id,),
                         fetch="one")
    
    if response is None:
       abort(404)
    
    
    user = run_query("""
                SELECT email FROM users 
                WHERE user_id = %s
                """,
                (response["user_id"],),
                fetch="one")
    
    if user is None:
        abort(404) # return not found
    
    # expiry check
    now = datetime.now(timezone.utc)
    
    expires_at = response["expires_at"]

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < now:
        return render_template('email_verification_error.html', email=user["email"])

    if response["used_at"] is not None: # if token is already used
        abort(403)

    if not raw_token:
        abort(403)

<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> refs/remotes/origin/feature/customer-portal-api
    incoming_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    if incoming_hash != response["token_hash"]:
        abort(403)

    # update the token
    run_query("""
              UPDATE access_tokens
<<<<<<< HEAD
=======
    raw_token = request.args.get("token")

    response = run_query("""
                         SELECT * FROM access_token WHERE token_id = %s AND token_type = 'email_verify'
                         """,
                         (token_id,),
                         fetch="one")
    if response is None:
        return jsonify({"message": "Invalid Token."}), 400
    
    # expiry check
    now = datetime.now(timezone.utc)
    if response["expires_at"].replace(tzinfo=timezone.utc) < now:
        return jsonify({"message": "Token Expired."}), 400
    
    if response["used_at"] is not None:
        return jsonify({"message": "Token already used."}), 400
    
    #hash 
=======
>>>>>>> f27b11c (completed the email_verification, designed email response and dynamic IP binding)
    incoming_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    if incoming_hash != response["token_hash"]:
        abort(403)

    # update the token
    run_query("""
              UPDATE access_token
>>>>>>> 2f24da0 (added email service / verification)
=======
>>>>>>> refs/remotes/origin/feature/customer-portal-api
              SET used_at = %s
              WHERE token_id =%s
              """,
              (now, token_id))
    
    run_query("""
            UPDATE users
            SET email_verified = 1
            WHERE user_id =%s
            """,
            (response["user_id"],))
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> f27b11c (completed the email_verification, designed email response and dynamic IP binding)
=======
>>>>>>> refs/remotes/origin/feature/customer-portal-api
    
    welcome_user(user["email"], 'email/welcome.html')  
    
    return render_template('email_verification_ok.html')
<<<<<<< HEAD
<<<<<<< HEAD
    
=======

    return jsonify({"message": "verification successful!"}), 200
>>>>>>> 2f24da0 (added email service / verification)
=======
    
>>>>>>> f27b11c (completed the email_verification, designed email response and dynamic IP binding)
=======
    
>>>>>>> refs/remotes/origin/feature/customer-portal-api
