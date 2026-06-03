from flask import jsonify, request, session
from conn import run_query

VALID_CLAIM_TYPES = ['repair', 'replacement', 'refund']
VALID_CONTACT_METHODS = ['email', 'sms', 'whatsapp']
VALID_PAYMENT_METHODS = ['cash', 'installment', 'bank_transfer']


def get_dashboard():
    user_id = session.get("user")

    active_sales = run_query("""
        SELECT COUNT(*) AS total
        FROM sales
        WHERE customer_id = %s AND status = 'active'
    """, (user_id,), fetch="one")

    next_payment_due = run_query("""
        SELECT 
            a.schedule_id,
            a.due_date,
            a.total_due,
            a.status
        FROM amortization_schedule a
        INNER JOIN loan_details l ON a.loan_id = l.loan_id
        INNER JOIN sales s ON l.sale_id = s.sale_id
        WHERE s.customer_id = %s AND a.status IN ('unpaid', 'overdue')
        ORDER BY a.due_date ASC
        LIMIT 1
    """, (user_id,), fetch="one")

    open_inquiries = run_query("""
        SELECT COUNT(*) AS total
        FROM inquiries
        WHERE user_id = %s AND status IN ('open', 'assigned')
    """, (user_id,), fetch="one")

    unread_notifications = run_query("""
        SELECT COUNT(*) AS total
        FROM notifications
        WHERE user_id = %s AND is_read = 0
    """, (user_id,), fetch="one")

    return jsonify({
        "message": "Customer dashboard fetched successfully.",
        "data": {
            "active_sales": active_sales["total"] if active_sales else 0,
            "next_payment_due": next_payment_due,
            "open_inquiries": open_inquiries["total"] if open_inquiries else 0,
            "unread_notifications": unread_notifications["total"] if unread_notifications else 0
        }
    }), 200


def browse_available_vehicles():
    vehicles = run_query("""
        SELECT 
            vehicle_id,
            brand,
            model,
            year,
            color,
            body_type,
            transmission,
            fuel_type,
            price,
            status
        FROM vehicles
        WHERE status = 'available'
        ORDER BY created_at DESC
    """, fetch="all")

    return jsonify({
        "message": "Available vehicles fetched successfully.",
        "data": vehicles
    }), 200


def get_customer_sales():
    user_id = session.get("user")

    sales = run_query("""
        SELECT 
            s.sale_id,
            s.vehicle_id,
            s.selling_price,
            s.payment_type,
            s.sale_date,
            s.status,
            v.brand,
            v.model,
            v.year,
            v.color
        FROM sales s
        INNER JOIN vehicles v ON s.vehicle_id = v.vehicle_id
        WHERE s.customer_id = %s
        ORDER BY s.sale_date DESC
    """, (user_id,), fetch="all")

    return jsonify({
        "message": "Customer sales fetched successfully.",
        "data": sales
    }), 200


def get_customer_sale_detail(sale_id):
    user_id = session.get("user")

    sale_exists = run_query("""
        SELECT sale_id FROM sales WHERE sale_id = %s
    """, (sale_id,), fetch="one")

    if not sale_exists:
        return jsonify({"message": "Sale not found."}), 404

    sale = run_query("""
        SELECT 
            s.sale_id,
            s.vehicle_id,
            s.selling_price,
            s.payment_type,
            s.sale_date,
            s.status,
            v.brand,
            v.model,
            v.year,
            v.color,
            v.vin
        FROM sales s
        INNER JOIN vehicles v ON s.vehicle_id = v.vehicle_id
        WHERE s.sale_id = %s AND s.customer_id = %s
    """, (sale_id, user_id), fetch="one")

    if not sale:
        return jsonify({"message": "Sale does not belong to you."}), 403

    loan = run_query("""
        SELECT 
            loan_id,
            down_payment,
            loan_amount,
            interest_rate,
            term_months,
            monthly_amortization,
            bank_name,
            bank_approval_status
        FROM loan_details
        WHERE sale_id = %s
    """, (sale_id,), fetch="one")

    amortization = run_query("""
        SELECT 
            a.schedule_id,
            a.month_number,
            a.due_date,
            a.principal,
            a.interest,
            a.total_due,
            a.running_balance,
            a.status
        FROM amortization_schedule a
        INNER JOIN loan_details l ON a.loan_id = l.loan_id
        WHERE l.sale_id = %s
        ORDER BY a.month_number ASC
    """, (sale_id,), fetch="all")

    payments = run_query("""
        SELECT 
            payment_id,
            amount_paid,
            payment_date,
            payment_method,
            reference
        FROM payments
        WHERE sale_id = %s
        ORDER BY payment_date DESC
    """, (sale_id,), fetch="all")

    return jsonify({
        "message": "Sale detail fetched successfully.",
        "data": {
            "sale": sale,
            "loan": loan,
            "amortization_schedule": amortization,
            "payments": payments
        }
    }), 200


