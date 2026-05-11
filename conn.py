import mysql.connector

# creating a connection
def connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="automatik"
    )
    
    
    
    #code       meaning         need to use
    #200        OK              GET,PUT,DELETE success
    #201        Created         POST success
    #400        BAD REQUEST     MISSING FIELDS IN BODY
    #404        NOT FOUND       NO DATA FOUND
    #500        SERVER ERROR    UNEXPECTED ERROR