from flask import Blueprint,request, jsonify
from validators.middleware import role_required,logged_in_required
from controllers.inquiriesController import (
    submit_inquiry,
    get_inquiry_details,
    get_inquiries,
    update_inquiry
)

inquiry_bp = Blueprint('inquiry', __name__)

@inquiry_bp.route("/")
@role_required("admin","agent")
def home(): return get_inquiries()

@inquiry_bp.route("/<int:id>")
@role_required("admin","agent")
def show(id): return get_inquiry_details(id)

@inquiry_bp.route("/<int:id>/update", methods=["PUT"])
@role_required("admin", "agent")
def update(id): return update_inquiry(id)

@inquiry_bp.route("/create", methods=["POST"])
@role_required("admin","agent")
def create(): return submit_inquiry()