from datetime import datetime
from flask import jsonify, session
from conn import run_query
from services.socket_service import socketio

# notification_id
# user_id
# title
# message
# channel
# ref_type
# ref_id
# is_read
# created_at

def fire_notif(user_id: int, title: str, message: str, channel: str, ref_type: str, ref_id: int):
    created_at = datetime.now()
    res = run_query("""
                    INSERT INTO notifications
                    (user_id, title, message, channel, ref_type, 
                     ref_id, created_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (user_id, title, message, channel, ref_type, ref_id, created_at))
    
    if not res:
        return jsonify({"message": "notification fails to send."}), 400
    
    notif = run_query("""
                      SELECT title,message FROM notifications 
                      WHERE notification_id = %s
                      """,
                      (res,),
                      fetch="one")
    
    return jsonify({"data": notif})

def read_notif(id: int):
    res = run_query("""
                    UPDATE notifications
                    SET is_read = %s 
                    WHERE notification_id = %s
                    """,
                    (1, id))
    
    return jsonify({"action": "read notification."}), 200


def emit_notification(user_id: int, notification: dict):
    unread = run_query("""
        SELECT COUNT(*) AS total
        FROM notifications
        WHERE user_id = %s AND is_read = 0
    """, (user_id,), fetch="one")

    room = f"user_{user_id}"

    socketio.emit("notification:new", notification, room=room)
    socketio.emit("notification:unread_count", {
        "user_id": user_id,
        "unread_count": unread["total"] if unread else 0
    }, room=room)


def create_notification(user_id: int, title: str, message: str, channel: str = "in_app",
                        ref_type: str = None, ref_id: int = None):
    notification_id = run_query("""
        INSERT INTO notifications
        (user_id, title, message, channel, ref_type, ref_id, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        user_id,
        title,
        message,
        channel,
        ref_type,
        ref_id,
        datetime.now()
    ))

    notification = run_query("""
        SELECT
            notification_id,
            user_id,
            title,
            message,
            channel,
            ref_type,
            ref_id,
            is_read,
            created_at
        FROM notifications
        WHERE notification_id = %s
    """, (notification_id,), fetch="one")

    if notification:
        emit_notification(user_id, notification)

    return notification


def notify_sale_created(sale_id: int):
    sale = run_query("""
        SELECT
            s.sale_id,
            s.customer_id,
            s.vehicle_id,
            v.brand,
            v.model
        FROM sales s
        INNER JOIN vehicles v ON s.vehicle_id = v.vehicle_id
        WHERE s.sale_id = %s
    """, (sale_id,), fetch="one")

    if not sale:
        return None

    return create_notification(
        user_id=sale["customer_id"],
        title="Sale Created",
        message=f"Your sale for {sale['brand']} {sale['model']} has been created.",
        channel="in_app",
        ref_type="sales",
        ref_id=sale_id
    )


def notify_inquiry_assigned(inquiry_id: int):
    inquiry = run_query("""
        SELECT
            inquiry_id,
            agent_id,
            guest_name,
            user_id
        FROM inquiries
        WHERE inquiry_id = %s
    """, (inquiry_id,), fetch="one")

    if not inquiry or not inquiry.get("agent_id"):
        return None

    customer_name = inquiry.get("guest_name") or f"Customer #{inquiry.get('user_id')}"

    return create_notification(
        user_id=inquiry["agent_id"],
        title="Inquiry Assigned",
        message=f"A new inquiry from {customer_name} has been assigned to you.",
        channel="in_app",
        ref_type="inquiries",
        ref_id=inquiry_id
    )


def notify_amortization_due(schedule_id: int):
    schedule = run_query("""
        SELECT
            a.schedule_id,
            a.due_date,
            a.total_due,
            s.customer_id
        FROM amortization_schedule a
        INNER JOIN loan_details l ON a.loan_id = l.loan_id
        INNER JOIN sales s ON l.sale_id = s.sale_id
        WHERE a.schedule_id = %s
    """, (schedule_id,), fetch="one")

    if not schedule:
        return None

    return create_notification(
        user_id=schedule["customer_id"],
        title="Amortization Due",
        message=f"Your amortization payment of PHP {schedule['total_due']} is due on {schedule['due_date']}.",
        channel="in_app",
        ref_type="amortization_schedule",
        ref_id=schedule_id
    )


def notify_payment_recorded(payment_id: int):
    payment = run_query("""
        SELECT
            p.payment_id,
            p.amount_paid,
            p.sale_id,
            s.customer_id
        FROM payments p
        INNER JOIN sales s ON p.sale_id = s.sale_id
        WHERE p.payment_id = %s
    """, (payment_id,), fetch="one")

    if not payment:
        return None

    return create_notification(
        user_id=payment["customer_id"],
        title="Payment Recorded",
        message=f"Your payment of PHP {payment['amount_paid']} has been recorded.",
        channel="in_app",
        ref_type="payments",
        ref_id=payment_id
    )


def notify_warranty_approved(claim_id: int):
    claim = run_query("""
        SELECT
            w.claim_id,
            w.status,
            s.customer_id
        FROM warranty_claims w
        INNER JOIN sales s ON w.sale_id = s.sale_id
        WHERE w.claim_id = %s
    """, (claim_id,), fetch="one")

    if not claim or claim["status"] != "approved":
        return None

    return create_notification(
        user_id=claim["customer_id"],
        title="Warranty Approved",
        message="Your warranty claim has been approved.",
        channel="in_app",
        ref_type="warranty_claims",
        ref_id=claim_id
    )


def notify_booking_confirmed(booking_id: int):
    booking = run_query("""
        SELECT
            booking_id,
            customer_id,
            booking_type,
            status
        FROM service_bookings
        WHERE booking_id = %s
    """, (booking_id,), fetch="one")

    if not booking or booking["status"] != "confirmed":
        return None

    return create_notification(
        user_id=booking["customer_id"],
        title="Booking Confirmed",
        message=f"Your {booking['booking_type']} booking has been confirmed.",
        channel="in_app",
        ref_type="service_bookings",
        ref_id=booking_id
    )


def notify_commission_paid(commission_id: int):
    commission = run_query("""
        SELECT
            commission_id,
            agent_id,
            commission_amount,
            is_paid
        FROM agent_commissions
        WHERE commission_id = %s
    """, (commission_id,), fetch="one")

    if not commission or commission["is_paid"] != 1:
        return None

    return create_notification(
        user_id=commission["agent_id"],
        title="Commission Paid",
        message=f"Your commission of PHP {commission['commission_amount']} has been paid.",
        channel="in_app",
        ref_type="agent_commissions",
        ref_id=commission_id
    )