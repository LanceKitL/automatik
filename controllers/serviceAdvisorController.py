"""
Service Advisor controller — dashboard stats and booking self-assignment.

Reuses existing booking functions from serviceController.
"""

from flask import jsonify, session
from conn import run_query


def getServiceAdvisorDashboard():
    """
    Return aggregated stats for the service advisor dashboard.
    Queries: total pending bookings, unassigned bookings, my assigned count,
             total bookings today.
    Returns:    JSON { data: { pending_bookings, unassigned_bookings, my_assigned, today_bookings } }
    Status:     200
    """
    user_id = session["user"]

    pending_bookings = run_query(
        "SELECT COUNT(*) AS count FROM service_bookings WHERE status = 'pending'",
        fetch="one",
    )

    unassigned_bookings = run_query(
        "SELECT COUNT(*) AS count FROM service_bookings WHERE assigned_to IS NULL AND status IN ('pending', 'confirmed')",
        fetch="one",
    )

    my_assigned = run_query(
        "SELECT COUNT(*) AS count FROM service_bookings WHERE assigned_to = %s AND status IN ('pending', 'confirmed')",
        (user_id,),
        fetch="one",
    )

    today_bookings = run_query(
        """SELECT COUNT(*) AS count FROM service_bookings b
           JOIN service_slots s ON b.slot_id = s.slot_id
           WHERE DATE(s.slot_datetime) = CURDATE()""",
        fetch="one",
    )

    return jsonify({
        "data": {
            "pending_bookings": pending_bookings["count"],
            "unassigned_bookings": unassigned_bookings["count"],
            "my_assigned": my_assigned["count"],
            "today_bookings": today_bookings["count"],
        }
    }), 200
