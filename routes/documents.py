from flask import Blueprint, session
from validators.middleware import role_required, logged_in_required
from controllers.documentsController import (
    getAllDocuments,
    getDocumentById,
    uploadDocument,
    updateDocument,
    deleteDocument,
    getMyDocuments,
    getMyDocumentById
)

documents_bp = Blueprint('documents', __name__)

# GET /documents/
@documents_bp.route("/")
@logged_in_required
@role_required("admin")
def get_all_documents(): return getAllDocuments()

# GET /documents/<document_id>
@documents_bp.route("/<int:document_id>")
@logged_in_required
@role_required("admin")
def get_document(document_id): return getDocumentById(document_id)

# POST /documents/sales/<sale_id>
@documents_bp.route("/sales/<int:sale_id>", methods=["POST"])
@logged_in_required
@role_required("admin")
def upload_document(sale_id): return uploadDocument(sale_id)

# PUT /documents/<document_id>
@documents_bp.route("/<int:document_id>", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update_document(document_id): return updateDocument(document_id)

# DELETE /documents/<document_id>
@documents_bp.route("/<int:document_id>", methods=["DELETE"])
@logged_in_required
@role_required("admin")
def delete_document(document_id): return deleteDocument(document_id)

# GET /documents/my - customer
@documents_bp.route("/my")
@logged_in_required
@role_required("customer")
def get_my_documents():
    customer_id = session["user"]
    return getMyDocuments(customer_id)

# GET /documents/my/<document_id> - customer
@documents_bp.route("/my/<int:document_id>")
@logged_in_required
@role_required("customer")
def get_my_document(document_id):
    customer_id = session["user"]
    return getMyDocumentById(document_id, customer_id)