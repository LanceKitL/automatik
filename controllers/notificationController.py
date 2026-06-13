from flask import session, jsonify
from conn import run_query
from utils.notification import read_notif

def getNotifications():
    """
    GET /notification/list
    Returns all unread notifications for the current user,
    ordered by most recent first.
    """
    user_id = session.get("user")
    if not user_id:
        return jsonify({"message": "Not authenticated"}), 403

    rows = run_query("""
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
        WHERE user_id = %s AND is_read = 0
        ORDER BY created_at DESC
    """, (user_id,), fetch="all")

    # Convert datetime objects to ISO strings for JSON serialization
    result = []
    for row in rows or []:
        result.append({
            "id": row["notification_id"],
            "title": row["title"],
            "message": row["message"],
            "channel": row["channel"],
            "ref_type": row["ref_type"],
            "ref_id": row["ref_id"],
            "is_read": bool(row["is_read"]),
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        })

    return jsonify(result), 200


def markAsRead(notif_id):
    """
    PUT /notification/read/<notif_id>
    Marks a single notification as read for the current user.
    """
    user_id = session.get("user")
    if not user_id:
        return jsonify({"message": "Not authenticated"}), 403

    # Verify the notification belongs to the current user
    notif = run_query("""
        SELECT notification_id FROM notifications
        WHERE notification_id = %s AND user_id = %s
    """, (notif_id, user_id), fetch="one")

    if not notif:
        return jsonify({"message": "Notification not found"}), 404

    read_notif(notif_id)

    return jsonify({"message": "Marked as read"}), 200


def getRecentNotifications():
    """Return the 6 most recent notifications for the current user (read + unread)."""
    user_id = session.get("user")
    if not user_id:
        return jsonify({"message": "Not authenticated"}), 403

    rows = run_query("""
        SELECT notification_id, title, message, channel, ref_type, ref_id, is_read, created_at
        FROM notifications
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 6
    """, (user_id,), fetch="all")

    result = []
    for row in rows or []:
        result.append({
            "id": row["notification_id"],
            "title": row["title"],
            "message": row["message"],
            "channel": row["channel"],
            "ref_type": row["ref_type"],
            "ref_id": row["ref_id"],
            "is_read": bool(row["is_read"]),
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        })

    return jsonify({"data": result}), 200


def getAllNotifications():
    """Return ALL notifications for the current user, newest first."""
    user_id = session.get("user")
    if not user_id:
        return jsonify({"message": "Not authenticated"}), 403

    rows = run_query("""
        SELECT notification_id, title, message, channel, ref_type, ref_id, is_read, created_at
        FROM notifications
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (user_id,), fetch="all")

    result = []
    for row in rows or []:
        result.append({
            "id": row["notification_id"],
            "title": row["title"],
            "message": row["message"],
            "channel": row["channel"],
            "ref_type": row["ref_type"],
            "ref_id": row["ref_id"],
            "is_read": bool(row["is_read"]),
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        })

    return jsonify({"data": result}), 200
