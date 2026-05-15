from validators.middleware import role_required, logged_in_required
from flask import Blueprint
from controllers.authController import (
    loginHandler,
    customerAccountHandler,
    AgentAccountHandler,
    logoutHandler,
    me,
    verifyEmail,
    changePassword
)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/me")
@logged_in_required
def get_me(): return me()

@auth_bp.route("/login", methods=["POST"])
def login(): return loginHandler()
    
@auth_bp.route("/customer/create", methods=["POST"])
@logged_in_required
@role_required("admin", "agent")
def create_customer(): return customerAccountHandler()

@auth_bp.route("/verify", methods=["PUT"])
def verify_email(): return verifyEmail()

@auth_bp.route('/register', methods=["POST"])
@logged_in_required
@role_required("admin") # -> only for admin because people are now allowed to create their own account, unless it's registered by the admin
def register(): return AgentAccountHandler()

@auth_bp.route("/change_password", methods=["PUT"])
@logged_in_required
def change_pw(): return changePassword()

@auth_bp.route("/logout", methods=["POST"])
@logged_in_required
def logout(): return logoutHandler()
