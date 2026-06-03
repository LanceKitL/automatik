from flask import Blueprint, jsonify, request, session
from conn import run_query
from validators.middleware import logged_in_required, role_required

customerportal_bp = Blueprint("customerportal", __name__)


@customerportal_bp.route("/dashboard", methods=["GET"])
@logged_in_required
@role_required("customer")
def customer_dashboard():
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


@customerportal_bp.route("/vehicles", methods=["GET"])
@logged_in_required
@role_required("customer")
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


@customerportal_bp.route("/sales", methods=["GET"])
@logged_in_required
@role_required("customer")
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


@customerportal_bp.route("/sales/<int:sale_id>", methods=["GET"])
@logged_in_required
@role_required("customer")
def get_customer_sale_detail(sale_id):
    user_id = session.get("user")

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
        return jsonify({"message": "Sale not found."}), 404

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


@customerportal_bp.route("/payments", methods=["GET"])
@logged_in_required
@role_required("customer")
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


@customerportal_bp.route("/amortization", methods=["GET"])
@logged_in_required
@role_required("customer")
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


@customerportal_bp.route("/documents", methods=["GET"])
@logged_in_required
@role_required("customer")
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


@customerportal_bp.route("/documents/<int:document_id>", methods=["GET"])
@logged_in_required
@role_required("customer")
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


@customerportal_bp.route("/inquiries", methods=["GET"])
@logged_in_required
@role_required("customer")
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


@customerportal_bp.route("/inquiries", methods=["POST"])
@logged_in_required
@role_required("customer")
def create_customer_inquiry():
    user_id = session.get("user")
    data = request.get_json()

    vehicle_id = data.get("vehicle_id")
    message = data.get("message")

    if not vehicle_id or not message:
        return jsonify({
            "message": "vehicle_id and message are required."
        }), 400

    run_query("""
        INSERT INTO inquiries (user_id, vehicle_id, message, status)
        VALUES (%s, %s, %s, 'open')
    """, (user_id, vehicle_id, message))

    return jsonify({
        "message": "Inquiry submitted successfully."
    }), 201


@customerportal_bp.route("/notifications", methods=["GET"])
@logged_in_required
@role_required("customer")
def get_customer_notifications():
    user_id = session.get("user")

    notifications = run_query("""
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
        ORDER BY created_at DESC
    """, (user_id,), fetch="all")

    return jsonify({
        "message": "Customer notifications fetched successfully.",
        "data": notifications
    }), 200


@customerportal_bp.route("/notifications/<int:notification_id>/read", methods=["PUT"])
@logged_in_required
@role_required("customer")
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


@customerportal_bp.route("/profile", methods=["PUT"])
@logged_in_required
@role_required("customer")
def update_customer_profile():
    user_id = session.get("user")
    data = request.get_json()

    run_query("""
        UPDATE user_profile
        SET 
            full_name = COALESCE(%s, full_name),
            phone_number = COALESCE(%s, phone_number),
            address = COALESCE(%s, address),
            city = COALESCE(%s, city),
            province = COALESCE(%s, province),
            zip_code = COALESCE(%s, zip_code),
            profile_picture_url = COALESCE(%s, profile_picture_url)
        WHERE user_id = %s
    """, (
        data.get("full_name"),
        data.get("phone_number"),
        data.get("address"),
        data.get("city"),
        data.get("province"),
        data.get("zip_code"),
        data.get("profile_picture_url"),
        user_id
    ))

    run_query("""
        UPDATE customer_details
        SET 
            preferred_contact_method = COALESCE(%s, preferred_contact_method),
            preferred_payment_method = COALESCE(%s, preferred_payment_method)
        WHERE user_id = %s
    """, (
        data.get("preferred_contact_method"),
        data.get("preferred_payment_method"),
        user_id
    ))

    return jsonify({
        "message": "Customer profile updated successfully."
    }), 200


@customerportal_bp.route("/insurance", methods=["GET"])
@logged_in_required
@role_required("customer")
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


@customerportal_bp.route("/warranty", methods=["GET"])
@logged_in_required
@role_required("customer")
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


@customerportal_bp.route("/warranty", methods=["POST"])
@logged_in_required
@role_required("customer")
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

    return jsonify({
        "message": "Warranty claim submitted successfully."
    }), 201