from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ISSUES_FILE = PROJECT_ROOT / "issues.txt"
MARKER = f"notif-test-{datetime.now().strftime('%Y%m%d%H%M%S')}"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import app
from conn import run_query


class TestFailure(Exception):
    pass


def set_session(client, user_id: int, role: str) -> None:
    with client.session_transaction() as sess:
        sess["user"] = user_id
        sess["role"] = role


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise TestFailure(message)


def pick_user_for_role(role: str) -> dict[str, Any] | None:
    return run_query(
        """
        SELECT user_id, role
        FROM users
        WHERE role = %s
        ORDER BY user_id ASC
        LIMIT 1
        """,
        (role,),
        fetch="one",
    )


def pick_any_user(exclude_user_id: int | None = None) -> dict[str, Any] | None:
    if exclude_user_id is None:
        return run_query(
            """
            SELECT user_id, role
            FROM users
            ORDER BY user_id ASC
            LIMIT 1
            """,
            fetch="one",
        )

    return run_query(
        """
        SELECT user_id, role
        FROM users
        WHERE user_id <> %s
        ORDER BY user_id ASC
        LIMIT 1
        """,
        (exclude_user_id,),
        fetch="one",
    )


def pick_role_for_broadcast() -> str | None:
    row = run_query(
        """
        SELECT role
        FROM users
        GROUP BY role
        ORDER BY COUNT(*) DESC
        LIMIT 1
        """,
        fetch="one",
    )
    return str(row["role"]) if row else None


