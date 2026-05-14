from flask import Blueprint, jsonify, session
from conn import run_query
from validators.middleware import logged_in_required, role_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/stats", methods=["GET"])
@logged_in_required
@role_required("admin", "agent")
def get_dashboard_stats():
    total_users = run_query("SELECT COUNT(*) AS total FROM users",
        fetch="one"
    )

    total_vehicles = run_query(
        "SELECT COUNT(*) AS total FROM vehicles",
        fetch="one"
    )

    total_inquiries = run_query(
        "SELECT COUNT(*) AS total FROM inquiries",
        fetch="one"
    )

    open_inquiries = run_query(
        "SELECT COUNT(*) AS total FROM inquiries WHERE status = 'open'",
        fetch="one"
    )

    resolved_inquiries = run_query(
        "SELECT COUNT(*) AS total FROM inquiries WHERE resolved_at IS NOT NULL",
        fetch="one"
    )

    return jsonify({
        "message": "Dashboard statistics fetched successfully.",
        "data": {
            "total_users": total_users["total"],
            "total_vehicles": total_vehicles["total"],
            "total_inquiries": total_inquiries["total"],
            "open_inquiries": open_inquiries["total"],
            "resolved_inquiries": resolved_inquiries["total"]
        }
    }), 200


@dashboard_bp.route("/agent-task", methods=["GET"])
@logged_in_required
@role_required("agent", "admin")
def get_agent_task_summary():
    role = session["role"]
    user_id = session["user"]

    if role == "admin":
        result = run_query("""
            SELECT agent_id, COUNT(*) AS total_tasks, SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) 
            AS open_tasks, SUM(CASE WHEN resolved_at IS NOT NULL THEN 1 ELSE 0 END) AS resolved_tasks
            FROM inquiries WHERE agent_id IS NOT NULL GROUP BY agent_id """, fetch="all")
    else:
        result = run_query("""
            SELECT agent_id, COUNT(*) AS total_tasks, SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) AS open_tasks,
            SUM(CASE WHEN resolved_at IS NOT NULL THEN 1 ELSE 0 END) AS resolved_tasks
            FROM inquiries
            WHERE agent_id = %s
            GROUP BY agent_id """, (user_id,), fetch="all")

    return jsonify({
        "message": "Agent task summary fetched successfully.",
        "data": result
    }), 200