def get_customer_payments():
    user_id = session.get("user")

    payments = run_query("""
        SELECT 
            p.payment_id,
            p.sale_id,
            p.amount_paid,
            p.payment_date,
            p.payment_method,
            p.reference
        FROM payments p
        INNER JOIN sales s ON p.sale_id = s.sale_id
        WHERE s.customer_id = %s
        ORDER BY p.payment_date DESC
    """, (user_id,), fetch="all")

    return jsonify({
        "message": "Customer payment history fetched successfully.",
        "data": payments
    }), 200


def get_customer_amortization():
    user_id = session.get("user")

    schedule = run_query("""
        SELECT 
            s.sale_id,
            l.loan_id,
            a.schedule_id,
            a.month_number,
            a.due_date,
            a.principal,
            a.interest,
            a.total_due,
            a.running_balance,
            a.status
        FROM amortization_schedule a
        INNER JOIN loan_details l ON a.loan_id = l.loan_id
        INNER JOIN sales s ON l.sale_id = s.sale_id
        WHERE s.customer_id = %s
        ORDER BY a.due_date ASC
    """, (user_id,), fetch="all")

    return jsonify({
        "message": "Amortization schedule fetched successfully.",
        "data": schedule
    }), 200


def get_customer_documents():
    user_id = session.get("user")

    documents = run_query("""
        SELECT 
            d.document_id,
            d.sale_id,
            d.document_type,
            d.file_url,
            d.is_accessible,
            d.created_at
        FROM documents d
        INNER JOIN sales s ON d.sale_id = s.sale_id
        WHERE s.customer_id = %s AND d.is_accessible = 1
        ORDER BY d.created_at DESC
    """, (user_id,), fetch="all")

    return jsonify({
        "message": "Customer documents fetched successfully.",
        "data": documents
    }), 200


def get_customer_document_detail(document_id):
    user_id = session.get("user")

    document = run_query("""
        SELECT 
            d.document_id,
            d.sale_id,
            d.document_type,
            d.file_url,
            d.is_accessible,
            d.created_at
        FROM documents d
        INNER JOIN sales s ON d.sale_id = s.sale_id
        WHERE d.document_id = %s 
        AND s.customer_id = %s 
        AND d.is_accessible = 1
    """, (document_id, user_id), fetch="one")

    if not document:
        return jsonify({
            "message": "Document not found or not accessible."
        }), 404

    return jsonify({
        "message": "Document fetched successfully.",
        "data": document
    }), 200


