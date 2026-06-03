from conn import run_query
from flask import session, jsonify, request
from datetime import datetime
from utils.log import audit_log
from utils.notification import fire_notif, brodcast_notif
from services.mail_service import send_new_inquiry_notification, send_warranty_claim_notification
import json


def index():
    customer_id = session["user"]

    user = run_query(
        "SELECT username, email FROM users WHERE user_id = %s",
        (customer_id,),
        fetch="one",
    )
    if not user:
        return jsonify({"message": "Customer not found."}), 404

    profile = run_query(
        "SELECT full_name FROM user_profile WHERE user_id = %s",
        (customer_id,),
        fetch="one",
    )

    inquiry_count = run_query(
        "SELECT COUNT(*) AS cnt FROM inquiries WHERE user_id = %s",
        (customer_id,),
        fetch="one",
    )
    claim_count = run_query(
        """SELECT COUNT(*) AS cnt FROM warranty_claims wc
           JOIN sales s ON wc.sale_id = s.sale_id
           WHERE s.customer_id = %s""",
        (customer_id,),
        fetch="one",
    )
    sale_count = run_query(
        "SELECT COUNT(*) AS cnt FROM sales WHERE customer_id = %s",
        (customer_id,),
        fetch="one",
    )

    return jsonify({
        "customer_id": customer_id,
        "username": user["username"],
        "email": user["email"],
        "full_name": profile["full_name"] if profile else None,
        "inquiry_count": inquiry_count["cnt"],
        "warranty_claim_count": claim_count["cnt"],
        "sale_count": sale_count["cnt"],
    })


def get_customer_inquiries():
    customer_id = session["user"]

    res = run_query(
        """SELECT i.*, v.brand, v.model, v.color, v.body_type, v.price
           FROM inquiries i
           JOIN vehicles v ON i.vehicle_id = v.vehicle_id
           WHERE i.user_id = %s
           ORDER BY i.created_at DESC""",
        (customer_id,),
        fetch="all",
    )

    formatted = []
    for row in res:
        formatted.append({
            "inquiry_id": row["inquiry_id"],
            "agent_assigned": row["agent_id"],
            "message": row["message"],
            "status": row["status"],
            "created_at": row["created_at"],
            "resolved_at": row["resolved_at"],
            "vehicle": {
                "brand": row["brand"],
                "model": row["model"],
                "color": row["color"],
                "body_type": row["body_type"],
                "price": row["price"],
            },
        })

    return jsonify(formatted), 200


def get_customer_inquiry(inquiry_id):
    customer_id = session["user"]

    row = run_query(
        """SELECT i.*, v.brand, v.model, v.color, v.body_type, v.price
           FROM inquiries i
           JOIN vehicles v ON i.vehicle_id = v.vehicle_id
           WHERE i.inquiry_id = %s AND i.user_id = %s""",
        (inquiry_id, customer_id),
        fetch="one",
    )

    if not row:
        return jsonify({"message": "Inquiry not found."}), 404

    return jsonify({
        "inquiry_id": row["inquiry_id"],
        "agent_assigned": row["agent_id"],
        "message": row["message"],
        "status": row["status"],
        "created_at": row["created_at"],
        "resolved_at": row["resolved_at"],
        "vehicle": {
            "brand": row["brand"],
            "model": row["model"],
            "color": row["color"],
            "body_type": row["body_type"],
            "price": row["price"],
        },
    }), 200


