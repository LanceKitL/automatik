from flask import render_template, request
from flask_mail import Message, Mail
from conn import run_query


mail = Mail()

def _render(template, **ctx):
    try:
        base = request.url_root.rstrip('/')
    except RuntimeError:
        base = "http://localhost:5173"
    ctx.setdefault('logo_url', f"{base}/static/LOGO.png")
    return render_template(template, **ctx)

def init_mail(app):
    mail.init_app(app)

def send_email_verification(user_email, name, verify_url):
    msg = Message(
        sender=("AutoMatik", "AutoMatik@services.com"),
        subject="Welcome to Automatik!",
        recipients=[user_email]
    )

    msg.html = _render(
        'email/email_verification.html',
        name=name,
        verify_url=verify_url
    )

    mail.send(msg)

def welcome_user(email, template, username=None, temp_password=None, portal_url=None):
    subject = "Your AutoMatik Account is Ready!" if username else "Email Verified Successfully!"
    msg = Message(
        sender=("AutoMatik", "AutoMatik@services.com"),
        subject=subject,
        recipients=[email]
    )

    msg.html = _render(template, email=email, username=username, temp_password=temp_password, portal_url=portal_url)
    mail.send(msg)

def inquiry_received(email):
    """Send plain-text confirmation to a guest who submitted an inquiry."""
    msg = Message(
        sender=("AutoMatik", "AutoMatik@services.com"),
        subject="Hi there, we have received your Inquiry!",
        body="Thank you so much!",
        recipients=[email]
    )
    mail.send(msg)

def inquiry_assigned(email, name, agent_name, inquiry_id):
    """Notify the inquiry submitter that an agent has been assigned."""
    msg = Message(
        sender=("AutoMatik", "AutoMatik@services.com"),
        subject="Your Inquiry Has Been Assigned to an Agent",
        recipients=[email]
    )
    msg.html = _render(
        'email/inquiry_assigned.html',
        name=name,
        agent_name=agent_name,
        inquiry_id=inquiry_id
    )
    mail.send(msg)

def send_reservation_fee_notification(email, name, vehicle_name, amount):
    """Send reservation fee prompt with vehicle and amount details."""
    msg = Message(
        sender=("AutoMatik", "AutoMatik@services.com"),
        subject="Reservation Fee – Complete Your Reservation",
        recipients=[email]
    )
    msg.html = _render(
        'email/reservation_fee.html',
        name=name,
        vehicle_name=vehicle_name,
        amount=amount
    )
    mail.send(msg)

def send_sale_confirmation(email, name, sale_id, vehicle_name, total_amount):
    """Send sale confirmation receipt with vehicle and amount details."""
    msg = Message(
        sender=("AutoMatik", "AutoMatik@services.com"),
        subject="Sale Confirmed – Thank You!",
        recipients=[email]
    )
    msg.html = _render(
        'email/sale_confirmation.html',
        name=name,
        sale_id=sale_id,
        vehicle_name=vehicle_name,
        total_amount=total_amount
    )
    mail.send(msg)

def send_payment_receipt(email, name, amount_paid, sale_id, payment_method, allocation=None, reference=None, vehicle_name=None):
    """Send payment receipt with amount, sale reference, payment method, and vehicle info."""
    method_labels = {'cash': 'Cash', 'bank_transfer': 'Bank Transfer', 'check': 'Check', 'online': 'Online'}
    method_label = method_labels.get(payment_method, payment_method)
    msg = Message(
        sender=("AutoMatik", "AutoMatik@services.com"),
        subject=f"Payment Receipt — Sale #{sale_id}",
        recipients=[email]
    )
    msg.html = _render(
        'email/payment_receipt.html',
        name=name,
        amount_paid=amount_paid,
        sale_id=sale_id,
        payment_method=method_label,
        allocation=allocation,
        reference=reference,
        vehicle_name=vehicle_name
    )
    mail.send(msg)

def send_loan_status(email, name, loan_status, sale_id):
    """Notify customer whether their loan was approved or rejected."""
    msg = Message(
        sender=("AutoMatik", "AutoMatik@services.com"),
        subject=f"Loan {loan_status.title()} – AutoMatik",
        recipients=[email]
    )
    msg.html = _render(
        'email/loan_status.html',
        name=name,
        loan_status=loan_status,
        sale_id=sale_id
    )
    mail.send(msg)

