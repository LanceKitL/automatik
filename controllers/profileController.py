from flask import session,request,jsonify
from conn import run_query


def get_profile():
    """ 
    [LOGIN REQUIRED]
    View own profile. JOIN users + user_profile.
    """
    # get logged in user
    user_id = session["user"]

    user = run_query("""
                    SELECT username, email, role FROM users WHERE user_id = %s
                    """, 
                    (user_id,), 
                    fetch="one")

    profile = run_query("SELECT * FROM user_profile WHERE user_id = %s", (user_id, ), fetch="one")

    if not user:
        return jsonify({"message": "user not found."}), 404

    if profile is None:
        profile = {}

    user["profile"] = profile

    return jsonify({"message": user})

def update_profile():
    """
    [LOGIN REQUIRED]
    update own user_profile fields.
    allowed fields: [full_name,phone_number,address,city,province,zip_code,date_of_birth,gender]
    """
    # get the current signed_in user
    user_id = session["user"]


    data = request.get_json(silent=True) or {}
    
    full_name = data.get("full_name")
    phone_number = data.get("phone_number")
    address = data.get("address")
    city = data.get("city")
    province = data.get("province")
    zip_code = data.get("zip_code")
    date_of_birth = data.get("date_of_birth")
    gender = data.get("gender")

    allowed_fields = {
        "full_name": full_name,
        "phone_number": phone_number,
        "address": address,
        "city": city,
        "province": province,
        "zip_code": zip_code,
        "date_of_birth": date_of_birth,
        "gender": gender,
    }

    update = []
    params = []
    updated_fields = []

    for field_name, value in allowed_fields.items():
        if value is not None:
            update.append(f"{field_name} = %s")
            params.append(value)
            updated_fields.append(field_name)

    if not update:
        return jsonify({"message": "no fields to update."}), 400
    
    params.append(user_id)

    sql = f"""
        UPDATE user_profile
        SET {', '.join(update)}
        WHERE user_id = %s
        """

    run_query(sql, params)

    return jsonify({
        "message": "updated succesfully!",
        "updated_fields": updated_fields
        })