def create_customer_inquiry():
    customer_id = session["user"]
    data = request.get_json()

    vehicle_id = data.get("vehicle_id")
    message = data.get("message")

    if not vehicle_id:
        return jsonify({"message": "vehicle_id is required."}), 400
    if not message:
        return jsonify({"message": "Inquiry message is required."}), 400
    if len(message) > 1000:
        return jsonify({"message": "Message must be 1000 characters or fewer."}), 422

    vehicle = run_query(
        "SELECT vehicle_id, brand, model FROM vehicles WHERE vehicle_id = %s",
        (vehicle_id,),
        fetch="one",
    )
    if not vehicle:
        return jsonify({"message": "Vehicle not found."}), 404

    inquiry_id = run_query(
        """INSERT INTO inquiries (user_id, vehicle_id, message, status)
           VALUES (%s, %s, %s, 'open')""",
        (customer_id, vehicle_id, message),
    )

    audit_log(
        id=customer_id,
        action="POST",
        tablename="inquiries",
        record_id=inquiry_id,
    )

    fire_notif(
        user_id=customer_id,
        title="Inquiry Submitted",
        message="Your inquiry has been received. An agent will follow up shortly.",
        channel="in_app",
        ref_type="inquiries",
        ref_id=inquiry_id,
    )

    brodcast_notif(
        role="admin",
        title="New Customer Inquiry",
        message=f"Customer #{customer_id} sent an inquiry about {vehicle['brand']} {vehicle['model']}.",
        channel="in_app",
        ref_type="inquiries",
        ref_id=inquiry_id,
    )

    brodcast_notif(
        role="agent",
        title="New Customer Inquiry",
        message=f"Customer #{customer_id} sent an inquiry about {vehicle['brand']} {vehicle['model']}.",
        channel="in_app",
        ref_type="inquiries",
        ref_id=inquiry_id,
    )

    send_new_inquiry_notification(
        customer_id=customer_id,
        inquiry_id=inquiry_id,
        vehicle_name=f"{vehicle['brand']} {vehicle['model']}",
        message=message,
    )

    return jsonify({
        "message": "Inquiry submitted successfully.",
        "inquiry_id": inquiry_id,
    }), 201


def get_customer_warranty_claims():
    customer_id = session["user"]

    res = run_query(
        """SELECT wc.*, v.brand, v.model
           FROM warranty_claims wc
           JOIN sales s ON wc.sale_id = s.sale_id
           JOIN vehicles v ON wc.vehicle_id = v.vehicle_id
           WHERE s.customer_id = %s
           ORDER BY wc.submitted_at DESC""",
        (customer_id,),
        fetch="all",
    )

    formatted = []
    for row in res:
        formatted.append({
            "claim_id": row["claim_id"],
            "sale_id": row["sale_id"],
            "claim_type": row["claim_type"],
            "description": row["description"],
            "status": row["status"],
            "resolution": row["resolution"],
            "submitted_at": row["submitted_at"],
            "resolved_at": row["resolved_at"],
            "vehicle": {
                "brand": row["brand"],
                "model": row["model"],
            },
        })

    return jsonify(formatted), 200


def get_customer_warranty_claim(claim_id):
    customer_id = session["user"]

    row = run_query(
        """SELECT wc.*, v.brand, v.model
           FROM warranty_claims wc
           JOIN sales s ON wc.sale_id = s.sale_id
           JOIN vehicles v ON wc.vehicle_id = v.vehicle_id
           WHERE wc.claim_id = %s AND s.customer_id = %s""",
        (claim_id, customer_id),
        fetch="one",
    )

    if not row:
        return jsonify({"message": "Warranty claim not found."}), 404

    return jsonify({
        "claim_id": row["claim_id"],
        "sale_id": row["sale_id"],
        "claim_type": row["claim_type"],
        "description": row["description"],
        "status": row["status"],
        "resolution": row["resolution"],
        "submitted_at": row["submitted_at"],
        "resolved_at": row["resolved_at"],
        "vehicle": {
            "brand": row["brand"],
            "model": row["model"],
        },
    }), 200


