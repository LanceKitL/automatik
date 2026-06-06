"""
Full payment flow test — Cash sale → Payment → Official Receipt.

This script connects directly to the MySQL database (same config as
conn.py), exercises the complete cash payment pipeline, and cleans up
test data afterwards.

Run:
    python tests/test_payment_flow.py

Requires:
    - MySQL running on localhost:3306
    - Database 'automatik' with seed data loaded
    - DB credentials from environment or defaults (root / no password)
"""

import os
import sys
import random
import string
from datetime import datetime

import mysql.connector
from mysql.connector import Error as DBError

# Allow running from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── DB config (mirrors conn.py) ──────────────────────────────
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "automatik"),
}

# ── Helpers ──────────────────────────────────────────────────


def get_connection():
    """Return a new MySQL connection with dictionary cursor factory."""
    conn = mysql.connector.connect(**DB_CONFIG)
    return conn


def run_query(query, params=None, fetch=None, conn=None, cursor=None):
    """
    Execute a SQL query with optional parameters and return results.

    Mirrors the behaviour of conn.run_query() but uses a plain
    mysql.connector connection (no pooling).

    Args:
        query (str): SQL string.
        params (tuple|None): Bound parameters.
        fetch (str|None): ``"one"``, ``"all"``, or ``None`` for
            INSERT rowcount/lastrowid.
        conn (connection|None): Re-use an existing connection.
        cursor (cursor|None): Re-use an existing cursor.

    Returns:
        dict | list[dict] | int | None
    """
    own_conn = conn is None
    own_cursor = cursor is None

    if own_conn:
        conn = get_connection()
    if own_cursor:
        cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(query, params)
        result = None

        if fetch == "one":
            result = cursor.fetchone()
        elif fetch == "all":
            result = cursor.fetchall()
        else:
            if own_conn:
                conn.commit()
            if query.strip().upper().startswith("INSERT"):
                result = cursor.lastrowid
            else:
                result = cursor.rowcount

        return result
    except DBError:
        if own_conn:
            conn.rollback()
        raise
    finally:
        if own_cursor:
            cursor.close()
        if own_conn:
            conn.close()


