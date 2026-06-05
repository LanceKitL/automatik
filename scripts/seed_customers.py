"""
Seed mock customer data for customer portal testing.

Usage:
    DB_USER=kit DB_PASSWORD=kit DB_NAME=automatik python3 scripts/seed_customers.py

Inserts 4 customers (password: customer123) with profiles,
customer_details, inquiries, sales, and warranty claims.
Idempotent -- skips existing usernames/emails.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from werkzeug.security import generate_password_hash
from conn import run_query

PASSWORD = "customer123"
HASHED = generate_password_hash(PASSWORD)

CUSTOMERS = [
    {
        "username": "cust_juan",
        "email": "juan.luna@email.com",
        "full_name": "Juan Luna",
        "phone": "09171230001",
        "address": "42 P. Burgos St",
        "city": "Manila",
        "province": "Metro Manila",
        "zip": "1000",
        "customer_number": "CUST-2025-003",
        "preferred_contact": "email",
        "preferred_payment": "cash",
    },
    {
        "username": "cust_luisa",
        "email": "luisa.mercado@email.com",
        "full_name": "Luisa Mercado",
        "phone": "09181230002",
        "address": "88 Scout Rallos St",
        "city": "Quezon City",
        "province": "Metro Manila",
        "zip": "1103",
        "customer_number": "CUST-2025-004",
        "preferred_contact": "sms",
        "preferred_payment": "installment",
    },
    {
        "username": "cust_carlos",
        "email": "carlos.reyes@email.com",
        "full_name": "Carlos Reyes",
        "phone": "09191230003",
        "address": "15 F. Calderon St",
        "city": "Mandaluyong",
        "province": "Metro Manila",
        "zip": "1550",
        "customer_number": "CUST-2025-005",
        "preferred_contact": "email",
        "preferred_payment": "cash",
    },
    {
        "username": "cust_angela",
        "email": "angela.v@email.com",
        "full_name": "Angela Villanueva",
        "phone": "09201230004",
        "address": "7 Manga Ave",
        "city": "Pasig",
        "province": "Metro Manila",
        "zip": "1600",
        "customer_number": "CUST-2025-006",
        "preferred_contact": "whatsapp",
        "preferred_payment": "installment",
    },
]


def customer_exists(username, email):
    result = run_query(
        "SELECT user_id FROM users WHERE username = %s OR email = %s",
        (username, email),
        fetch="one",
    )
    return result is not None


def insert_customer(c):
    uid = run_query(
        """INSERT INTO users (username, hashed_password, email, role, email_verified, is_active)
           VALUES (%s, %s, %s, 'customer', 1, 1)""",
        (c["username"], HASHED, c["email"]),
    )
    run_query(
        """INSERT INTO user_profile (user_id, full_name, phone_number, address, city, province, zip_code)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (uid, c["full_name"], c["phone"], c["address"], c["city"], c["province"], c["zip"]),
    )
    run_query(
        """INSERT INTO customer_details (user_id, customer_number, preferred_contact_method, preferred_payment_method)
           VALUES (%s, %s, %s, %s)""",
        (uid, c["customer_number"], c["preferred_contact"], c["preferred_payment"]),
    )
    return uid


def seed():
    inserted = 0
    skipped = 0
    user_map = {}

    print("=== Inserting customer accounts ===")
    for c in CUSTOMERS:
        if customer_exists(c["username"], c["email"]):
            print(f"  SKIP {c['username']} -- already exists")
            skipped += 1
            row = run_query(
                "SELECT user_id FROM users WHERE username = %s", (c["username"],), fetch="one"
            )
            if row:
                user_map[c["username"]] = row["user_id"]
            continue
        uid = insert_customer(c)
        user_map[c["username"]] = uid
        inserted += 1
        print(f"  OK   {c['username']} (user_id={uid})")

    print("\n=== Inserting reference data ===")

    if "cust_juan" in user_map:
        uid = user_map["cust_juan"]
        exists = run_query(
            "SELECT inquiry_id FROM inquiries WHERE user_id = %s LIMIT 1", (uid,), fetch="one"
        )
        if not exists:
            run_query(
                """INSERT INTO inquiries (user_id, vehicle_id, message, status)
                   VALUES (%s, %s, %s, 'open')""",
                (
                    uid,
                    2,
                    "Good day! I am interested in the Vios XLE CVT for my daily commute. "
                    "Do you offer free LTO registration and comprehensive insurance? "
                    "Please advise on the best deal available.",
                ),
            )
            print(f"  INQ  Juan Luna -- inquiry about Vios XLE (vehicle_id=2)")

    if "cust_luisa" in user_map:
        uid = user_map["cust_luisa"]
        exists = run_query(
            "SELECT inquiry_id FROM inquiries WHERE user_id = %s LIMIT 1", (uid,), fetch="one"
        )
        if not exists:
            run_query(
                """INSERT INTO inquiries (user_id, vehicle_id, message, status)
                   VALUES (%s, %s, %s, 'open')""",
                (
                    uid,
                    5,
                    "Hi! I currently own a 2019 sedan and am looking to trade it in "
                    "for the Civic RS Turbo. Do you accept trade-ins? "
                    "What is the total cash-out needed?",
                ),
            )
            print(f"  INQ  Luisa Mercado -- inquiry about Civic RS (vehicle_id=5)")

    if "cust_carlos" in user_map:
        uid = user_map["cust_carlos"]
        sale_exists = run_query(
            "SELECT sale_id FROM sales WHERE customer_id = %s LIMIT 1", (uid,), fetch="one"
        )
        if not sale_exists:
            sale_id = run_query(
                """INSERT INTO sales (vehicle_id, customer_id, agent_id, selling_price, payment_type, status)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (1, uid, 2, 2390000.00, "installment", "active"),
            )
            print(f"  SALE Carlos Reyes -- Fortuner GR Sport PHP 2,390,000 (sale_id={sale_id})")

            claim_exists = run_query(
                "SELECT claim_id FROM warranty_claims WHERE sale_id = %s LIMIT 1",
                (sale_id,),
                fetch="one",
            )
            if not claim_exists:
                run_query(
                    """INSERT INTO warranty_claims (sale_id, vehicle_id, claim_type, description, status)
                       VALUES (%s, %s, 'repair', %s, 'submitted')""",
                    (
                        sale_id,
                        1,
                        "The engine check light has been intermittent since the second week "
                        "of ownership. Dealership inspection suggested a possible sensor issue. "
                        "Requesting warranty repair.",
                    ),
                )
                print(f"  WC   Carlos Reyes -- warranty claim on Fortuner GR (sale_id={sale_id})")

    print(f"\nDone. {inserted} customers inserted, {skipped} skipped.")


if __name__ == "__main__":
    seed()
