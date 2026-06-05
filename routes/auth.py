"""
Authentication routes — login, registration, email verification, password management.

Public endpoints: /seed, /login (GET+POST), /verify, /resendVerification,
/forgot-password, /reset-password.
Logged-in endpoints: /me, /customer/create, /registerAgent,
/changePassword, /logout.
"""

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
    resendVerification,
    forgotPassword,
    resetPassword
<<<<<<< HEAD
    
=======
>>>>>>> 7814b6bb5884f40f3aed5c4c24d32be40cc3482d
)

auth_bp = Blueprint('auth', __name__)

# ── Seed / bootstrap ─────────────────────────────────────────────────────

@auth_bp.route("/seed")
def seed():
    """Create the default admin account (admin / admin123)."""
    return seedAdmin()

# ── Session ──────────────────────────────────────────────────────────────

@auth_bp.route("/me")
@logged_in_required
def get_me():
    """Return the currently logged-in user's info."""
    return me()

# ── Login ────────────────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["GET"])
def login_page():
    """Render the login page (temporary, for testing)."""
    return render_template("login.html")

@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate with username/email + password, start a session."""
    return loginHandler()

# ── Customer account creation (admin/agent only) ─────────────────────────

@auth_bp.route("/customer/create", methods=["POST"])
@logged_in_required
@role_required("admin", "agent")
def create_customer():
    """Create a customer account manually (with temp password)."""
    return customerAccountHandler()

# ── Email verification ───────────────────────────────────────────────────

@auth_bp.route("/verify", methods=["GET"])
def verify_email():
    """Verify email via token_id & raw_token query parameters."""
    return verifyEmail()

@auth_bp.route("/resendVerification")
def resend():
    """Resend the verification email (?email=...)."""
    email = request.args.get("email")
    return resendVerification(email)

# ── Agent registration (admin only) ──────────────────────────────────────

@auth_bp.route('/registerAgent', methods=["POST"])
@logged_in_required
@role_required("admin")
def register():
    """Create a new agent account; sends email-verification link."""
    return AgentAccountHandler()

# ── Password management ──────────────────────────────────────────────────

@auth_bp.route("/changePassword", methods=["PUT"])
@logged_in_required
def change_pw():
    """Change the current user's password (requires old_password)."""
    return changePassword()

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot():
    """Send a password-reset link to the given email."""
    return forgotPassword()

@auth_bp.route("/reset-password", methods=["POST"])
def reset():
    """Reset password using a valid token_id + raw_token."""
    return resetPassword()

# ── Logout ───────────────────────────────────────────────────────────────

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot(): return forgotPassword()

@auth_bp.route("/reset-password", methods=["POST"])
def reset(): return resetPassword()

@auth_bp.route("/logout", methods=["POST"])
@logged_in_required
def logout():
    """Clear the session and mark user as inactive."""
    return logoutHandler()
