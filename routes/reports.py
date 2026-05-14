from flask import Blueprint, jsonify, request
from conn import run_query
from validators.middleware import logged_in_required, role_required

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/sales", methods=["GET"])
@logged_in_required
@role_required("admin")
def get_sales_report():
    period = request.args.get("period")
    agent_id = request.args.get("agent_id")

    query = """ SELECT i.inquiry_id, i.agent_id, i.vehicle_id, i.guest_name, i.guest_email, 
                i.status, i.created_at, i.resolved_at, v.brand, v.model, v.price
                FROM inquiries i LEFT JOIN vehicles v ON i.vehicle_id = v.vehicle_id 
                WHERE i.resolved_at IS NOT NULL 
            """
    params = []

    if agent_id:
        query += " AND i.agent_id = %s"
        params.append(agent_id)

    if period == "daily":
        query += " AND DATE(i.resolved_at) = CURDATE()"
    elif period == "weekly":
        query += " AND YEARWEEK(i.resolved_at, 1) = YEARWEEK(CURDATE(), 1)"
    elif period == "monthly":
        query += " AND MONTH(i.resolved_at) = MONTH(CURDATE()) AND YEAR(i.resolved_at) = YEAR(CURDATE())"

    query += " ORDER BY i.resolved_at DESC"
    result = run_query(query, tuple(params), fetch="all")
    total_sales = sum(item["price"] or 0 for item in result)

    return jsonify({
        "message": "Sales report fetched successfully.",
        "filters": { 
            "period": period, 
            "agent_id": agent_id
        },
        "summary": {
            "total_records": len(result),
            "total_sales": total_sales
        },
        "data": result
    }), 200