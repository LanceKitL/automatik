from werkzeug.security import check_password_hash, generate_password_hash
from utils.token_helper import EmailVerificationToken, PasswordResetToken
from flask import session, jsonify, request, render_template, abort
from services.mail_service import send_email_verification, welcome_user, send_password_reset, send_password_reset_confirmation
from datetime import datetime, timezone
from conn import run_query, get_db, Error
from utils.log import audit_log, get_local_ip
import hashlib
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
    
    if user["is_active"] == 0:
        return jsonify({"message": "Your account is disabled. Contact support to reactivate your account."}), 403
    
    # check if the password match
    if not check_password_hash(user["hashed_password"], password):
        return jsonify({"message": "Invalid Credentials."}),403
    
    # user logs in successfull!
    session["user"] = user["user_id"] # stores the user id
    session["role"] = user["role"] # store the user role
    session.permanent = True # activate the expiration time

    return jsonify({
        "message": "Logged in successfully!",
        "user": {
            "user_id": user["user_id"],
            "role": user["role"],
            "email": user["email"],
            "username": user["username"],
        }
    }), 200
    
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

    audit_log(
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

        # for user_profile -> full name is the only not nullable
        run_query("""
                INSERT INTO user_profile (user_id, full_name) VALUES (%s,%s) 
                """,
                (result, 
                 full_name,
                 ),
                 conn=conn,
                 cursor=cursor)

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
              UPDATE users SET last_login = %s
              WHERE user_id = %s 
              """, 
              (last_login, user))
    
    session.clear()
    return jsonify({"message": "Logged out success."}), 200


def resendVerification(email):
    # Return JSON instead of HTML for API consistency
    if not email:
        return jsonify({"message": "Email is required."}), 400

    user_row = run_query("""
                        SELECT user_id FROM users 
                        WHERE email = %s
                        """,
                        (email,),
                        fetch="one")

    if not user_row:
        return jsonify({"message": "User with that email not found."}), 404

    user_id = user_row["user_id"]
    token = EmailVerificationToken(user_id)

    if not token:
        return jsonify({"message": "Token generation failed."}), 500

    link = f"http://{get_local_ip()}:5000/auth/verify?token_id={token['token_id']}&raw_token={token['raw_token']}"
    send_email_verification(email, email.split('@')[0], link)

    return jsonify({"message": "Verification email resent successfully."}), 200
    

def verifyEmail():
    token_id = request.args.get("token_id")
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

    incoming_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    if incoming_hash != response["token_hash"]:
        abort(403)

    # update the token
    run_query("""
              UPDATE access_tokens
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
    
    from utils.log import get_local_ip
    portal_url = f"http://{get_local_ip()}:5173"
    welcome_user(user["email"], 'email/welcome.html', portal_url=portal_url)  
    
    return render_template('email_verification_ok.html')
    

def forgotPassword():
    """
    [PUBLIC]
    Send a password reset link to the user's email.
    Always returns the same message to prevent email enumeration.
    Rate-limited by the token mechanism (3 active tokens max per user).
    """
    data = request.get_json(silent=True) or {}
    email = data.get("email")

    if not email:
        return jsonify({"message": "Email is required."}), 400

    user = run_query(
        "SELECT user_id, email FROM users WHERE email = %s",
        (email,),
        fetch="one"
    )

    # Always return the same message regardless of whether the email exists
    # to prevent user enumeration attacks.
    if not user:
        return jsonify({"message": "If that email exists, a reset link has been sent."}), 200

    token = PasswordResetToken(user["user_id"])

    if not token:
        return jsonify({"message": "Token generation failed."}), 500

    reset_url = f"http://localhost:5173/auth/reset-password?token_id={token['token_id']}&raw_token={token['raw_token']}"
    send_password_reset(email, reset_url)

    return jsonify({"message": "If that email exists, a reset link has been sent."}), 200


def resetPassword():
    """
    [PUBLIC] (token-based)
    Reset the user's password using a valid reset token.
    Validates: token exists, not expired, not already used, hash matches.
    Sends confirmation email on success.
    """
    data = request.get_json(silent=True) or {}
    token_id = data.get("token_id")
    raw_token = data.get("raw_token")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    if not all([token_id, raw_token, new_password, confirm_password]):
        return jsonify({"message": "token_id, raw_token, new_password, and confirm_password are required."}), 400

    if new_password != confirm_password:
        return jsonify({"message": "Passwords do not match."}), 400

    response = run_query("""
                         SELECT * FROM access_tokens
                         WHERE token_id = %s
                         AND token_type = 'password_reset'
                         """,
                         (token_id,),
                         fetch="one")

    if response is None:
        return jsonify({"message": "Invalid or expired reset link."}), 404

    now = datetime.now(timezone.utc)
    expires_at = response["expires_at"]
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < now:
        return jsonify({"message": "Reset link has expired."}), 400

    if response["used_at"] is not None:
        return jsonify({"message": "Reset link has already been used."}), 400

    if not raw_token:
        return jsonify({"message": "Invalid token."}), 400

    incoming_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    if incoming_hash != response["token_hash"]:
        return jsonify({"message": "Invalid token."}), 403

    hashed_password = generate_password_hash(new_password)

    # Mark token as used to prevent replay attacks
    run_query("UPDATE access_tokens SET used_at = %s WHERE token_id = %s",
              (now, token_id))

    # Update the user's password
    run_query("UPDATE users SET hashed_password = %s WHERE user_id = %s",
              (hashed_password, response["user_id"]))

    # Send confirmation email
    user = run_query("SELECT email FROM users WHERE user_id = %s",
                     (response["user_id"],), fetch="one")

    if user:
        send_password_reset_confirmation(user["email"])

    return jsonify({"message": "Password has been reset successfully."}), 200