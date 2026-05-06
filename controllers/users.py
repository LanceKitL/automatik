from conn import connection
from flask import jsonify, request, session

def getAll():
    conn = connection()
    conn.connect() # connecting to database
    cursor = conn.cursor(dictionary=True) # by default -> tuple
    cursor.execute("SELECT * FROM users")
    user = cursor.fetchall() # fetchone()
    session["data"] = user
    cursor.close()
    conn.close()
    return jsonify({"data": user}) # key: value-pair

def getById(id):
    conn = connection()
    conn.connect() # connecting to database
    cursor = conn.cursor(dictionary=True) # by default -> tuple
    cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
    user = cursor.fetchone() # fetchone()
    cursor.close()
    conn.close()
    return jsonify({"data": user}) # key: value-pair

def addUser():
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    favorite_movie = data["favorite_movie"]
    conn = connection()
    conn.connect() # connecting to database

    cursor = conn.cursor(dictionary=True) # by default -> tuple
    cursor.execute("INSERT INTO users (username,password,favorite_movie) VALUES (%s,%s,%s) ", (username,password, favorite_movie))
    
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "user added successfully!"}) # key: value-pair


def updateUser(id):
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    favorite_movie = data["favorite_movie"]
    conn = connection()
    conn.connect() # connecting to database
    cursor = conn.cursor(dictionary=True) # by default -> tuple
    
    cursor.execute("UPDATE users SET username=%s,password=%s,favorite_movie=%s WHERE id = %s", (username, password, favorite_movie, id))
    
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": f"user {id} updated successfully!"}) # 

def deleteUser(id):
    conn = connection()
    conn.connect() # connecting to database
    cursor = conn.cursor(dictionary=True) # by default -> tuple
    cursor.execute("DELETE FROM users WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"data": f"user {id} deleted succesfully"}) # key: value-pair\
