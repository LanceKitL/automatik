from flask import Flask, session, jsonify
from controllers.users import getAll, getById, addUser, updateUser, deleteUser
from functools import wraps

app = Flask(__name__)
app.secret_key = "super_secret_ultra_key"
    
# # INSERT -> CREATE
@app.route("/users/add", methods=["POST"])
def add_user():
    return addUser()

# READ
@app.route("/users")
def index():
    return getAll()

#SEARCH
# wildcards
@app.route("/users/<id>")
def getUser(id): # -> id
    return getById(id)

# # ID, FIELD -> na iuupdate (username, password, favorite_movie)
@app.route("/users/update/<id>", methods=["PUT"])
def update_user(id):
    return updateUser(id)

# # Delete
@app.route("/users/delete/<id>", methods=["DELETE"])
def deleteUser(id): # -> id
    return deleteUser(id)


@app.route("/session")
def asd():
    return jsonify({"session_data": session["data"]})

if __name__ == "__main__":
    app.run(debug=True)