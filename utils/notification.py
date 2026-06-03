from flask_socketio import join_room, leave_room, emit, rooms
from flask import session
from datetime import datetime
from conn import run_query
from utils.socket_handler import socketio


def fire_notif(user_id, title, message, channel, ref_type, ref_id):
    created_at = datetime.now()
    res = run_query("""
                    INSERT INTO notifications
                    (user_id, title, message, channel, ref_type,
                     ref_id, created_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (user_id, title, message, channel, ref_type, ref_id, created_at))

    if not res:
        return False

    socketio.emit('notification', {
        'title': title,
        'message': message,
        'channel': channel,
        'created_at': created_at.isoformat()
    }, room=f"user_{user_id}")

    return True

def brodcast_notif(role, title, message, channel, ref_type, ref_id):
    res = run_query("SELECT * FROM users WHERE role = %s",(role,), fetch="all")
    created_at = datetime.now()
    if not res: # if a user with role admin exists
        return False
        # insert data to notifications
    for admin in res:
            run_query("""
                INSERT INTO notifications
                (user_id, title, message, channel, ref_type,
                    ref_id,created_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                """,
                (admin["user_id"], title, message, channel, ref_type, ref_id, created_at))
    
    socketio.emit('notification',{
        'title': title,
        'message': message,
        'channel': channel,
        'created_at': created_at
    }, room=f"role_{role}")
    
    return True

def read_notif(id):
    run_query("""
              UPDATE notifications
              SET is_read = %s
              WHERE notification_id = %s
              """,
              (1, id))

    return True


@socketio.on('connect')
def handle_connect():
    if "user" not in session or "role" not in session:
        return False

    join_room(f"user_{session['user']}")
    join_room(f"role_{session['role']}")

    print(f"Socket connected: user={session['user']} role={session['role']}")

    emit('connected', {
        'msg': f'Authenticated as {session["user"]} (role={session["role"]})'
    })


@socketio.on("disconnect")
def handle_disconnect():
    user_id = session.get("user")
    role = session.get("role")
    if user_id:
        leave_room(f"user_{user_id}")
    if role:
        leave_room(f"role_{role}")
    print("Socket disconnected")
