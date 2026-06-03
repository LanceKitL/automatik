from flask import render_template
from flask_mail import Message, Mail
from conn import run_query


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

def welcome_user(email, template):
    msg = Message(
        sender=("AutoMatik", "AutoMatik@services.com"),
        subject="Email Verified Successfully!",
        recipients=[email]
    )
    
    msg.html = render_template(template, email=email)
    mail.send(msg)

def inquiry_received(email):
    msg = Message(
        sender=("AutoMatik", "AutoMatik@services.com"),
        subject="Hi there, we have received your Inquiry!",
        body="Thank you so much!",
        recipients=[email]
    )
    mail.send(msg)


def send_new_inquiry_notification(customer_id, inquiry_id, vehicle_name, message):
    staff = run_query(
        "SELECT email FROM users WHERE role IN ('admin','agent') AND is_active = 1",
        fetch="all",
    )
    if not staff:
        return

    subject = f"New Inquiry #{inquiry_id} from Customer #{customer_id}"
    html = render_template(
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
    html = render_template(
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