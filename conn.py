from mysql.connector import pooling, Error
from flask import jsonify
# creating a connection
pool = pooling.MySQLConnectionPool(
        pool_name="mypool",
        pool_size=5,
        host="localhost",
        user="root",
        password="",
        database="automatik" # <- database name || you should match this with your database name
    )

def run_query(query, params=None, fetch=None):
    """
    Executes a given SQL query with optional parameters and fetches results based on the specified fetch type.
    Args:
        query (str): The SQL query to be executed.
        params (tuple, optional): Parameters to be passed to the SQL query. Defaults to None.
        fetch (str, optional): Determines the type of result to fetch. Can be "one", "all", or None. Defaults to None.
    Returns:
        The result of the query execution based on the specified fetch type. If fetch is "one", returns a single record; if "all", returns all records; otherwise, returns the number of affected rows or the last inserted ID for INSERT queries.
    Raises:
        Error: If an error occurs during the execution of the SQL query, the error is raised after rolling back any changes made to the database.
    """
    conn = pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(query, params)
        result = None
        
        if fetch == "one":
            result = cursor.fetchone()
        elif fetch == "all":
            result = cursor.fetchall()
        else:
            conn.commit()
            
            if query.strip().upper().startswith("INSERT"):
                result = cursor.lastrowid
            else:
                result = cursor.rowcount

        return result
    except Error as e:
        conn.rollback()
        raise e
    finally:        
        cursor.close()
        conn.close()