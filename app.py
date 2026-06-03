from dotenv import load_dotenv
load_dotenv()

from validators.middleware import role_required, logged_in_required
from conn import run_query

from flask import Flask, jsonify, render_template
from services.mail_service import init_mail
from datetime import timedelta
from flask_cors import CORS
from config import MailConfig
from utils.socket_handler import socketio
import os

#routes
from routes.admin import admin_bp
from routes.auth import auth_bp
from routes.vehicles import vehicles_bp
from routes.inquiries import inquiry_bp
from routes.supplier import supplier_bp
from routes.profile import profile_bp
from routes.notification import notif_bp
from routes.agent import agent_bp

app = Flask(__name__)

CORS(app, supports_credentials=True, origins=["http://localhost:5173"])
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
debug = os.getenv("FLASK_DEBUG", "0") == "1"
app.config["SESSION_COOKIE_SECURE"] = os.getenv(
    "SESSION_COOKIE_SECURE",
    "0" if debug else "1"
) == "1"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
app.config["SESSION_REFRESH_EACH_REQUEST"] = True
session_secret = os.getenv("SESSION_SECRET")
if not session_secret:
    raise RuntimeError("SESSION_SECRET is required.")

app.secret_key = session_secret

app.config.from_object(MailConfig)
init_mail(app)
socketio.init_app(app)

#routes
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(vehicles_bp, url_prefix="/vehicle")
app.register_blueprint(inquiry_bp, url_prefix="/inquiry")
app.register_blueprint(supplier_bp, url_prefix="/supplier")
app.register_blueprint(profile_bp, url_prefix="/profile")
app.register_blueprint(notif_bp, url_prefix="/notification")
app.register_blueprint(agent_bp)

#404 not found page
@app.errorhandler(404)
def not_found(error):
    return render_template("error/404.html"), 404

#403 unauthorized access
@app.errorhandler(403)
def forbidden(error):
    return render_template("error/403.html"), 403

#500 server error
@app.errorhandler(500)
def server_error(error):
    return render_template("error/500.html"), 500

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
    

if __name__ == "__main__":
   socketio.run(app, debug=True)