def send_warranty_approved(email, name, claim_id, booking_link):
    """Notify customer that warranty claim is approved with a link to book service."""
    msg = Message(
        sender=("AutoMatik", "AutoMatik@services.com"),
        subject="Warranty Claim Approved – Book Your Service",
        recipients=[email]
    )
    msg.html = _render(
        'email/warranty_approved.html',
        name=name,
        claim_id=claim_id,
        booking_link=booking_link
    )
    mail.send(msg)

def send_warranty_rejected(email, name, claim_id, resolution_notes, booking_link=None):
    """Notify customer that warranty claim was rejected with resolution notes and repair booking link."""
    msg = Message(
        sender=("AutoMatik", "AutoMatik@services.com"),
        subject="Warranty Claim Update",
        recipients=[email]
    )
    msg.html = _render(
        'email/warranty_rejected.html',
        name=name,
        claim_id=claim_id,
        resolution_notes=resolution_notes,
        booking_link=booking_link
    )
    mail.send(msg)

def send_booking_confirmed(email, name, booking_id, date_time, location):
    """Send booking confirmation with date/time/location details."""
    msg = Message(
        sender=("AutoMatik", "AutoMatik@services.com"),
        subject="Service Booking Confirmed",
        recipients=[email]
    )
    msg.html = _render(
        'email/booking_confirmed.html',
        name=name,
        booking_id=booking_id,
        date_time=date_time,
        location=location
    )
    mail.send(msg)

def send_test_drive_confirmed(email, name, booking_id, date_time, location, vehicle_name):
    """Send test drive booking confirmation with policy details."""
    msg = Message(
        sender=("AutoMatik", "AutoMatik@services.com"),
        subject="Test Drive Booking Confirmed – AutoMatik",
        recipients=[email]
    )
    msg.html = _render(
        'email/test_drive_confirmed.html',
        name=name,
        booking_id=booking_id,
        date_time=date_time,
        location=location,
        vehicle_name=vehicle_name
    )
    mail.send(msg)

def send_password_reset(email, reset_url):
    """Send password reset email with a one-time link (expires in 1 hour)."""
    msg = Message(
        sender=("AutoMatik", "AutoMatik@services.com"),
        subject="Reset Your Password",
        recipients=[email]
    )
    msg.html = _render(
        'email/password_reset.html',
        reset_url=reset_url
    )
    mail.send(msg)

def send_password_reset_confirmation(email):
    """Send confirmation email after password has been successfully reset."""
    msg = Message(
        sender=("AutoMatik", "AutoMatik@services.com"),
        subject="Your Password Has Been Reset",
        recipients=[email]
    )
    msg.body = "Your password was successfully reset. If you did not do this, please contact support."
    mail.send(msg)

def send_custom_email(to_email, subject, body):
    """Send a plain-text email with an arbitrary subject and body."""
    msg = Message(
        sender=("AutoMatik", "AutoMatik@services.com"),
        subject=subject,
        recipients=[to_email]
    )
    msg.body = body
    mail.send(msg)

def send_new_inquiry_notification(customer_id, inquiry_id, vehicle_name, message):
    staff = run_query(
        "SELECT email FROM users WHERE role IN ('admin','agent') AND is_active = 1",
        fetch="all",
    )
    if not staff:
        return

    subject = f"New Inquiry #{inquiry_id} from Customer #{customer_id}"
    html = _render(
        "email/new_inquiry.html",
        customer_id=customer_id,
        vehicle_name=vehicle_name,
        message=message,
        inquiry_url=f"http://localhost:5000/inquiry/{inquiry_id}",
    )

    for s in staff:
        try:
            msg = Message(
                sender=("AutoMatik", "AutoMatik@services.com"),
                subject=subject,
                recipients=[s["email"]],
            )
            msg.html = html
            mail.send(msg)
        except Exception:
            pass


def send_warranty_claim_notification(customer_id, claim_id, claim_type, description, vehicle_name):
    staff = run_query(
        "SELECT email FROM users WHERE role IN ('admin','agent') AND is_active = 1",
        fetch="all",
    )
    if not staff:
        return

    subject = f"New Warranty Claim #{claim_id} from Customer #{customer_id}"
    html = _render(
        "email/new_warranty_claim.html",
        customer_id=customer_id,
        claim_type=claim_type,
        vehicle_name=vehicle_name,
        description=description,
        claim_url=f"http://localhost:5000/warranty-claims/{claim_id}",
    )

    for s in staff:
        try:
            msg = Message(
                sender=("AutoMatik", "AutoMatik@services.com"),
                subject=subject,
                recipients=[s["email"]],
            )
            msg.html = html
            mail.send(msg)
        except Exception:
            pass
