from flask import jsonify, request
from conn import run_query

def getAllDocuments():
    documents = run_query("""
        SELECT doc.*, s.selling_price, s.payment_type, s.status
        FROM documents doc
        JOIN sales s ON doc.sale_id = s.sale_id
    """, fetch="all")

    if not documents:
        return jsonify({"message": "No documents found!"}), 404

    return jsonify({"data": documents}), 200


def getDocumentById(document_id):
    document = run_query("""
        SELECT doc.*, s.selling_price, s.payment_type, s.status
        FROM documents doc
        JOIN sales s ON doc.sale_id = s.sale_id
        WHERE doc.document_id = %s
    """, (document_id,), fetch="one")

    if not document:
        return jsonify({"message": "Document not found!"}), 404

    return jsonify({"data": document}), 200


def uploadDocument(sale_id):
    data = request.get_json(silent=True) or {}
    document_type = data.get("document_type")
    file_url = data.get("file_url")
    is_accessible = data.get("is_accessible", 1)

    if not document_type or not file_url:
        return jsonify({"message": "document_type and file_url are required."}), 400

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
    run_query("""
        DELETE FROM documents WHERE document_id = %s
    """, (document_id,))

    return jsonify({"message": "Document deleted successfully!"}), 200


def getMyDocuments(customer_id):
    documents = run_query("""
        SELECT doc.*, s.selling_price, s.payment_type, s.status
        FROM documents doc
        JOIN sales s ON doc.sale_id = s.sale_id
        WHERE s.customer_id = %s AND doc.is_accessible = 1
    """, (customer_id,), fetch="all")

    if not documents:
        return jsonify({"message": "No documents found!"}), 404

    return jsonify({"data": documents}), 200


def getMyDocumentById(document_id, customer_id):
    document = run_query("""
        SELECT doc.document_id, doc.sale_id, doc.document_type, doc.file_url, doc.is_accessible, doc.created_at,
               s.selling_price, s.payment_type, s.status, s.sale_date
        FROM documents doc
        JOIN sales s ON doc.sale_id = s.sale_id
        WHERE doc.document_id = %s AND s.customer_id = %s AND doc.is_accessible = 1
    """, (document_id, customer_id), fetch="one")

    if not document:
        return jsonify({"message": "Document not found or not accessible!"}), 404

    return jsonify({"data": document}), 200