from conn import connection
from flask import jsonify, request

#POST - UPLOAD OR GENERATE SALES 
def uploadContract(sale_id):
    data = request.get_json()
    document_type = data["document_type"]
    file_url = data["file_url"]
    is_accessible = data.get("is_accessible", 1)
 
    conn = connection()
    conn.connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "INSERT INTO documents (sale_id, document_type, file_url, is_accessible) VALUES (%s, %s, %s, %s)",
        (sale_id, document_type, file_url, is_accessible)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": f"Contract for sale {sale_id} uploaded successfully!"}), 201
 
#GET - DOCUMENTS
def getDocumentsBySale(sale_id):
    conn = connection()
    conn.connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM documents WHERE sale_id = %s", (sale_id,))
    documents = cursor.fetchall()
    cursor.close()
    conn.close()
    if not documents:
        return jsonify({"message": "No documents found!"}), 404
    return jsonify({"data": documents}), 200
 
# POST - UPLOAD DOCUMENT
def uploadDocument(sale_id):
    data = request.get_json()
    document_type = data["document_type"]
    file_url = data["file_url"]
    is_accessible = data.get("is_accessible", 1)
 
    conn = connection()
    conn.connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "INSERT INTO documents (sale_id, document_type, file_url, is_accessible) VALUES (%s, %s, %s, %s)",
        (sale_id, document_type, file_url, is_accessible)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": f"Document uploaded for sale {sale_id} successfully!"}),201