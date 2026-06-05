from conn import run_query
from flask import session, jsonify, request
from datetime import datetime
from utils.log import audit_log
from utils.notification import fire_notif, brodcast_notif
from services.mail_service import send_new_inquiry_notification, send_warranty_claim_notification
import json


def index():
    """Fetch dashboard data for the logged-in customer.

    Queries:
        - users table for customer username/email
        - sales table for active sales count
        - amortization_schedule (via loan_details, sales) for next unpaid payment due/amount
        - documents (via sales) for the 3 most recent documents
        - vehicles (via sales) for vehicles owned by the customer
        - inquiries table for open inquiries count
        - notifications table for unread in-app notification count

    Returns:
        tuple: (jsonify({"data": {...}}), 200) on success,
               (jsonify({"message": "Customer not found."}), 404) if user is missing.
    """
    customer_id = session["user"]

    user = run_query(
        "SELECT username, email FROM users WHERE user_id = %s",
        (customer_id,),
        fetch="one",
    )

    if not user:
        return jsonify({"message": "Customer not found."}), 404

    # Defaults
    next_payment_due = None
    next_payment_amount = None
    recent_documents = []
    my_vehicles = []

    sales = run_query(
        """
        SELECT *
        FROM sales
        WHERE customer_id = %s
        """,
        (customer_id,),
        fetch="all",
    ) or []

    active_sales_count = len(sales)

    if sales:
        # Get next unpaid amortization across all approved loans
        amortization = run_query(
            """
            SELECT
                a.total_due AS next_payment_amount,
                a.due_date AS next_payment_due
            FROM amortization_schedule a
            JOIN loan_details l
                ON a.loan_id = l.loan_id
            JOIN sales s
                ON l.sale_id = s.sale_id
            WHERE s.customer_id = %s
              AND l.bank_approval_status = 'approved'
              AND a.status = 'unpaid'
            ORDER BY a.due_date ASC
            LIMIT 1
            """,
            (customer_id,),
            fetch="one",
        )

        if amortization:
            next_payment_amount = amortization["next_payment_amount"]
            next_payment_due = amortization["next_payment_due"]

        # Recent documents
        recent_documents = run_query(
            """
            SELECT d.*
            FROM documents d
            JOIN sales s
                ON d.sale_id = s.sale_id
            WHERE s.customer_id = %s
            ORDER BY d.created_at DESC
            LIMIT 3
            """,
            (customer_id,),
            fetch="all",
        ) or []

        # My vehicles
        my_vehicles = run_query(
            """
            SELECT v.*
            FROM vehicles v
            JOIN sales s
                ON v.vehicle_id = s.vehicle_id
            WHERE s.customer_id = %s
            """,
            (customer_id,),
            fetch="all",
        ) or []

    inquiries = run_query(
        """
        SELECT *
        FROM inquiries
        WHERE user_id = %s
          AND status = 'open'
        """,
        (customer_id,),
        fetch="all",
    ) or []

    open_inquiries = len(inquiries)

    notifs = run_query(
        """
        SELECT *
        FROM notifications
        WHERE user_id = %s
          AND channel = 'in_app'
          AND is_read = 0
        """,
        (customer_id,),
        fetch="all",
    ) or []

    unread_notifs = len(notifs)

    return jsonify({
        "data": {
            "dashboard": {
                "active_sales": active_sales_count,
                "next_payment_due": next_payment_due,
                "next_payment_amount": next_payment_amount,
                "open_inquiries": open_inquiries,
                "unread_notification": unread_notifs,
                "recent_documents": recent_documents,
                "my_vehicles": my_vehicles
            },
            "notifications": notifs,
            "inquiries": inquiries,
            "sales": sales
        }
    }), 200

# vehicle routes taken from vehicle_controller