def random_temp_password(length=12):
    """Generate a random alphanumeric string."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


# ── Test data pickers ────────────────────────────────────────


def pick_available_vehicle(conn, cursor):
    """
    Find a vehicle with status 'available' to use for the test sale.

    Returns a dict with vehicle_id, brand, model, price.
    """
    vehicle = run_query(
        """SELECT vehicle_id, brand, model, price
           FROM vehicles
           WHERE status = 'available'
           ORDER BY RAND() LIMIT 1""",
        fetch="one",
        conn=conn,
        cursor=cursor,
    )
    if not vehicle:
        raise RuntimeError("No available vehicle found in DB. Seed data first.")
    return vehicle


def pick_agent(conn, cursor):
    """
    Pick a user with role 'agent' and an agent_details record.

    Returns a dict with user_id, username, email.
    """
    agent = run_query(
        """SELECT u.user_id, u.username, u.email
           FROM users u
           JOIN agent_details ad ON u.user_id = ad.user_id
           WHERE u.role = 'agent'
           ORDER BY RAND() LIMIT 1""",
        fetch="one",
        conn=conn,
        cursor=cursor,
    )
    if not agent:
        raise RuntimeError("No agent found in DB. Seed data first.")
    return agent


def pick_customer(conn, cursor):
    """
    Pick an existing customer (role='customer') from the DB.

    Returns a dict with user_id, username, email.
    """
    customer = run_query(
        """SELECT user_id, username, email
           FROM users
           WHERE role = 'customer'
           ORDER BY RAND() LIMIT 1""",
        fetch="one",
        conn=conn,
        cursor=cursor,
    )
    if not customer:
        raise RuntimeError("No customer found in DB. Seed data first.")
    return customer


# ── Main test flow ───────────────────────────────────────────


def test_cash_sale_payment_or_flow():
    """
    Full cash-payment flow: create a cash sale → record a payment
    → generate an Official Receipt document.

    Steps:
        1. Pick a random available vehicle, agent, customer from DB
        2. Check vehicle status (must be 'available')
        3. Create the sale (INSERT into sales table)
        4. Insert agent commission and draft contract
        5. Update vehicle status to 'delivered'
        6. Record a cash payment (INSERT into payments table)
        7. Create an Official Receipt (INSERT into documents table,
           document_type='OR')
        8. Verify every INSERT with SELECT queries
        9. Roll back / clean up all test data

    Returns:
        dict with sale_id, payment_id, document_id on success.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    created_ids = {}  # track what we inserted for cleanup

    try:
        # ── 1. PICK REFERENCE DATA ────────────────────────────
        vehicle = pick_available_vehicle(conn, cursor)
        agent = pick_agent(conn, cursor)
        customer = pick_customer(conn, cursor)

        selling_price = float(vehicle["price"])
        payment_type = "cash"
        print(f"Using vehicle:  {vehicle['brand']} {vehicle['model']} "
              f"(ID={vehicle['vehicle_id']}, PHP {selling_price:,.2f})")
        print(f"Using agent:    {agent['username']} (ID={agent['user_id']})")
        print(f"Using customer: {customer['username']} (ID={customer['user_id']})")

        # ── 2. VERIFY VEHICLE IS AVAILABLE ────────────────────
        v = run_query(
            "SELECT status FROM vehicles WHERE vehicle_id = %s FOR UPDATE",
            (vehicle["vehicle_id"],),
            fetch="one",
            conn=conn,
            cursor=cursor,
        )
        if v["status"] != "available":
            raise RuntimeError(
                f"Vehicle {vehicle['vehicle_id']} is '{v['status']}', "
                f"not 'available'."
            )

        # ── 3. CREATE THE SALE ────────────────────────────────
        cursor.execute(
            """INSERT INTO sales
               (vehicle_id, customer_id, agent_id, selling_price, payment_type, status)
               VALUES (%s, %s, %s, %s, %s, 'pending')""",
            (
                vehicle["vehicle_id"],
                customer["user_id"],
                agent["user_id"],
                selling_price,
                payment_type,
            ),
        )
        sale_id = cursor.lastrowid
        created_ids["sale_id"] = sale_id
        print(f"Sale created:   ID={sale_id}")

        # ── 4. VERIFY SALE ────────────────────────────────────
        sale = run_query(
            "SELECT * FROM sales WHERE sale_id = %s",
            (sale_id,),
            fetch="one",
            conn=conn,
            cursor=cursor,
        )
        assert sale is not None, "Sale was not inserted"
        assert sale["status"] == "pending", f"Expected 'pending', got '{sale['status']}'"
        assert sale["payment_type"] == "cash"
        assert float(sale["selling_price"]) == selling_price

        # ── 5. AGENT COMMISSION ───────────────────────────────
        agent_rate = run_query(
            "SELECT default_commission_rate FROM agent_details WHERE user_id = %s",
            (agent["user_id"],),
            fetch="one",
            conn=conn,
            cursor=cursor,
        )
        rate = float(agent_rate["default_commission_rate"]) if agent_rate else 3.5
        commission_amount = round(selling_price * rate / 100, 2)
        cursor.execute(
            """INSERT INTO agent_commissions
               (sale_id, agent_id, commission_amount, rate_applied)
               VALUES (%s, %s, %s, %s)""",
            (sale_id, agent["user_id"], commission_amount, rate),
        )
        commission_id = cursor.lastrowid
        created_ids["commission_id"] = commission_id

        # ── 6. DRAFT CONTRACT ─────────────────────────────────
        cursor.execute(
            "INSERT INTO sales_contracts (sale_id, status) VALUES (%s, 'draft')",
            (sale_id,),
        )
        contract_id = cursor.lastrowid
        created_ids["contract_id"] = contract_id

        # ── 7. MARK VEHICLE AS DELIVERED ──────────────────────
        cursor.execute(
            "UPDATE vehicles SET status = 'delivered' WHERE vehicle_id = %s",
            (vehicle["vehicle_id"],),
        )

        conn.commit()
        print("Sale transaction committed.")

        # ── 8. RECORD A CASH PAYMENT ──────────────────────────
        amount_paid = selling_price  # full payment for cash sale
        payment_method = "cash"

        cursor.execute(
            """INSERT INTO payments
               (sale_id, amount_paid, payment_method, payment_date, recorded_by)
               VALUES (%s, %s, %s, NOW(), %s)""",
            (sale_id, amount_paid, payment_method, agent["user_id"]),
        )
        payment_id = cursor.lastrowid
        created_ids["payment_id"] = payment_id
        conn.commit()
        print(f"Payment recorded: ID={payment_id} (PHP {amount_paid:,.2f}, cash)")

        # ── 9. VERIFY PAYMENT ─────────────────────────────────
        payment = run_query(
            """SELECT p.*, u.username AS recorded_by_name
               FROM payments p
               JOIN users u ON p.recorded_by = u.user_id
               WHERE p.payment_id = %s""",
            (payment_id,),
            fetch="one",
            conn=conn,
            cursor=cursor,
        )
        assert payment is not None, "Payment was not inserted"
        assert payment["payment_method"] == "cash"
        assert float(payment["amount_paid"]) == amount_paid
        assert payment["sale_id"] == sale_id
        print(f"Payment verified: method={payment['payment_method']}, "
              f"amount={float(payment['amount_paid']):,.2f}")

        # ── 10. GENERATE OFFICIAL RECEIPT (OR) ────────────────
        or_number = f"OR-{datetime.now().strftime('%Y%m%d')}-{payment_id:04d}"
        or_file_url = f"https://docs.automatik.ph/or/{or_number}.pdf"

        cursor.execute(
            """INSERT INTO documents
               (sale_id, document_type, file_url, is_accessible)
               VALUES (%s, 'OR', %s, 1)""",
            (sale_id, or_file_url),
        )
        document_id = cursor.lastrowid
        created_ids["document_id"] = document_id
        conn.commit()
        print(f"Official Receipt created: ID={document_id} ({or_file_url})")

        # ── 11. VERIFY OR DOCUMENT ────────────────────────────
        doc = run_query(
            """SELECT d.*, s.sale_id, v.brand, v.model
               FROM documents d
               JOIN sales s ON d.sale_id = s.sale_id
               JOIN vehicles v ON s.vehicle_id = v.vehicle_id
               WHERE d.document_id = %s""",
            (document_id,),
            fetch="one",
            conn=conn,
            cursor=cursor,
        )
        assert doc is not None, "OR document was not inserted"
        assert doc["document_type"] == "OR"
        assert doc["sale_id"] == sale_id
        assert doc["is_accessible"] == 1
        print(f"OR verified: type={doc['document_type']}, "
              f"file_url={doc['file_url']}")

        # ── 12. VERIFY TOTAL PAYMENTS FOR SALE ────────────────
        total_paid = run_query(
            "SELECT COALESCE(SUM(amount_paid), 0) AS total FROM payments WHERE sale_id = %s",
            (sale_id,),
            fetch="one",
            conn=conn,
            cursor=cursor,
        )
        total = float(total_paid["total"])
        print(f"Total payments for sale #{sale_id}: PHP {total:,.2f}")
        assert total == amount_paid, (
            f"Expected total {amount_paid:,.2f}, got {total:,.2f}"
        )

        print("\n✓ Full payment flow PASSED")
        return {
            "sale_id": sale_id,
            "payment_id": payment_id,
            "document_id": document_id,
            "or_number": or_number,
        }

    except DBError as e:
        conn.rollback()
        print(f"\n✗ Database error: {e}", file=sys.stderr)
        raise
    except AssertionError as e:
        print(f"\n✗ Assertion failed: {e}", file=sys.stderr)
        raise
    finally:
        cursor.close()
        conn.close()
        print("Connection closed.")


