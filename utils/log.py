from flask import jsonify, request
from conn import run_query

def get_client_ip():
    return request.headers.get(
          "X-Forwarded-For",
          request.remote_addr
    ).split(",")[0].strip()

def audit_log(
        id, # -> current id ng nagbago ng field
        action, # -> ano yung ginawa ["PUT", "POST", "DELETE"]
        tablename, # -> anong table yung binago
        record_id=None, # -> yung id ng binago mo
        old_value=None, # -> yung old value. make sure import niyo yung "json" and using json.dump(value_here, default=str)
        new_value=None, # -> new value
        ip_address=None
    ):
        """SAMPLE USAGE IS PRESENT IN adminController"""

        query = """
            INSERT INTO audit_logs
            (
                user_id,
                action,
                table_name,
                record_id,
                old_value,
                new_value,
                ip_address
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        ip_address = get_client_ip()
        params = (
            id,
            action,
            tablename,
            record_id,
            old_value,
            new_value,
            ip_address
        )

        run_query(query, params)

        return True
        
        