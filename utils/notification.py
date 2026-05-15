from datetime import datetime
from flask import jsonify, session
from conn import run_query

# notification_id
# user_id
# title
# message
# channel
# ref_type
# ref_id
# is_read
# created_at

def fire_notif(user_id: int, title: str, message: str, channel: str, ref_type: str, ref_id: int):
    created_at = datetime.now()
    res = run_query("""
                    INSERT INTO notifications
                    (user_id, title, message, channel, ref_type, 
                     ref_id, created_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (user_id, title, message, channel, ref_type, ref_id, created_at))
    
    if not res:
        return jsonify({"message": "notification fails to send."}), 400
    
    notif = run_query("""
                      SELECT title,message FROM notifications 
                      WHERE notification_id = %s
                      """,
                      (res,),
                      fetch="one")
    
    return jsonify({"data": notif})

def read_notif(id: int):
    res = run_query("""
                    UPDATE notifications
                    SET is_read = %s 
                    WHERE notification_id = %s
                    """,
                    (1, id))
    
    return jsonify({"action": "read notification."}), 200