def get_customer_inquiries():
    user_id = session.get("user")

    inquiries = run_query("""
        SELECT 
            inquiry_id,
            vehicle_id,
            agent_id,
            message,
            status,
            created_at,
            resolved_at
        FROM inquiries
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (user_id,), fetch="all")

    return jsonify({
        "message": "Customer inquiries fetched successfully.",
        "data": inquiries
    }), 200


def create_customer_inquiry():
    user_id = session.get("user")
    data = request.get_json()

    vehicle_id = data.get("vehicle_id")
    message = data.get("message")

    if not vehicle_id or not message:
        return jsonify({
            "message": "vehicle_id and message are required."
        }), 400

    if len(message) > 1000:
        return jsonify({
            "message": "message must not exceed 1000 characters."
        }), 422

    run_query("""
        INSERT INTO inquiries (user_id, vehicle_id, message, status)
        VALUES (%s, %s, %s, 'open')
    """, (user_id, vehicle_id, message))

    # TODO: audit_log(user_id, "POST", "inquiries", inquiry_id, ...)
    # TODO: FIRE_NOTIF to notify agents/admins about new inquiry (CAPSLOCK = needs notification)

    return jsonify({
        "message": "Inquiry submitted successfully."
    }), 201


def get_customer_notifications():
    user_id = session.get("user")
    is_read_filter = request.args.get("is_read")

    query = """
        SELECT 
            notification_id,
            title,
            message,
            channel,
            ref_type,
            ref_id,
            is_read,
            created_at
        FROM notifications
        WHERE user_id = %s
    """
    params = [user_id]

    if is_read_filter is not None:
        query += " AND is_read = %s"
        params.append(int(is_read_filter))

    query += " ORDER BY created_at DESC"

    notifications = run_query(query, params, fetch="all")

    return jsonify({
        "message": "Customer notifications fetched successfully.",
        "data": notifications
    }), 200


def mark_customer_notification_read(notification_id):
    user_id = session.get("user")

    notification = run_query("""
        SELECT notification_id
        FROM notifications
        WHERE notification_id = %s AND user_id = %s
    """, (notification_id, user_id), fetch="one")

    if not notification:
        return jsonify({
            "message": "Notification not found."
        }), 404

    run_query("""
        UPDATE notifications
        SET is_read = 1
        WHERE notification_id = %s AND user_id = %s
    """, (notification_id, user_id))

    return jsonify({
        "message": "Notification marked as read successfully."
    }), 200


def update_customer_profile():
    user_id = session.get("user")
    data = request.get_json()

    allowed_profile_fields = {
        "full_name": data.get("full_name"),
        "phone_number": data.get("phone_number"),
        "address": data.get("address"),
        "city": data.get("city"),
        "province": data.get("province"),
        "zip_code": data.get("zip_code"),
        "profile_picture_url": data.get("profile_picture_url"),
    }

    contact_method = data.get("preferred_contact_method")
    payment_method = data.get("preferred_payment_method")

    if contact_method and contact_method not in VALID_CONTACT_METHODS:
        return jsonify({
            "message": f"preferred_contact_method must be one of: {', '.join(VALID_CONTACT_METHODS)}"
        }), 422

    if payment_method and payment_method not in VALID_PAYMENT_METHODS:
        return jsonify({
            "message": f"preferred_payment_method must be one of: {', '.join(VALID_PAYMENT_METHODS)}"
        }), 422

    updated_fields = []
    set_clauses = []
    params = []

    for field, value in allowed_profile_fields.items():
        if value is not None:
            set_clauses.append(f"{field} = %s")
            params.append(value)
            updated_fields.append(field)

    profile_exists = run_query("""
        SELECT user_id FROM user_profile WHERE user_id = %s
    """, (user_id,), fetch="one")

    if set_clauses:
        params.append(user_id)
        if profile_exists:
            run_query(f"""
                UPDATE user_profile
                SET {', '.join(set_clauses)}
                WHERE user_id = %s
            """, params)
        else:
            cols = [s.split(" =")[0].strip() for s in set_clauses]
            placeholders = ", ".join(["%s"] * len(cols))
            col_names = ", ".join(cols)
            insert_params = [value for field, value in allowed_profile_fields.items() if value is not None]
            insert_params.append(user_id)
            run_query(f"""
                INSERT INTO user_profile ({col_names}, user_id)
                VALUES ({placeholders}, %s)
            """, insert_params)

    customer_fields = {}
    if contact_method is not None:
        customer_fields["preferred_contact_method"] = contact_method
    if payment_method is not None:
        customer_fields["preferred_payment_method"] = payment_method

    if customer_fields:
        customer_exists = run_query("""
            SELECT user_id FROM customer_details WHERE user_id = %s
        """, (user_id,), fetch="one")

        customer_set = [f"{k} = %s" for k in customer_fields]
        customer_params = list(customer_fields.values())
        customer_params.append(user_id)

        if customer_exists:
            run_query(f"""
                UPDATE customer_details
                SET {', '.join(customer_set)}
                WHERE user_id = %s
            """, customer_params)
        else:
            cols = list(customer_fields.keys())
            placeholders = ", ".join(["%s"] * len(cols))
            col_names = ", ".join(cols)
            insert_params = list(customer_fields.values()) + [user_id]
            run_query(f"""
                INSERT INTO customer_details ({col_names}, user_id)
                VALUES ({placeholders}, %s)
            """, insert_params)

        updated_fields.extend(customer_fields.keys())

    if not updated_fields:
        return jsonify({"message": "No fields to update."}), 400

    # TODO: audit_log(user_id, "PUT", "user_profile", user_id, old_values, new_values)
    # TODO: audit_log(user_id, "PUT", "customer_details", user_id, old_values, new_values)

    return jsonify({
        "message": "Customer profile updated successfully.",
        "updated_fields": updated_fields
    }), 200


def get_customer_insurance():
    user_id = session.get("user")

    insurance = run_query("""
        SELECT 
            i.insurance_id,
            i.sale_id,
            i.vehicle_id,
            i.provider_name,
            i.policy_number,
            i.coverage_type,
            i.start_date,
            i.end_date,
            i.status
        FROM insurance_records i
        INNER JOIN sales s ON i.sale_id = s.sale_id
        WHERE s.customer_id = %s
        ORDER BY i.end_date DESC
    """, (user_id,), fetch="all")

    return jsonify({
        "message": "Customer insurance records fetched successfully.",
        "data": insurance
    }), 200


def get_customer_warranty_claims():
    user_id = session.get("user")

    claims = run_query("""
        SELECT 
            w.claim_id,
            w.sale_id,
            w.vehicle_id,
            w.claim_type,
            w.description,
            w.status,
            w.resolution,
            w.submitted_at,
            w.resolved_at
        FROM warranty_claims w
        INNER JOIN sales s ON w.sale_id = s.sale_id
        WHERE s.customer_id = %s
        ORDER BY w.submitted_at DESC
    """, (user_id,), fetch="all")

    return jsonify({
        "message": "Customer warranty claims fetched successfully.",
        "data": claims
    }), 200


def create_customer_warranty_claim():
    user_id = session.get("user")
    data = request.get_json()

    sale_id = data.get("sale_id")
    vehicle_id = data.get("vehicle_id")
    claim_type = data.get("claim_type")
    description = data.get("description")

    if not sale_id or not vehicle_id or not claim_type or not description:
        return jsonify({
            "message": "sale_id, vehicle_id, claim_type, and description are required."
        }), 400

    if claim_type not in VALID_CLAIM_TYPES:
        return jsonify({
            "message": f"claim_type must be one of: {', '.join(VALID_CLAIM_TYPES)}"
        }), 422

    if len(description) > 1000:
        return jsonify({
            "message": "description must not exceed 1000 characters."
        }), 422

    sale = run_query("""
        SELECT sale_id
        FROM sales
        WHERE sale_id = %s AND vehicle_id = %s AND customer_id = %s
    """, (sale_id, vehicle_id, user_id), fetch="one")

    if not sale:
        return jsonify({
            "message": "Sale ownership could not be verified."
        }), 403

    run_query("""
        INSERT INTO warranty_claims 
        (sale_id, vehicle_id, claim_type, description, status)
        VALUES (%s, %s, %s, %s, 'submitted')
    """, (sale_id, vehicle_id, claim_type, description))

    # TODO: audit_log(user_id, "POST", "warranty_claims", claim_id, ...)
    # TODO: FIRE_NOTIF to notify agents/admins about new warranty claim (CAPSLOCK = needs notification)

    return jsonify({
        "message": "Warranty claim submitted successfully."
    }), 201
