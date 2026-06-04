from flask import Blueprint
from validators.middleware import role_required, logged_in_required
from controllers.financingController import createLoan
from controllers.documentsController import uploadDocument

sales_bp = Blueprint('sales', __name__)

@sales_bp.route("/<int:sale_id>/loan", methods=["POST"])
@logged_in_required
@role_required("admin")
def create_sale_loan(sale_id):
    return createLoan(sale_id)

@sales_bp.route("/<int:sale_id>/documents", methods=["POST"])
@logged_in_required
@role_required("admin")
def upload_sale_document(sale_id):
    return uploadDocument(sale_id)
