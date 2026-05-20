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
portal_bp = Blueprint('portal', __name__)

# GET /admin/documents
@documents_bp.route("/")
@logged_in_required
@role_required("admin")
def get_all_documents(): return getAllDocuments()

# GET /admin/documents/<document_id>
@documents_bp.route("/<int:document_id>")
@logged_in_required
@role_required("admin")
def get_document(document_id): return getDocumentById(document_id)

# POST /admin/documents/sales/<sale_id>
@documents_bp.route("/sales/<int:sale_id>", methods=["POST"])
@logged_in_required
@role_required("admin")
def upload_document(sale_id): return uploadDocument(sale_id)

# PUT /admin/documents/<document_id>
@documents_bp.route("/<int:document_id>", methods=["PUT"])
@logged_in_required
@role_required("admin")
def update_document(document_id): return updateDocument(document_id)

# DELETE /admin/documents/<document_id>
@documents_bp.route("/<int:document_id>", methods=["DELETE"])
@logged_in_required
@role_required("admin")
def delete_document(document_id): return deleteDocument(document_id)

# GET /portal/documents
@portal_bp.route("/documents")
@logged_in_required
@role_required("customer")
def get_my_documents():
    customer_id = session["user"]
    return getMyDocuments(customer_id)

# GET /portal/documents/<document_id>
@portal_bp.route("/documents/<int:document_id>")
@logged_in_required
@role_required("customer")
def get_my_document(document_id):
    customer_id = session["user"]
    return getMyDocumentById(document_id, customer_id)