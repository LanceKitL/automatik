from validators.middleware import role_required, logged_in_required
from flask import Blueprint
from controllers.authController import (
    loginHandler,
    customerAccountHandler,
    AgentAccountHandler,
    logoutHandler
)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["POST"])
def login(): return loginHandler()
    
@auth_bp.route("/createCustomerAcc/<email>", methods=["POST"])
@logged_in_required
@role_required("admin", "agent")
def create_customer(email): return customerAccountHandler(email)

@auth_bp.route('/register', methods=["POST"])
def register(): return AgentAccountHandler()

@auth_bp.route("/logout", methods=["POST"])
@logged_in_required
def logout(): return logoutHandler()