# SALES
def get_customer_sales():
    """Retrieve all sales/purchases for the logged-in customer.

    Queries:
        - sales table joined with vehicles to get sale details + vehicle info

    Returns:
        tuple: (jsonify(list of formatted sale dicts), 200).
    """
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
    """Retrieve a single sale/purchase by ID for the logged-in customer.

    Queries:
        - sales table joined with vehicles, filtered by sale_id and customer_id.

    Args:
        sale_id (int): The sale ID to look up.

    Returns:
        tuple: (jsonify(sale dict), 200) on success,
               (jsonify({"message": "Sale not found."}), 404) if not found or not owned.
    """
    customer_id = session["user"]

    row = run_query(
        """
        SELECT s.*, v.brand, v.model, v.year, v.color, v.body_type, v.price AS vehicle_price
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

# PAYMENTS & AMORTIZATION SCHED
def get_payment_history():
    """Retrieve payment history for the logged-in customer.

    Queries:
        - payments table joined with sales, filtered by customer_id.

    Returns:
        tuple: (jsonify({"data": [...]}), 200).
    """
    customer_id = session["user"]
    
    payment_history = run_query("""
                                SELECT p.* FROM payments p
                                JOIN sales s
                                ON p.sale_id = s.sale_id
                                WHERE s.customer_id = %s
                                """,
                                (customer_id,),
                                fetch="all")
    
    return jsonify({"data": payment_history}), 200        

def get_amortization_schedule():
    """Retrieve the full amortization schedule for all the customer's approved loans.

    Queries:
        - amortization_schedule joined with loan_details and sales, filtered by customer_id.

    Returns:
        tuple: (jsonify({"data": [...]}), 200).
    """
    customer_id = session["user"]
    
    amortization_schedule = run_query("""
                                        SELECT am.*
                                        FROM amortization_schedule am
                                        JOIN loan_details ld
                                            ON ld.loan_id = am.loan_id
                                        JOIN sales s
                                            ON s.sale_id = ld.sale_id
                                        WHERE s.customer_id = %s
                                      """,
                                      (customer_id,),
                                      fetch="all")
    
    return jsonify({"data": amortization_schedule})

# DOCUMENTS
def get_documents():
    """Retrieve all accessible documents for the logged-in customer.

    Queries:
        - documents table joined with sales, filtered by customer_id and is_accessible flag.

    Returns:
        tuple: (jsonify(list of document dicts), 200).
    """
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
    """Retrieve a single document by ID for the logged-in customer.

    Queries:
        - documents table joined with sales, filtered by document_id, customer_id, and is_accessible.

    Args:
        document_id (int): The document ID to look up.

    Returns:
        tuple: (jsonify(document dict), 200) on success,
               (jsonify({"message": "Document not found."}), 404) if not found or inaccessible.
    """
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

# INQUIRIES
def get_customer_inquiries():
    """Retrieve all inquiries made by the logged-in customer.

    Queries:
        - inquiries table joined with vehicles and agent_details, filtered by user_id.

    Returns:
        tuple: (jsonify(list of formatted inquiry dicts), 200).
    """
    customer_id = session["user"]

    res = run_query(
        """
           SELECT i.*,ad.*, v.brand, v.model, v.color, v.body_type, v.price
           FROM inquiries i
           JOIN vehicles v ON i.vehicle_id = v.vehicle_id
           JOIN agent_details ad ON i.agent_id = ad.user_id
           WHERE i.user_id = %s
           ORDER BY i.created_at DESC""",
        (customer_id,),
        fetch="all",
    )

    formatted = []
    for row in res:
        formatted.append({
            "inquiry_id": row["inquiry_id"],
            "agent_assigned": row["employee_number"],
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
    """Retrieve a single inquiry by ID for the logged-in customer.

    Queries:
        - inquiries table joined with vehicles and agent_details, filtered by inquiry_id and user_id.

    Args:
        inquiry_id (int): The inquiry ID to look up.

    Returns:
        tuple: (jsonify(inquiry dict), 200) on success,
               (jsonify({"message": "inquiry_id is required."}), 400) if no ID provided,
               (jsonify({"message": "Inquiry not found."}), 404) if not found.
    """
    customer_id = session["user"]
    
    if not inquiry_id:
        return jsonify({
            "message": "inquiry_id is required."
        }), 400
    
    row = run_query(
        """SELECT i.*, ad.employee_number, v.brand, v.model, v.color, v.body_type, v.price
           FROM inquiries i
           JOIN vehicles v ON i.vehicle_id = v.vehicle_id
           JOIN agent_details ad ON i.agent_id = ad.user_id
           WHERE i.inquiry_id = %s AND i.user_id = %s""",
        (inquiry_id, customer_id),
        fetch="one",
    )

    if not row:
        return jsonify({"message": "Inquiry not found."}), 404

    return jsonify({
        "inquiry_id": row["inquiry_id"],
        "agent_assigned": row["employee_number"],
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

# NOTIFICATIONS
def get_notifications():
    """Retrieve all notifications for the logged-in customer.

    Queries:
        - notifications table filtered by user_id, ordered by created_at DESC.

    Returns:
        tuple: (jsonify({"data": [...]}), 200).
    """
    customer_id = session["user"]

    notifs = run_query("""
                       SELECT * FROM notifications
                       WHERE user_id = %s
                       ORDER BY created_at DESC
                       """,
                       (customer_id,),
                       fetch="all")
    
    return jsonify({"data": notifs})    

def mark_notification_read(notification_id):
    """Mark a single notification as read for the logged-in customer.

    Queries:
        - SELECT on notifications to verify ownership and current read state.
        - UPDATE on notifications to set is_read = 1.

    Args:
        notification_id (int): The notification ID to mark as read.

    Returns:
        tuple: (jsonify({"message": "Notification marked as read."}), 200) on success,
               (jsonify({"message": "Notification not found."}), 404) if not found,
               (jsonify({"message": "notification marked as read already."}), 400) if already read.
    """
    customer_id = session["user"]

    row = run_query(
        "SELECT is_read, notification_id FROM notifications WHERE notification_id = %s AND user_id = %s",
        (notification_id, customer_id),
        fetch="one",
    )

    if not row:
        return jsonify({"message": "Notification not found."}), 404

    if row["is_read"] == 1:
        return jsonify({"message": "notification marked as read already."}),400

    run_query(
        "UPDATE notifications SET is_read = 1 WHERE notification_id = %s",
        (notification_id,),
    )

    return jsonify({"message": "Notification marked as read."}), 200

# USER PROFILE
def get_profile():
    """Retrieve the authenticated customer's full profile (account + profile + customer details).

    Queries:
        - users table with LEFT JOINs on user_profile and customer_details, filtered by user_id.

    Returns:
        tuple: (jsonify({"user": ..., "profile": ..., "customer_details": ...}), 200) on success,
               (jsonify({"message": "Unauthorized"}), 401) if no user in session,
               (jsonify({"message": "User not found."}), 404) if user record missing.
    """

    user_id = session.get("user")

    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401

    result = run_query(
        """
        SELECT
            -- users
            u.user_id,
            u.username,
            u.email,
            u.role,
            u.created_at,

            -- user_profile
            p.full_name,
            p.phone_number,
            p.address,
            p.city,
            p.province,
            p.zip_code,
            p.date_of_birth,
            p.gender,

            -- customer_details
            c.customer_number,
            c.preferred_contact_method,
            c.preferred_payment_method,
            c.notes

        FROM users u
        LEFT JOIN user_profile p
            ON p.user_id = u.user_id
        LEFT JOIN customer_details c
            ON c.user_id = u.user_id
        WHERE u.user_id = %s
        """,
        (user_id,),
        fetch="one",
    )

    if not result:
        return jsonify({"message": "User not found."}), 404

    response = {
        "user": {
            "user_id": result["user_id"],
            "username": result["username"],
            "email": result["email"],
            "role": result["role"],
            "created_at": result["created_at"],
        },
        "profile": {
            "full_name": result["full_name"],
            "phone_number": result["phone_number"],
            "address": result["address"],
            "city": result["city"],
            "province": result["province"],
            "zip_code": result["zip_code"],
            "date_of_birth": result["date_of_birth"],
            "gender": result["gender"],
        }
    }

    if result["role"] == "customer":
        response["customer_details"] = {
            "customer_number": result["customer_number"],
            "preferred_contact_method": result["preferred_contact_method"],
            "preferred_payment_method": result["preferred_payment_method"],
            "notes": result["notes"],
        }

    return jsonify(response), 200

# INSURANCE
def get_insurance():
    """Retrieve insurance records for the logged-in customer.

    Queries:
        - insurance_records table filtered by customer_id.

    Returns:
        tuple: (jsonify({"data": [...]}), 200).
    """
    customer_id = session["user"]
    
    insurance = run_query("""
                          SELECT * FROM insurance_records 
                          WHERE customer_id = %s; 
                          """,
                          (customer_id,),
                          fetch="all")

    return jsonify({"data": insurance}), 200
    
    
# WARRANTY CLAIMS
    
def get_customer_warranty_claims():
    """Retrieve all warranty claims submitted by the logged-in customer.

    Queries:
        - warranty_claims joined with sales and vehicles, filtered by customer_id.

    Returns:
        tuple: (jsonify(list of formatted claim dicts), 200).
    """
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
    """Retrieve a single warranty claim by ID for the logged-in customer.

    Queries:
        - warranty_claims joined with sales and vehicles,
          filtered by claim_id and customer_id.

    Args:
        claim_id (int): The warranty claim ID to look up.

    Returns:
        tuple: (jsonify(claim dict), 200) on success,
               (jsonify({"message": "Warranty claim not found."}), 404) if not found.
    """
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
    """Create a new warranty claim for the logged-in customer.

    Validates request JSON for required fields (sale_id, claim_type, description).
    Verifies the sale belongs to the authenticated customer.
    Inserts a new record into warranty_claims, then performs an audit log,
    sends in-app notifications (to customer, admins, and agents), and
    dispatches an email notification.

    Queries:
        - SELECT on sales (joined with vehicles) to verify ownership.
        - INSERT into warranty_claims.

    Returns:
        tuple: (jsonify({"message": "...", "claim_id": id}), 201) on success,
               (jsonify({"message": "Unauthorized"}), 401) if no user in session,
               (jsonify({"message": "..."}), 400/422) on validation errors,
               (jsonify({"message": "..."}), 404) if sale not found or not owned.
    """
    customer_id = session.get("user")

    if not customer_id:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}

    sale_id = data.get("sale_id")
    claim_type = data.get("claim_type")
    description = data.get("description")

    # -------------------------
    # VALIDATION
    # -------------------------
    if not sale_id:
        return jsonify({"message": "sale_id is required."}), 400

    if not claim_type:
        return jsonify({"message": "claim_type is required."}), 400

    if claim_type not in ("repair", "replacement", "refund"):
        return jsonify({
            "message": "claim_type must be repair, replacement, or refund."
        }), 422

    if not description:
        return jsonify({"message": "Description is required."}), 400

    if len(description) > 2000:
        return jsonify({"message": "Description must be 2000 characters or fewer."}), 422

    # -------------------------
    # VERIFY SALE BELONGS TO CUSTOMER
    # -------------------------
    sale = run_query(
        """
        SELECT
            s.sale_id,
            s.vehicle_id,
            v.brand,
            v.model
        FROM sales s
        JOIN vehicles v ON s.vehicle_id = v.vehicle_id
        WHERE s.sale_id = %s
        AND s.customer_id = %s
        """,
        (sale_id, customer_id),
        fetch="one",
    )

    if not sale:
        return jsonify({
            "message": "Sale not found or does not belong to you."
        }), 404

    vehicle_id = sale["vehicle_id"]

    # -------------------------
    # INSERT CLAIM
    # -------------------------
    claim_id = run_query(
        """
        INSERT INTO warranty_claims
        (sale_id, vehicle_id, claim_type, description, status)
        VALUES (%s, %s, %s, %s, 'submitted')
        """,
        (sale_id, vehicle_id, claim_type, description),
    )

    # -------------------------
    # AUDIT LOG
    # -------------------------
    audit_log(
        id=customer_id,
        action="POST",
        tablename="warranty_claims",
        record_id=claim_id,
    )

    # -------------------------
    # NOTIFICATIONS
    # -------------------------
    fire_notif(
        user_id=customer_id,
        title="Warranty Claim Submitted",
        message="Your warranty claim has been received and is under review.",
        channel="in_app",
        ref_type="warranty_claims",
        ref_id=claim_id,
    )

    broadcast_message = (
        f"Customer #{customer_id} submitted a {claim_type} claim for "
        f"{sale['brand']} {sale['model']}."
    )

    brodcast_notif(
        role="admin",
        title="New Warranty Claim",
        message=broadcast_message,
        channel="in_app",
        ref_type="warranty_claims",
        ref_id=claim_id,
    )

    brodcast_notif(
        role="agent",
        title="New Warranty Claim",
        message=broadcast_message,
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

    # -------------------------
    # RESPONSE
    # -------------------------
    return jsonify({
        "message": "Warranty claim submitted successfully.",
        "claim_id": claim_id,
    }), 201