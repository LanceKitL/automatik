"""
AutoMatik — Flask application entry point.

Loads environment variables, initialises extensions,
registers blueprints, and starts the SocketIO development server.
"""

# ── Environment ──────────────────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv()                            # Load .env before any other import

# ── Core imports ─────────────────────────────────────────────────────────
from flask import Flask, jsonify, render_template
from datetime import timedelta
from flask_cors import CORS
import os

<<<<<<< HEAD
#routes
from routes.admin import admin_bp
from routes.auth import auth_bp
from routes.vehicles import vehicles_bp
from routes.inquiries import inquiry_bp
from routes.supplier import supplier_bp
from routes.profile import profile_bp
from routes.notification import notif_bp
from routes.sales import sales_bp
=======
# ── Application modules ──────────────────────────────────────────────────
from validators.middleware import role_required, logged_in_required
from conn import run_query
from services.mail_service import init_mail
from config import MailConfig
from utils.socket_handler import socketio
>>>>>>> 7814b6bb5884f40f3aed5c4c24d32be40cc3482d

# ── Blueprints (route modules) ───────────────────────────────────────────
from routes.admin import admin_bp         # Admin user/agent/customer mgmt
from routes.auth import auth_bp           # Login, register, verify, forgot-pw
from routes.vehicles import vehicles_bp   # Vehicle inventory CRUD + photos
from routes.inquiries import inquiry_bp   # Customer inquiry lifecycle
from routes.supplier import supplier_bp   # Supplier CRUD
from routes.profile import profile_bp     # User profile (own)
from routes.notification import notif_bp  # In-app notifications
from routes.sales import sales_bp         # Sales, loans, payments, insurance

# ── App initialisation ───────────────────────────────────────────────────
app = Flask(__name__)

# ── CORS ─────────────────────────────────────────────────────────────────
# Allow the Vite dev-server origin (localhost:5173) to make credentialed requests.
CORS(app, supports_credentials=True, origins=["http://localhost:5173"])

# ── Session configuration ────────────────────────────────────────────────
app.config["SESSION_COOKIE_HTTPONLY"] = True          # Not accessible via JS
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"         # CSRF protection
debug = os.getenv("FLASK_DEBUG", "0") == "1"
app.config["SESSION_COOKIE_SECURE"] = os.getenv(
    "SESSION_COOKIE_SECURE",
    "0" if debug else "1"                             # Secure in production
) == "1"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
app.config["SESSION_REFRESH_EACH_REQUEST"] = True

# ── Secret key (required for session signing) ────────────────────────────
session_secret = os.getenv("SESSION_SECRET")
if not session_secret:
    raise RuntimeError("SESSION_SECRET is required.")
app.secret_key = session_secret

# ── Mail configuration ───────────────────────────────────────────────────
app.config.from_object(MailConfig)
init_mail(app)

# ── SocketIO ─────────────────────────────────────────────────────────────
socketio.init_app(app)

# ── Blueprint registration ───────────────────────────────────────────────
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(vehicles_bp, url_prefix="/vehicle")
app.register_blueprint(inquiry_bp, url_prefix="/inquiry")
app.register_blueprint(supplier_bp, url_prefix="/supplier")
app.register_blueprint(profile_bp, url_prefix="/profile")
app.register_blueprint(notif_bp, url_prefix="/notification")
<<<<<<< HEAD
app.register_blueprint(sales_bp)
=======
app.register_blueprint(sales_bp)           # no prefix — uses /admin/... and /sales/... internally
>>>>>>> 7814b6bb5884f40f3aed5c4c24d32be40cc3482d

# ── Error handlers ───────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(error):
    return render_template("error/404.html"), 404

@app.errorhandler(403)
def forbidden(error):
    return render_template("error/403.html"), 403

@app.errorhandler(500)
def server_error(error):
    return render_template("error/500.html"), 500

# ── Health & utility endpoints ───────────────────────────────────────────
@app.route("/health")
def index():
    return jsonify({
        "message": "Welcome to AUTOMATIK API!",
        "status": 200
    }), 200

@app.route("/logs")
@logged_in_required
@role_required("admin")
def indexLogs():
    res = run_query("SELECT * FROM audit_logs", fetch="all")
    return jsonify(res), 200

# ── Entry point ──────────────────────────────────────────────────────────
if __name__ == "__main__":
   socketio.run(app, host="0.0.0.0", debug=debug, allow_unsafe_werkzeug=debug)