# ── Cleanup ──────────────────────────────────────────────────


def cleanup(ids):
    """
    Delete all rows created during the test.

    Temporarily disables FK checks so rows can be deleted in any order.
    Re-enables checks afterwards.

    Args:
        ids (dict): Keys are table identifiers, values are primary key
            values. Expected keys: document_id, payment_id, contract_id,
            commission_id, sale_id.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Disable FK checks for safe test-data cleanup
        cursor.execute("SET foreign_key_checks = 0")

        # Reverse-insertion order: child tables before parents
        tables = [
            ("documents", "document_id"),
            ("payments", "payment_id"),
            ("sales_contracts", "contract_id"),
            ("agent_commissions", "commission_id"),
            ("sales", "sale_id"),
        ]
        for table, pk_col in tables:
            val = ids.get(pk_col)
            if val is not None:
                cursor.execute(
                    f"DELETE FROM {table} WHERE {pk_col} = %s", (val,)
                )
                print(f"  Cleaned up {table}.{pk_col} = {val}")

        cursor.execute("SET foreign_key_checks = 1")
        conn.commit()
        print("Cleanup complete.")
    except DBError as e:
        conn.rollback()
        print(f"Cleanup error: {e}", file=sys.stderr)
    finally:
        cursor.close()
        conn.close()


# ── Entry point ──────────────────────────────────────────────


if __name__ == "__main__":
    print("=" * 60)
    print("Payment Flow Test (Cash Sale → Payment → OR)")
    print("=" * 60)
    ids = None
    try:
        ids = test_cash_sale_payment_or_flow()
    except Exception as e:
        print(f"\nTest FAILED: {e}")
        sys.exit(1)
    finally:
        if ids:
            print("\n--- Cleaning up test data ---")
            cleanup(ids)
        else:
            print("\nNo IDs to clean up.")
