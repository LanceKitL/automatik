from validators.middleware import role_required, logged_in_required
from flask import Blueprint, render_template, request
from controllers.authController import (
    loginHandler,
    customerAccountHandler,
    AgentAccountHandler,
    logoutHandler,
    me,
    verifyEmail,
    changePassword,
    seedAdmin,
    resendVerification
    
)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/seed")
def seed():
    # add admin users
    return seedAdmin()

@auth_bp.route("/me")
@logged_in_required
def get_me(): return me()

# TEMPORARY: Remove this GET route and templates/login.html after testing
@auth_bp.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

@auth_bp.route("/login", methods=["POST"])
def login(): return loginHandler()
    
@auth_bp.route("/customer/create", methods=["POST"])
@logged_in_required
@role_required("admin", "agent")
def create_customer(): return customerAccountHandler()

@auth_bp.route("/verify", methods=["GET"])
def verify_email(): return verifyEmail()

@auth_bp.route("/resendVerification")
def resend():
    # Get email from query parameter (e.g. ?email=user@example.com)
    email = request.args.get("email")
    return resendVerification(email)
    
@auth_bp.route('/registerAgent', methods=["POST"])
@logged_in_required
@role_required("admin") # -> only for admin because people are now allowed to create their own account, unless it's registered by the admin
def register(): return AgentAccountHandler()

@auth_bp.route("/changePassword", methods=["PUT"])
@logged_in_required
def change_pw(): return changePassword()

@auth_bp.route("/logout", methods=["POST"])
@logged_in_required
def logout(): return logoutHandler()
