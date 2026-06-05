"""
Generate PDF test guide for the Customer Portal API.

Usage:
    python3 scripts/generate_test_guide.py

Output: docs/customer_portal_test_guide.pdf
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fpdf import FPDF

ROUTES = [
    ("GET", "/portal/", "Customer dashboard with counts"),
    ("GET", "/portal/inquiries", "List customer's inquiries"),
    ("POST", "/portal/inquiries", "Create a new inquiry"),
    ("GET", "/portal/inquiries/{id}", "Get inquiry detail"),
    ("GET", "/portal/warranty-claims", "List customer's warranty claims"),
    ("POST", "/portal/warranty-claims", "Create a warranty claim"),
    ("GET", "/portal/warranty-claims/{id}", "Get claim detail"),
    ("GET", "/portal/sales", "List customer's sales"),
    ("GET", "/portal/sales/{id}", "Get sale detail"),
    ("GET", "/portal/profile", "Get customer profile"),
    ("PUT", "/portal/profile", "Update customer profile"),
    ("GET", "/portal/vehicles", "Browse available vehicles"),
    ("GET", "/portal/vehicles/{id}", "Get vehicle detail"),
    ("GET", "/portal/documents", "List vehicle documents"),
    ("GET", "/portal/documents/{id}", "Get document detail"),
    ("PUT", "/portal/notifications/{id}/read", "Mark notification as read"),
]


def build_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    # Title
    pdf.set_font("Helvetica", "B", 22)
    pdf.cell(0, 14, "AutoMatik", align="C", ln=1)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Customer Portal API - Test Guide", align="C", ln=1)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, "Base URL: http://localhost:5000/portal", align="C", ln=1)
    pdf.cell(0, 7, "Auth: Flask session cookie from POST /auth/login", align="C", ln=1)
    pdf.cell(0, 7, "Role required for all routes: customer", align="C", ln=1)
    pdf.cell(0, 7, "Test credentials: cust_juan / customer123", align="C", ln=1)
    pdf.ln(4)

    # Table of contents
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Table of Contents", ln=1)
    pdf.set_font("Helvetica", "", 10)
    for i, (method, url, desc) in enumerate(ROUTES, 1):
        pdf.cell(0, 5, f"  {i:2d}. {method:4s} {url}", ln=1)

    # Route detail pages
    for num, (method, url, desc) in enumerate(ROUTES, 1):
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, f"Route {num}: {method} {url}", ln=1)
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 6, desc, ln=1)
        pdf.ln(4)

        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, "Authentication & Authorization", ln=1)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 5, "  - Requires logged_in_required (valid Flask session)", ln=1)
        pdf.cell(0, 5, "  - Requires role_required('customer')", ln=1)
        pdf.cell(0, 5, "  - Non-customer roles (admin, agent) receive 403", ln=1)
        pdf.ln(2)

        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, "Error Cases", ln=1)
        pdf.set_font("Helvetica", "", 10)

        if method == "POST":
            if "inquiries" in url:
                pdf.cell(0, 5, "  - 400: missing vehicle_id or message", ln=1)
                pdf.cell(0, 5, "  - 422: message exceeds 1000 characters", ln=1)
            elif "warranty" in url:
                pdf.cell(0, 5, "  - 400: missing sale_id, vehicle_id, claim_type, or description", ln=1)
                pdf.cell(0, 5, "  - 422: invalid claim_type (must be repair/replacement/refund)", ln=1)
                pdf.cell(0, 5, "  - 422: description exceeds 2000 chars", ln=1)
                pdf.cell(0, 5, "  - 404: sale not found or does not belong to customer", ln=1)
        elif method == "PUT":
            if "profile" in url:
                pdf.cell(0, 5, "  - 200: returns success (profile updated)", ln=1)
            elif "read" in url:
                pdf.cell(0, 5, "  - 404: notification not found", ln=1)
        else:
            pdf.cell(0, 5, "  - 200: returns data (empty array if none)", ln=1)
            pdf.cell(0, 5, "  - 404: specific record not found (detail endpoints)", ln=1)

    # Appendix
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Appendix: Setup & Prerequisites", ln=1)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Session Authentication", ln=1)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, "  Before testing these routes, log in via POST /auth/login:", ln=1)
    pdf.set_font("Courier", "", 9)
    pdf.multi_cell(0, 4,
        '  curl -X POST http://localhost:5000/auth/login \\\n'
        '    -H "Content-Type: application/json" \\\n'
        '    -d \'{"username": "cust_juan", "password": "customer123"}\' \\\n'
        '    -c cookies.txt'
    )
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Use sessions cookie", ln=1)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, "  Append -b cookies.txt to subsequent curl requests.", ln=1)
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Verifying Side Effects", ln=1)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, "  Database: SELECT * FROM notifications WHERE user_id = ...", ln=1)
    pdf.cell(0, 5, "  SocketIO: Listen to 'notification' events on user_{id} / role_{role} rooms", ln=1)
    pdf.cell(0, 5, "  Email: Check Flask-Mail log / mailtrap.io if configured", ln=1)
    pdf.ln(4)

    # Test credentials
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Test Customer Credentials", ln=1)
    pdf.set_font("Courier", "", 9)
    creds = [
        ("cust_juan", "customer123", "Has inquiry about Vios XLE"),
        ("cust_luisa", "customer123", "Has inquiry about Civic RS"),
        ("cust_carlos", "customer123", "Has sale + warranty claim on Fortuner GR"),
        ("cust_angela", "customer123", "Fresh account, no inquiries or claims"),
    ]
    for u, p, n in creds:
        pdf.cell(0, 5, f"  {u:16s} / {p:16s}  {n}", ln=1)

    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "customer_portal_test_guide.pdf")
    pdf.output(out_path)
    print(f"PDF created: {out_path}")


if __name__ == "__main__":
    build_pdf()
