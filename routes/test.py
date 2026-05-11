from flask import Blueprint, jsonify
test_bp = Blueprint("test", __name__)

@test_bp.route("/")
def test():
    return jsonify({"message": "This is a test route!"})
