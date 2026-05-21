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

def welcome_user(email, template):
    msg = Message(
        sender=("AutoMatik", "AutoMatik@services.com"),
        subject="Email Verified Successfully!",
        recipients=[email]
    )
    
    msg.html = render_template(template, email=email)
    mail.send(msg)


