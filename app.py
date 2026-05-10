from flask import Flask, session, jsonify
from flask_cors import CORS
from datetime import timedelta
from dotenv import load_dotenv
import os

load_dotenv()

#routes
from routes.admin import admin_bp
from routes.auth import auth_bp

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:5173"])

app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = False
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=15)
app.config["SESSION_REFRESH_EACH_REQUEST"] = True

app.secret_key = os.getenv("SESSION_SECRET")

app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(auth_bp, url_prefix="/auth")

@app.route("/")
def index():
    return jsonify({
        "message": "Welcome to AUTOMATIK API!",
        "routes": {
            "auth": {
                    "/auth/login": {
                        "fields": ["username","email","password"],
                        "method": "POST"
                    },
                    "/auth/register": {
                        "fields": ["username", "email", "password", "confirmPassword"],
                        "method": "POST"
                    },
                    "/auth/logout": {
                        "fields": [],
                        "method": "POST"
                    },
                    "/auth/verify-email": {
                        "fields": ["email"],
                        "method": "POST"
                    },
                    "/auth/createCustomerAcc":{
                        "fields": ["email"],
                        "method": "POST"
                    },
                },
            
            "admin": {
                "/users": {
                    "fields": [],
                    "method": "GET"
                },
                "/users/<id>": {
                    "fields": [],
                    "method": "GET"
                }
            }
        }
        }), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
    