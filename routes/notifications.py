from flask import Blueprint, jsonify, session
from conn import run_query
from validators.middleware import logged_in_required, role_required

notification_bp = Blueprint("notification", __name__)


@notification_bp.route("/notifications", methods=["GET"])
@logged_in_required
def get_user_notifications():
    user_id = session.get("user")

    notifications = run_query(
        """    SELECT notification_id, user_id, title, message, ref_type, ref_id, is_read, created_at
               FROM notifications
                WHERE user_id = %s
                ORDER BY created_at DESC
         """, (user_id,), fetch="all")

    return jsonify({
        "message": "Notifications fetched successfully.",
        "data": notifications
    }), 200


@notification_bp.route("/notification/<int:id>/read", methods=["PUT"])
@logged_in_required
@role_required("admin")
def mark_notification_as_read(id):
    existing_notification = run_query("""
        SELECT notification_id 
        FROM notifications 
        WHERE notification_id = %s
    """, (id,), fetch="one")

    if not existing_notification:
        return jsonify({
            "message": "Notification not found."
        }), 404

    run_query("""
        UPDATE notifications
        SET is_read = 1
        WHERE notification_id = %s
    """, (id,), commit=True)

    return jsonify({
        "message": "Notification marked as read successfully."
    }), 200