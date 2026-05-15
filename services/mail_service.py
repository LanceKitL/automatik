from flask import render_template
from flask_mail import Message, Mail


mail = Mail()

def init_mail(app):
    mail.init_app(app)

def send_email_verification(user_email, name, verify_url):
    msg = Message(
        subject="Welcome to Automatik!",
        recipients=[user_email]
    )

    msg.html = render_template(
        'email/email_verification.html',
        name=name,
        verify_url=verify_url
    )

    mail.send(msg)

def send_verified(user_email, name):
    msg = Message(
        subject="Email Verified Successfully!",
        recipients=[user_email]
    )

    msg.html = render_template(
        'email/welcome.html',
        name=name
    )
    mail.send(msg)


