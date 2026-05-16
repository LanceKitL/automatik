from flask import Flask, jsonify
from datetime import timedelta
from dotenv import load_dotenv
from flask_cors import CORS
import os

load_dotenv()

#routes
from routes.admin import admin_bp
from routes.auth import auth_bp
from routes.vehicles import vehicles_bp
from routes.inquiries import inquiry_bp
from routes.supplier import supplier_bp
from routes.profile import profile_bp
from routes.financing import financing_bp
from routes.documents import documents_bp

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

#routes
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(vehicles_bp, url_prefix="/vehicle")
app.register_blueprint(inquiry_bp, url_prefix="/inquiry")
app.register_blueprint(supplier_bp, url_prefix="/supplier")
app.register_blueprint(profile_bp, url_prefix="/profile")
app.register_blueprint(financing_bp, url_prefix="/admin/loans")
app.register_blueprint(documents_bp, url_prefix="/admin/documents")

@app.route("/health")
def index():
    return jsonify({
        "message": "Welcome to AUTOMATIK API!",
        "status": 200
        }), 200

if __name__ == "__main__":
    app.run(debug=debug, host="0.0.0.0")