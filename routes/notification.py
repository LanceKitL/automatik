from flask import Blueprint, render_template
from validators.middleware import logged_in_required
from controllers.notificationController import getNotifications, markAsRead

notif_bp = Blueprint("notification", __name__)


@notif_bp.route("/test")
@logged_in_required
def index():
    return render_template("notification_test.html")


@notif_bp.route("/list", methods=["GET"])
@logged_in_required
def list_notifications():
    """Fetch all unread notifications for the current user."""
    return getNotifications()


@notif_bp.route("/read/<int:notif_id>", methods=["PUT"])
@logged_in_required
def read_notification(notif_id):
    """Mark a specific notification as read."""
    return markAsRead(notif_id)
