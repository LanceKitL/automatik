from flask import jsonify, request
from conn import run_query
from datetime import datetime
from werkzeug.utils import secure_filename
import os


UPLOAD_DIR = os.path.join("static", "uploads", "documents")


def uploadDocumentFile():
    if "file" not in request.files:
        return jsonify({"message": "No file provided."}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"message": "Empty filename."}), 400

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "bin"
    filename = f"{int(datetime.now().timestamp())}_{secure_filename(file.filename)}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    file.save(filepath)

    file_url = f"/static/uploads/documents/{filename}"
    return jsonify({"file_url": file_url}), 200


def getAllDocuments():
    data = request.args
    document_type = data.get("document_type")
    sale_id = data.get("sale_id")

    query = """
        SELECT documents.*
        FROM documents
        WHERE 1=1
    """
    params = []

    if document_type:
        query += " AND documents.document_type = %s"
        params.append(document_type)

    if sale_id:
        query += " AND documents.sale_id = %s"
        params.append(sale_id)

    documents = run_query(query, params if params else None, fetch="all")

    if not documents:
        return jsonify({"message": "No documents found!"}), 404

    return jsonify({"data": documents}), 200


def getDocumentById(document_id):
    document = run_query("""
        SELECT documents.*, sales.selling_price, sales.payment_type, sales.status
        FROM documents
        JOIN sales ON documents.sale_id = sales.sale_id
        WHERE documents.document_id = %s
    """, (document_id,), fetch="one")

    if not document:
        return jsonify({"message": "Document not found!"}), 404

    return jsonify({"data": document}), 200


def uploadDocument(sale_id):
    """
    [ADMIN] -> create a document and bind sale_id
    """
    _DOCUMENT_TYPES = ["OR","CR","warranty_cert","amortization_schedule","sales_contract","other"]

    data = request.get_json(silent=True) or {}
    document_type = data.get("document_type")
    file_url = data.get("file_url")
    is_accessible = data.get("is_accessible", 1)

    if not document_type or not file_url:
        return jsonify({"message": "document_type and file_url are required."}), 400

    if document_type not in _DOCUMENT_TYPES:
        return jsonify({
            "message": "document_type is invalid.",
            "valid_documents": _DOCUMENT_TYPES 
        }), 400
        
    # check if sale ID exist
    sale = run_query("""
                     SELECT sale_id from sales
                     WHERE sale_id = %s 
                     """,
                     (sale_id,),
                     fetch="one")
    
    if not sale:
        return jsonify({
            "message": "sale does not exists."
        }),404
    
    run_query("""
        INSERT INTO documents (sale_id, document_type, file_url, is_accessible) 
        VALUES (%s, %s, %s, %s)
    """, (sale_id, document_type, file_url, is_accessible))

    return jsonify({"message": "Document uploaded successfully!"}), 201


def updateDocument(document_id):
    data = request.get_json(silent=True) or {}
    file_url = data.get("file_url")
    is_accessible = data.get("is_accessible")

    if not file_url and is_accessible is None:
        return jsonify({"message": "file_url or is_accessible is required."}), 400

    run_query("""
        UPDATE documents SET file_url=%s, is_accessible=%s 
        WHERE document_id = %s
    """, (file_url, is_accessible, document_id))

    return jsonify({"message": "Document updated successfully!"}), 200


def deleteDocument(document_id):
    """
    [ADMIN] -> Delete specific document
    """
    if not document_id:
        return jsonify({
            "message": "document_id is empty"
        }), 400
    
    run_query("""
        DELETE FROM documents WHERE document_id = %s
    """, (document_id,))

    return jsonify({"message": "Document deleted successfully!"}), 200

