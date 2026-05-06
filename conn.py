import mysql.connector

# creating a connection
def connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="tutorial"
    )