def create_customer_warranty_claim():
    customer_id = session["user"]
    data = request.get_json()

    sale_id = data.get("sale_id")
    vehicle_id = data.get("vehicle_id")
    claim_type = data.get("claim_type")
    description = data.get("description")

    if not sale_id:
        return jsonify({"message": "sale_id is required."}), 400
    if not vehicle_id:
        return jsonify({"message": "vehicle_id is required."}), 400
    if not claim_type:
        return jsonify({"message": "claim_type is required."}), 400
    if claim_type not in ("repair", "replacement", "refund"):
        return jsonify({"message": "claim_type must be repair, replacement, or refund."}), 422
    if not description:
        return jsonify({"message": "Description is required."}), 400
    if len(description) > 2000:
        return jsonify({"message": "Description must be 2000 characters or fewer."}), 422

    sale = run_query(
        """SELECT s.*, v.brand, v.model FROM sales s
           JOIN vehicles v ON s.vehicle_id = v.vehicle_id
           WHERE s.sale_id = %s AND s.customer_id = %s""",
        (sale_id, customer_id),
        fetch="one",
    )
    if not sale:
        return jsonify({"message": "Sale not found or does not belong to you."}), 404

    vehicle = run_query(
        "SELECT vehicle_id FROM vehicles WHERE vehicle_id = %s",
        (vehicle_id,),
        fetch="one",
    )
    if not vehicle:
        return jsonify({"message": "Vehicle not found."}), 404

    claim_id = run_query(
        """INSERT INTO warranty_claims (sale_id, vehicle_id, claim_type, description, status)
           VALUES (%s, %s, %s, %s, 'submitted')""",
        (sale_id, vehicle_id, claim_type, description),
    )

    audit_log(
        id=customer_id,
        action="POST",
        tablename="warranty_claims",
        record_id=claim_id,
    )

    fire_notif(
        user_id=customer_id,
        title="Warranty Claim Submitted",
        message="Your warranty claim has been received and is under review.",
        channel="in_app",
        ref_type="warranty_claims",
        ref_id=claim_id,
    )

    brodcast_notif(
        role="admin",
        title="New Warranty Claim",
        message=f"Customer #{customer_id} submitted a {claim_type} claim for {sale['brand']} {sale['model']}.",
        channel="in_app",
        ref_type="warranty_claims",
        ref_id=claim_id,
    )

    brodcast_notif(
        role="agent",
        title="New Warranty Claim",
        message=f"Customer #{customer_id} submitted a {claim_type} claim for {sale['brand']} {sale['model']}.",
        channel="in_app",
        ref_type="warranty_claims",
        ref_id=claim_id,
    )

    send_warranty_claim_notification(
        customer_id=customer_id,
        claim_id=claim_id,
        claim_type=claim_type,
        description=description,
        vehicle_name=f"{sale['brand']} {sale['model']}",
    )

    return jsonify({
        "message": "Warranty claim submitted successfully.",
        "claim_id": claim_id,
    }), 201


def get_customer_sales():
    customer_id = session["user"]

    res = run_query(
        """SELECT s.*, v.brand, v.model, v.year, v.color, v.body_type, v.price AS vehicle_price
           FROM sales s
           JOIN vehicles v ON s.vehicle_id = v.vehicle_id
           WHERE s.customer_id = %s
           ORDER BY s.created_at DESC""",
        (customer_id,),
        fetch="all",
    )

    formatted = []
    for row in res:
        formatted.append({
            "sale_id": row["sale_id"],
            "vehicle_id": row["vehicle_id"],
            "agent_id": row["agent_id"],
            "selling_price": row["selling_price"],
            "payment_type": row["payment_type"],
            "sale_date": row["sale_date"],
            "status": row["status"],
            "vehicle": {
                "brand": row["brand"],
                "model": row["model"],
                "year": row["year"],
                "color": row["color"],
                "body_type": row["body_type"],
            },
        })

    return jsonify(formatted), 200


def get_customer_sale(sale_id):
    customer_id = session["user"]

    row = run_query(
        """SELECT s.*, v.brand, v.model, v.year, v.color, v.body_type, v.price AS vehicle_price
           FROM sales s
           JOIN vehicles v ON s.vehicle_id = v.vehicle_id
           WHERE s.sale_id = %s AND s.customer_id = %s""",
        (sale_id, customer_id),
        fetch="one",
    )

    if not row:
        return jsonify({"message": "Sale not found."}), 404

    return jsonify({
        "sale_id": row["sale_id"],
        "vehicle_id": row["vehicle_id"],
        "agent_id": row["agent_id"],
        "selling_price": row["selling_price"],
        "payment_type": row["payment_type"],
        "sale_date": row["sale_date"],
        "status": row["status"],
        "vehicle": {
            "brand": row["brand"],
            "model": row["model"],
            "year": row["year"],
            "color": row["color"],
            "body_type": row["body_type"],
        },
    }), 200


