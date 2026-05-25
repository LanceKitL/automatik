-> NOTIFICATIONS MODULE <-

- this module is for creating and managing user notifications.
- it also supports realtime notification using flask-socketio.
- make sure flask-socketio is installed from requirements.txt.

main files:
- routes/notifications.py
- utils/notification.py
- services/socket_service.py

available endpoints:
- GET /notifications
- GET /notifications/unread-count
- PUT /notifications/<id>/read
- PUT /notifications/read-all
- POST /notifications/admin/notifications
- DELETE /notifications/<id>

main helper:
create_notification(user_id, title, message, channel="in_app", ref_type=None, ref_id=None)

auto-trigger helpers:
- notify_sale_created(sale_id)
- notify_inquiry_assigned(inquiry_id)
- notify_amortization_due(schedule_id)
- notify_payment_recorded(payment_id)
- notify_warranty_approved(claim_id)
- notify_booking_confirmed(booking_id)
- notify_commission_paid(commission_id)

sample usage:
from utils.notification import notify_payment_recorded

notify_payment_recorded(payment_id)

that's it! notification module is ready.