def insert_notification(user_id: int, title: str, message: str, is_read: int = 0) -> int:
    return run_query(
        """
        INSERT INTO notifications
        (user_id, title, message, channel, ref_type, ref_id, is_read, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            user_id,
            title,
            message,
            "in_app",
            "test",
            None,
            is_read,
            datetime.now(),
        ),
    )


def count_unread(user_id: int) -> int:
    result = run_query(
        """
        SELECT COUNT(*) AS total
        FROM notifications
        WHERE user_id = %s AND is_read = 0
        """,
        (user_id,),
        fetch="one",
    )
    return int(result["total"]) if result else 0


def cleanup_test_rows() -> None:
    run_query(
        """
        DELETE FROM notifications
        WHERE title LIKE %s OR message LIKE %s
        """,
        (f"%{MARKER}%", f"%{MARKER}%"),
    )


def log_issues(issues: list[str]) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    lines = ["", f"[{now}] Notification endpoint test run", f"marker={MARKER}"]

    if issues:
        lines.append("status=FAILED")
        for idx, issue in enumerate(issues, start=1):
            lines.append(f"{idx}. {issue}")
    else:
        lines.append("status=PASSED")
        lines.append("No issues found.")

    with ISSUES_FILE.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main() -> int:
    failures: list[str] = []

    admin = pick_user_for_role("admin")
    if not admin:
        failures.append("Precondition failed: no admin user found in users table.")

    owner = pick_any_user()
    if not owner:
        failures.append("Precondition failed: no user found in users table.")

    if failures:
        log_issues(failures)
        print("FAIL")
        for item in failures:
            print(f"- {item}")
        return 1

    assert admin is not None
    assert owner is not None

    if int(admin["user_id"]) == int(owner["user_id"]):
        alt = pick_any_user(exclude_user_id=int(owner["user_id"]))
        if alt:
            owner = alt

    outsider = pick_any_user(exclude_user_id=int(owner["user_id"]))
    broadcast_role = pick_role_for_broadcast()

    seed_unread = insert_notification(
        int(owner["user_id"]),
        f"{MARKER}-seed-unread-1",
        f"{MARKER}-seed-unread-1",
        is_read=0,
    )
    _seed_unread_2 = insert_notification(
        int(owner["user_id"]),
        f"{MARKER}-seed-unread-2",
        f"{MARKER}-seed-unread-2",
        is_read=0,
    )
    seed_read = insert_notification(
        int(owner["user_id"]),
        f"{MARKER}-seed-read-1",
        f"{MARKER}-seed-read-1",
        is_read=1,
    )

    outsider_notif = None
    if outsider:
        outsider_notif = insert_notification(
            int(outsider["user_id"]),
            f"{MARKER}-outsider",
            f"{MARKER}-outsider",
            is_read=0,
        )

    client = app.test_client()

    tests: list[tuple[str, Any]] = []

    def run_case(name: str, fn) -> None:
        try:
            fn()
            tests.append((name, "PASS"))
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{name}: {exc}")
            tests.append((name, "FAIL"))

    def case_unauthorized_get_notifications() -> None:
        res = client.get("/notifications/")
        ensure(res.status_code == 403, f"expected 403, got {res.status_code}")

    def case_get_notifications() -> None:
        set_session(client, int(owner["user_id"]), str(owner["role"]))
        res = client.get("/notifications/")
        ensure(res.status_code == 200, f"expected 200, got {res.status_code}")
        payload = res.get_json() or {}
        ensure(isinstance(payload.get("data"), list), "expected data to be a list")
        ids = {row.get("notification_id") for row in payload.get("data", []) if isinstance(row, dict)}
        ensure(seed_unread in ids, "seed unread notification not returned")
        ensure(seed_read in ids, "seed read notification not returned")

    def case_filter_unread() -> None:
        set_session(client, int(owner["user_id"]), str(owner["role"]))
        res = client.get("/notifications/?is_read=0")
        ensure(res.status_code == 200, f"expected 200, got {res.status_code}")
        payload = res.get_json() or {}
        for row in payload.get("data", []):
            ensure(str(row.get("is_read")) in ("0", "False", "false"), "found read notification in unread filter")

    def case_unread_count() -> None:
        expected = count_unread(int(owner["user_id"]))
        set_session(client, int(owner["user_id"]), str(owner["role"]))
        res = client.get("/notifications/unread-count")
        ensure(res.status_code == 200, f"expected 200, got {res.status_code}")
        payload = res.get_json() or {}
        actual = ((payload.get("data") or {}).get("unread_count"))
        ensure(int(actual) == int(expected), f"expected unread_count={expected}, got {actual}")

    def case_mark_single_read() -> None:
        set_session(client, int(owner["user_id"]), str(owner["role"]))
        res = client.put(f"/notifications/{seed_unread}/read")
        ensure(res.status_code == 200, f"expected 200, got {res.status_code}")
        row = run_query(
            "SELECT is_read FROM notifications WHERE notification_id = %s",
            (seed_unread,),
            fetch="one",
        )
        ensure(row and int(row["is_read"]) == 1, "notification was not marked as read")

    def case_mark_single_read_outsider() -> None:
        if outsider_notif is None:
            return
        set_session(client, int(owner["user_id"]), str(owner["role"]))
        res = client.put(f"/notifications/{outsider_notif}/read")
        ensure(res.status_code == 404, f"expected 404, got {res.status_code}")

    def case_read_all() -> None:
        new_unread = insert_notification(
            int(owner["user_id"]),
            f"{MARKER}-seed-unread-readall",
            f"{MARKER}-seed-unread-readall",
            is_read=0,
        )
        set_session(client, int(owner["user_id"]), str(owner["role"]))
        res = client.put("/notifications/read-all")
        ensure(res.status_code == 200, f"expected 200, got {res.status_code}")
        row = run_query(
            "SELECT is_read FROM notifications WHERE notification_id = %s",
            (new_unread,),
            fetch="one",
        )
        ensure(row and int(row["is_read"]) == 1, "read-all did not mark test notification as read")

    def case_delete_notification() -> None:
        target = insert_notification(
            int(owner["user_id"]),
            f"{MARKER}-delete-me",
            f"{MARKER}-delete-me",
            is_read=0,
        )
        set_session(client, int(owner["user_id"]), str(owner["role"]))
        res = client.delete(f"/notifications/{target}")
        ensure(res.status_code == 200, f"expected 200, got {res.status_code}")
        row = run_query(
            "SELECT notification_id FROM notifications WHERE notification_id = %s",
            (target,),
            fetch="one",
        )
        ensure(row is None, "notification was not deleted")

    def case_delete_not_found() -> None:
        set_session(client, int(owner["user_id"]), str(owner["role"]))
        res = client.delete("/notifications/999999999")
        ensure(res.status_code == 404, f"expected 404, got {res.status_code}")

    def case_admin_create_for_user() -> None:
        set_session(client, int(admin["user_id"]), str(admin["role"]))
        res = client.post(
            "/notifications/admin/notifications",
            json={
                "title": f"{MARKER}-admin-direct",
                "message": f"{MARKER}-admin-direct",
                "channel": "in_app",
                "user_id": int(owner["user_id"]),
            },
        )
        ensure(res.status_code == 201, f"expected 201, got {res.status_code}; body={res.get_json()}")

    def case_admin_create_missing_fields() -> None:
        set_session(client, int(admin["user_id"]), str(admin["role"]))
        res = client.post(
            "/notifications/admin/notifications",
            json={
                "message": f"{MARKER}-missing-title",
                "user_id": int(owner["user_id"]),
            },
        )
        ensure(res.status_code == 400, f"expected 400, got {res.status_code}")

    def case_admin_create_for_role() -> None:
        if not broadcast_role:
            raise TestFailure("no user role found to test role-based broadcast")

        set_session(client, int(admin["user_id"]), str(admin["role"]))
        res = client.post(
            "/notifications/admin/notifications",
            json={
                "title": f"{MARKER}-admin-role",
                "message": f"{MARKER}-admin-role",
                "channel": "in_app",
                "role": broadcast_role,
            },
        )
        ensure(res.status_code == 201, f"expected 201, got {res.status_code}; body={res.get_json()}")

    def case_non_admin_cannot_create_admin_notification() -> None:
        set_session(client, int(owner["user_id"]), str(owner["role"]))
        res = client.post(
            "/notifications/admin/notifications",
            json={
                "title": f"{MARKER}-forbidden",
                "message": f"{MARKER}-forbidden",
                "user_id": int(owner["user_id"]),
            },
        )
        ensure(res.status_code == 403, f"expected 403, got {res.status_code}")

    def case_test_notification_endpoint() -> None:
        set_session(client, int(owner["user_id"]), str(owner["role"]))
        res = client.post(
            "/notifications/test",
            json={
                "title": f"{MARKER}-realtime-test",
                "message": f"{MARKER}-realtime-test",
            },
        )
        ensure(res.status_code == 201, f"expected 201, got {res.status_code}; body={res.get_json()}")
        payload = res.get_json() or {}
        ensure(isinstance(payload.get("data"), dict), "expected data object in test notification response")

    run_case("Unauthorized GET /notifications/", case_unauthorized_get_notifications)
    run_case("GET /notifications/", case_get_notifications)
    run_case("GET /notifications/?is_read=0", case_filter_unread)
    run_case("GET /notifications/unread-count", case_unread_count)
    run_case("PUT /notifications/<id>/read", case_mark_single_read)
    run_case("PUT /notifications/<id>/read outsider", case_mark_single_read_outsider)
    run_case("PUT /notifications/read-all", case_read_all)
    run_case("DELETE /notifications/<id>", case_delete_notification)
    run_case("DELETE /notifications/<id> not found", case_delete_not_found)
    run_case("POST /notifications/admin/notifications as admin", case_admin_create_for_user)
    run_case("POST /notifications/admin/notifications by role", case_admin_create_for_role)
    run_case("POST /notifications/admin/notifications missing title", case_admin_create_missing_fields)
    run_case("POST /notifications/admin/notifications as non-admin", case_non_admin_cannot_create_admin_notification)
    run_case("POST /notifications/test", case_test_notification_endpoint)

    cleanup_test_rows()
    log_issues(failures)

    print("Notification endpoint test summary")
    for name, status in tests:
        print(f"[{status}] {name}")

    if failures:
        print("\nIssues detected:")
        for item in failures:
            print(f"- {item}")
        return 1

    print("\nAll tested notification endpoints passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
