from conn import run_query
import socket

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def audit_log(
        id, # -> current id ng nagbago ng field
        action, # -> ano yung ginawa ["PUT", "POST", "DELETE"]
        tablename, # -> anong table yung binago
        record_id=None, # -> yung id ng binago mo
        old_value=None, # -> yung old value. make sure import niyo yung "json" and using json.dump(value_here, default=str)
        new_value=None, # -> new value
        ip_address=None,
        conn=None,
        cursor=None
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
        ip_address = get_local_ip()
        params = (
            id,
            action,
            tablename,
            record_id,
            old_value,
            new_value,
            ip_address
        )

        run_query(query, params, cursor=cursor,conn=conn)

        return True
        
        