from flask import session
from flask_socketio import SocketIO, join_room, emit

# SocketIO instance used for realtime notification events.
socketio = SocketIO(
    cors_allowed_origins=[ "http://localhost:5173", "http://127.0.0.1:5173"],
    manage_session=False
)


def register_socket_events():
    @socketio.on("connect")
    def handle_connect():
        user_id = session.get("user")

        if user_id:
            room = f"user_{user_id}"
            join_room(room)

            emit("socket_connected", {
                "message": "Socket connected successfully.",
                "user_id": user_id,
                "room": room
            })
        else:
            emit("socket_connected", {
                "message": "Socket connected without logged-in session."
            })

    @socketio.on("join_user_room")
    def handle_join_user_room():
        user_id = session.get("user")

        if not user_id:
            emit("socket_error", {
                "message": "You are not logged in."
            })
            return

        room = f"user_{user_id}"
        join_room(room)

        emit("socket_joined", {
            "message": "Joined notification room successfully.",
            "user_id": user_id,
            "room": room
        })