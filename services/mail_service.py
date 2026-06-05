from flask import render_template
from flask_mail import Message, Mail


mail = Mail()

def init_mail(app):
    mail.init_app(app)

def send_email_verification(user_email, name, verify_url):
    msg = Message(
        sender=("AutoMatik", "AutoMatik@services.com"),
        subject="Welcome to Automatik!",
        recipients=[user_email]
    )

    msg.html = render_template(
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

    msg.html = render_template(template, email=email, username=username, temp_password=temp_password, portal_url=portal_url)
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
    msg.html = render_template(
        'email/inquiry_assigned.html',
        name=name,
        agent_name=agent_name,
        inquiry_id=inquiry_id
    )
    mail.send(msg)

def send_sale_confirmation(email, name, sale_id, vehicle_name, total_amount):
    """Send sale confirmation receipt with vehicle and amount details."""
    msg = Message(
        sender=("AutoMatik", "AutoMatik@services.com"),
        subject="Sale Confirmed – Thank You!",
        recipients=[email]
    )
    msg.html = render_template(
        'email/sale_confirmation.html',
        name=name,
        sale_id=sale_id,
        vehicle_name=vehicle_name,
        total_amount=total_amount
    )
    mail.send(msg)

def send_payment_receipt(email, name, amount_paid, sale_id, payment_method):
    """Send payment receipt with amount, sale reference, and payment method."""
    msg = Message(
        sender=("AutoMatik", "AutoMatik@services.com"),
        subject="Payment Received – Receipt",
        recipients=[email]
    )
    msg.html = render_template(
        'email/payment_receipt.html',
        name=name,
        amount_paid=amount_paid,
        sale_id=sale_id,
        payment_method=payment_method
    )
    mail.send(msg)

def send_loan_status(email, name, loan_status, sale_id):
    """Notify customer whether their loan was approved or rejected."""
    msg = Message(
        sender=("AutoMatik", "AutoMatik@services.com"),
        subject=f"Loan {loan_status.title()} – AutoMatik",
        recipients=[email]
    )
    msg.html = render_template(
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
    msg.html = render_template(
        'email/warranty_approved.html',
        name=name,
        claim_id=claim_id,
        booking_link=booking_link
    )
    mail.send(msg)

def send_warranty_rejected(email, name, claim_id, resolution_notes):
    """Notify customer that warranty claim was rejected with resolution notes."""
    msg = Message(
        sender=("AutoMatik", "AutoMatik@services.com"),
        subject="Warranty Claim Update",
        recipients=[email]
    )
    msg.html = render_template(
        'email/warranty_rejected.html',
        name=name,
        claim_id=claim_id,
        resolution_notes=resolution_notes
    )
    mail.send(msg)

def send_booking_confirmed(email, name, booking_id, date_time, location):
    """Send booking confirmation with date/time/location details."""
    msg = Message(
        sender=("AutoMatik", "AutoMatik@services.com"),
        subject="Service Booking Confirmed",
        recipients=[email]
    )
    msg.html = render_template(
        'email/booking_confirmed.html',
        name=name,
        booking_id=booking_id,
        date_time=date_time,
        location=location
    )
    mail.send(msg)

def send_password_reset(email, reset_url):
    """Send password reset email with a one-time link (expires in 1 hour)."""
    msg = Message(
        sender=("AutoMatik", "AutoMatik@services.com"),
        subject="Reset Your Password",
        recipients=[email]
    )
    msg.html = render_template(
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