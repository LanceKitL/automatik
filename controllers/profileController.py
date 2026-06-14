from flask import session,request,jsonify
from conn import run_query, get_db


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
    Update own profile information.
    """

    user_id = session.get("user")
    role = session.get("role")

    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}

    # Fields in user_profile table
    profile_fields = {
        "full_name": data.get("full_name"),
        "phone_number": data.get("phone_number"),
        "address": data.get("address"),
        "city": data.get("city"),
        "province": data.get("province"),
        "zip_code": data.get("zip_code"),
        "date_of_birth": data.get("date_of_birth"),
        "gender": data.get("gender"),
    }

    updated_fields = []

    # -------------------------
    # Update user_profile (upsert)
    # -------------------------
    profile_columns = []
    profile_values = []

    for field, value in profile_fields.items():
        if value is not None:
            profile_columns.append(field)
            profile_values.append(value)
            updated_fields.append(field)

    if profile_columns:
        columns_str = ', '.join(profile_columns + ['user_id'])
        placeholders = ', '.join(['%s'] * (len(profile_columns) + 1))
        update_set = ', '.join([f"{col} = VALUES({col})" for col in profile_columns])

        sql = f"""
            INSERT INTO user_profile ({columns_str})
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE {update_set}
        """
        run_query(sql, tuple(profile_values + [user_id]))

    # -------------------------
    # Update customer_details
    # -------------------------
    if role == "customer":
        PAYMENT_METHODS = {"cash", "installments", "bank_transfer"}
        CONTACT_METHODS = {"email", "sms", "in_app"}

        preferred_payment_method = data.get("preferred_payment_method")
        preferred_contact_method = data.get("preferred_contact_method")

        if (
            preferred_payment_method is not None
            and preferred_payment_method not in PAYMENT_METHODS
        ):
            return jsonify({
                "message": f"Invalid preferred_payment_method. Allowed values: {list(PAYMENT_METHODS)}"
            }), 400

        if (
            preferred_contact_method is not None
            and preferred_contact_method not in CONTACT_METHODS
        ):
            return jsonify({
                "message": f"Invalid preferred_contact_method. Allowed values: {list(CONTACT_METHODS)}"
            }), 400

        customer_fields = {
            "customer_number": data.get("customer_number"),
            "preferred_contact_method": preferred_contact_method,
            "preferred_payment_method": preferred_payment_method,
            "notes": data.get("notes"),
        }

        customer_updates = []
        customer_params = []

        for field, value in customer_fields.items():
            if value is not None:
                customer_updates.append(f"{field} = %s")
                customer_params.append(value)
                updated_fields.append(field)

        if customer_updates:
            customer_params.append(user_id)

            sql = f"""
                UPDATE customer_details
                SET {', '.join(customer_updates)}
                WHERE user_id = %s
            """

            run_query(sql, customer_params)

    # -------------------------
    # Final response
    # -------------------------
    if not updated_fields:
        return jsonify({
            "message": "No fields to update."
        }), 400

    return jsonify({
        "message": "Updated successfully!",
        "updated_fields": updated_fields
    }), 200