def get_profile():
    customer_id = session["user"]

    user = run_query(
        "SELECT username, email, role, created_at FROM users WHERE user_id = %s",
        (customer_id,),
        fetch="one",
    )
    if not user:
        return jsonify({"message": "User not found."}), 404

    profile = run_query(
        "SELECT * FROM user_profile WHERE user_id = %s",
        (customer_id,),
        fetch="one",
    )
    customer = run_query(
        "SELECT * FROM customer_details WHERE user_id = %s",
        (customer_id,),
        fetch="one",
    )

    return jsonify({
        "user": {
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "created_at": user["created_at"],
        },
        "profile": profile,
        "customer_details": customer,
    }), 200


def update_profile():
    customer_id = session["user"]
    data = request.get_json()

    profile_fields = {}
    for key in ("full_name", "phone_number", "address", "city", "province", "zip_code"):
        if key in data:
            profile_fields[key] = data[key]

    customer_fields = {}
    for key in ("preferred_contact_method", "preferred_payment_method", "notes"):
        if key in data:
            customer_fields[key] = data[key]

    if profile_fields:
        set_clause = ", ".join(f"{k} = %s" for k in profile_fields)
        values = list(profile_fields.values()) + [customer_id]
        run_query(
            f"UPDATE user_profile SET {set_clause} WHERE user_id = %s",
            values,
        )

    if customer_fields:
        set_clause = ", ".join(f"{k} = %s" for k in customer_fields)
        values = list(customer_fields.values()) + [customer_id]
        run_query(
            f"UPDATE customer_details SET {set_clause} WHERE user_id = %s",
            values,
        )

    return jsonify({"message": "Profile updated successfully."}), 200


def get_vehicles():
    res = run_query(
        """SELECT vehicle_id, brand, model, year, color, body_type,
                  seating_capacity, transmission, fuel_type, price, status
           FROM vehicles
           WHERE status = 'available'
           ORDER BY brand, model""",
        fetch="all",
    )

    return jsonify(res), 200


def get_vehicle(vehicle_id):
    row = run_query(
        """SELECT vehicle_id, brand, model, year, color, body_type,
                  seating_capacity, transmission, fuel_type, price, status
           FROM vehicles
           WHERE vehicle_id = %s""",
        (vehicle_id,),
        fetch="one",
    )

    if not row:
        return jsonify({"message": "Vehicle not found."}), 404

    return jsonify(row), 200


def get_documents():
    customer_id = session["user"]

    res = run_query(
        """SELECT d.* FROM documents d
           JOIN sales s ON d.sale_id = s.sale_id
           WHERE s.customer_id = %s AND d.is_accessible = 1
           ORDER BY d.created_at DESC""",
        (customer_id,),
        fetch="all",
    )

    return jsonify(res), 200


def get_document(document_id):
    customer_id = session["user"]

    row = run_query(
        """SELECT d.* FROM documents d
           JOIN sales s ON d.sale_id = s.sale_id
           WHERE d.document_id = %s AND s.customer_id = %s AND d.is_accessible = 1""",
        (document_id, customer_id),
        fetch="one",
    )

    if not row:
        return jsonify({"message": "Document not found."}), 404

    return jsonify(row), 200


def mark_notification_read(notification_id):
    customer_id = session["user"]

    row = run_query(
        "SELECT notification_id FROM notifications WHERE notification_id = %s AND user_id = %s",
        (notification_id, customer_id),
        fetch="one",
    )
    if not row:
        return jsonify({"message": "Notification not found."}), 404

    run_query(
        "UPDATE notifications SET is_read = 1 WHERE notification_id = %s",
        (notification_id,),
    )

    return jsonify({"message": "Notification marked as read."}), 200
