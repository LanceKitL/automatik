from mysql.connector import pooling

# creating a connection
pool = pooling.MySQLConnectionPool(
        pool_name="mypool",
        pool_size=5,
        host="localhost",
        user="root",
        password="",
        database="automatik"
    )

def run_query(query, params=None, fetch=None):
    """
    The `run_query` function executes a SQL query, fetches results based on the specified fetch
    parameter, and returns the result.
    
    :param query: The `query` parameter is a SQL query string that you want to execute against the
    database. It can be a SELECT, INSERT, UPDATE, DELETE, or any other valid SQL statement
    :param params: The `params` parameter in the `run_query` function is used to pass any parameters
    that need to be bound to the SQL query. These parameters can be used to dynamically insert values
    into the query to prevent SQL injection attacks and to make the query more flexible and reusable
    :param fetch: The `fetch` parameter in the `run_query` function determines how the query results are
    fetched and returned. It can have the following values:
    :return: The function `run_query` returns the result of the query execution based on the value of
    the `fetch` parameter. If `fetch` is set to "one", it returns a single row from the query result. If
    `fetch` is set to "all", it returns all rows from the query result. If `fetch` is not specified or
    set to any other value, it returns the
    """
    conn = pool.get_connection()
    cursor = conn.cursor(dictionary=True)
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

        
    cursor.close()
    conn.close()
    return result