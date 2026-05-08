from flask import Flask, session, jsonify
from datetime import timedelta
from dotenv import load_dotenv
from functools import wraps
import os

load_dotenv()

#routes
from routes.admin import admin_bp
from routes.auth import auth_bp

app = Flask(__name__)

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = False
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
app.config["SESSION_REFRESH_EACH_REQUEST"] = True

app.secret_key = os.getenv("SESSION_SECRET")

app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(auth_bp, url_prefix="/auth")

@app.route("/")
def index():
    return jsonify({
        "message": "Welcome to AUTOMATIK API!",
        "status": 200
        }), 200


if __name__ == "__main__":
    app.run(debug=True)