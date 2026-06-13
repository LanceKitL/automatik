"""
Finance Staff controller — dashboard stats and loan/payment management.

Reuses existing loan/payment functions from salesController and paymentsController.
Matches FINANCING_INSURANCE.md KPI spec.
"""

from flask import jsonify
from conn import run_query


def getFinanceDashboard():
    """
    Return aggregated stats for the finance staff dashboard.
    Queries match the FINANCING_INSURANCE.md spec KPIs:
      - pending_reviews:   COUNT pending loan applications
      - approved_contracting: approved loans without amortization schedule
      - total_financed_portfolio: SUM of principal on approved loans
      - delinquency_rate:   (overdue >30d / total active accounts) x 100
      - total_collected:    SUM of payments received
      - recent_payments:    last 5 payments
    Returns:    JSON { data: { ... } }
    Status:     200
    """
    # 1. Pending Reviews
    pending_reviews = run_query(
        "SELECT COUNT(*) AS count FROM loan_details WHERE bank_approval_status = 'pending'",
        fetch="one",
    )

    # 2. Approved Contracting — approved loans missing any amortization schedule row
    approved_contracting = run_query(
        """SELECT COUNT(*) AS count FROM loan_details l
           LEFT JOIN amortization_schedule a ON l.loan_id = a.loan_id
           WHERE l.bank_approval_status = 'approved' AND a.schedule_id IS NULL""",
        fetch="one",
    )

    # 3. Total Financed Portfolio — sum of loan amounts for approved loans
    total_financed_portfolio = run_query(
        "SELECT COALESCE(SUM(loan_amount), 0) AS total FROM loan_details WHERE bank_approval_status = 'approved'",
        fetch="one",
    )

    # 4. Delinquency Rate — accounts with unpaid entries past 30 days
    total_active_accounts = run_query(
        "SELECT COUNT(DISTINCT loan_id) AS count FROM amortization_schedule WHERE status IN ('unpaid', 'paid')",
        fetch="one",
    )
    overdue_30d_accounts = run_query(
        """SELECT COUNT(DISTINCT loan_id) AS count FROM amortization_schedule
           WHERE status = 'unpaid' AND due_date < DATE_SUB(CURDATE(), INTERVAL 30 DAY)""",
        fetch="one",
    )
    total_active = total_active_accounts["count"] or 1
    delinquency_rate = round(
        (overdue_30d_accounts["count"] / total_active) * 100, 1
    )

    # 5. Total Collected
    total_collected = run_query(
        "SELECT COALESCE(SUM(amount_paid), 0) AS total FROM payments",
        fetch="one",
    )

    # 6. Recent Payments
    recent_payments = run_query(
        """SELECT p.payment_id, p.amount_paid, p.payment_method, p.payment_date,
                  s.sale_id, v.brand, v.model, u.username AS customer_name
           FROM payments p
           JOIN sales s ON p.sale_id = s.sale_id
           JOIN vehicles v ON s.vehicle_id = v.vehicle_id
           JOIN users u ON s.customer_id = u.user_id
           ORDER BY p.payment_date DESC LIMIT 5""",
        fetch="all",
    )

    return jsonify({
        "data": {
            "pending_reviews": pending_reviews["count"],
            "approved_contracting": approved_contracting["count"],
            "total_financed_portfolio": total_financed_portfolio["total"],
            "delinquency_rate": delinquency_rate,
            "total_collected": total_collected["total"],
            "recent_payments": recent_payments,
        }
    }), 200
