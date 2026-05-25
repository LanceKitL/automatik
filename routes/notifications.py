from flask import Blueprint, jsonify, request, session
from conn import run_query
from validators.middleware import logged_in_required, role_required
from utils.notification import create_notification


notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.route("/", methods=["GET"])
@logged_in_required
def get_notifications():
    user_id = session.get("user")

    is_read = request.args.get("is_read")
    channel = request.args.get("channel")

    query = """
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
        WHERE user_id = %s
    """
    params = [user_id]

    if is_read is not None:
        query += " AND is_read = %s"
        params.append(is_read)

    if channel:
        query += " AND channel = %s"
        params.append(channel)

    query += " ORDER BY created_at DESC"

    notifications = run_query(query, tuple(params), fetch="all")

    return jsonify({
        "message": "Notifications fetched successfully.",
        "data": notifications
    }), 200


@notifications_bp.route("/unread-count", methods=["GET"])
@logged_in_required
def get_unread_count():
    user_id = session.get("user")

    result = run_query("""
        SELECT COUNT(*) AS total
        FROM notifications
        WHERE user_id = %s AND is_read = 0
    """, (user_id,), fetch="one")

    return jsonify({
        "message": "Unread notifications counted successfully.",
        "data": {
            "unread_count": result["total"] if result else 0
        }
    }), 200


@notifications_bp.route("/<int:notification_id>/read", methods=["PUT"])
@logged_in_required
def mark_notification_read(notification_id):
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


@notifications_bp.route("/read-all", methods=["PUT"])
@logged_in_required
def mark_all_notifications_read():
    user_id = session.get("user")

    run_query("""
        UPDATE notifications
        SET is_read = 1
        WHERE user_id = %s
    """, (user_id,))

    return jsonify({
        "message": "All notifications marked as read successfully."
    }), 200


@notifications_bp.route("/<int:notification_id>", methods=["DELETE"])
@logged_in_required
def delete_notification(notification_id):
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
        DELETE FROM notifications
        WHERE notification_id = %s AND user_id = %s
    """, (notification_id, user_id))

    return jsonify({
        "message": "Notification deleted successfully."
    }), 200


@notifications_bp.route("/admin/notifications", methods=["POST"])
@logged_in_required
@role_required("admin")
def create_admin_notification():
    data = request.get_json()

    title = data.get("title")
    message = data.get("message")
    channel = data.get("channel", "in_app")
    ref_type = data.get("ref_type")
    ref_id = data.get("ref_id")
    user_id = data.get("user_id")
    role = data.get("role")

    if not title or not message:
        return jsonify({
            "message": "title and message are required."
        }), 400

    if not user_id and not role:
        return jsonify({
            "message": "Either user_id or role is required."
        }), 400

    if user_id:
        inserted_id = run_query("""
            INSERT INTO notifications
            (user_id, title, message, channel, ref_type, ref_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, title, message, channel, ref_type, ref_id))

        return jsonify({
            "message": "Notification created successfully.",
            "data": {
                "notification_id": inserted_id
            }
        }), 201

    users = run_query("""
    SELECT user_id
    FROM users
    WHERE role = 'admin' AND is_active = 1
        """, fetch="all")

    if not users:
        return jsonify({
            "message": "No active users found for this role."
        }), 404

    created_ids = []

    for user in users:
        inserted_id = run_query("""
            INSERT INTO notifications
            (user_id, title, message, channel, ref_type, ref_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user["user_id"], title, message, channel, ref_type, ref_id))

        created_ids.append(inserted_id)

    return jsonify({
        "message": "Broadcast notification created successfully.",
        "data": {
            "created_count": len(created_ids),
            "notification_ids": created_ids
        }
    }), 201
    
    
@notifications_bp.route("/test", methods=["POST"])
@logged_in_required
def test_notification():
    user_id = session.get("user")
    data = request.get_json() or {}

    notification = create_notification(
        user_id=user_id,
        title=data.get("title", "Test Notification"),
        message=data.get("message", "This is a realtime test notification."),
        channel="in_app",
        ref_type="test",
        ref_id=None
    )

    return jsonify({
        "message": "Test notification created successfully.",
        "data": notification
    }), 201