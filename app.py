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
from routes.servicebooking import services_bp

app = Flask(__name__)
CORS(app,supports_credentials=True, origins=["http://localhost:5173"])

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
app.config["SESSION_REFRESH_EACH_REQUEST"] = True

app.secret_key = os.getenv("SESSION_SECRET")

#routes
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(vehicles_bp, url_prefix="/vehicle")
app.register_blueprint(inquiry_bp, url_prefix="/inquiry")
app.register_blueprint(services_bp,url_prefix ="/service")

@app.route("/health")
def index():
    return jsonify({
        "message": "Welcome to AUTOMATIK API!",
        "status": 200
        }), 200


if __name__ == "__main__":
    app.run(debug=True)