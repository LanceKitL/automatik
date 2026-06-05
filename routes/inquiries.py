"""
Inquiry routes — lifecycle of customer inquiries.

Public:  POST /inquiry/                  — submit a new inquiry
Admin:   GET  /inquiry/                  — list all inquiries
         PUT  /inquiry/assign/<id>       — assign to an agent
         PUT  /inquiry/close/<id>        — close an inquiry
Agent:   PUT  /inquiry/resolve/<id>      — mark resolved
Customer: GET /inquiry/my               — own inquiries
"""

from flask import Blueprint, request
from validators.middleware import role_required, logged_in_required
from controllers.inquiriesController import (
    submitInquiry,
    displayInquiries,
    indexCustomerInquiries,
    assignInquiry,
    resolveInquiry,
    closeInquiry
)

inquiry_bp = Blueprint('inquiry', __name__)

# ── Public ───────────────────────────────────────────────────────────────

@inquiry_bp.route("/", methods=["POST"])
def create():
    """Submit a new vehicle inquiry (guest or logged-in)."""
    return submitInquiry()

# ── Admin ────────────────────────────────────────────────────────────────

@inquiry_bp.route("/")
@logged_in_required
@role_required("admin", "agent")
def admin_index():
    """List all inquiries (admin/agent view)."""
    return displayInquiries()

@inquiry_bp.route("/assign/<int:inquiry_id>", methods=["PUT"])
@logged_in_required
@role_required("admin")
def assign_task(inquiry_id):
    """Assign an inquiry to an agent for follow-up."""
    return assignInquiry(inquiry_id)

@inquiry_bp.route("/close/<int:inquiry_id>", methods=["PUT"])
@logged_in_required
@role_required("admin")
def close_inquiry(inquiry_id):
    """Close a resolved or stale inquiry."""
    return closeInquiry(inquiry_id)

# ── Agent ────────────────────────────────────────────────────────────────

@inquiry_bp.route("/resolve/<int:inquiry_id>", methods=["PUT"])
@logged_in_required
@role_required("agent")
def resolve_task(inquiry_id):
    """Mark an inquiry as resolved (agent action)."""
    return resolveInquiry(inquiry_id)

# ── Customer ─────────────────────────────────────────────────────────────

@inquiry_bp.route("/my")
@logged_in_required
@role_required("customer", "admin")
def index_customer_inquiries():
    """List the current customer's own inquiries."""
    return indexCustomerInquiries()
