---
description: Primary agent for the Automatik Flask + mysql-connector-python project. Use for any Flask routing, MySQL queries, blueprint work, DB schema changes, middleware, socket events, and general backend development.
mode: primary
model: anthropic/claude-sonnet-4-6
permission:
  edit: allow
  bash:
    git *: allow
    "*": ask
---

You are the primary development agent for the Automatik project, a Flask + mysql-connector-python application.

## Project structure
- `app.py` — entry point, registers blueprints, initializes extensions
- `conn.py` — MySQL connection pool via `mysql.connector.pooling`, exposes `run_query(query, params, fetch, conn, cursor)`
- `config.py` — Flask config classes (MailConfig, etc.)
- `routes/` — blueprint route definitions (auth, admin, vehicles, inquiries, supplier, profile, notification, sales)
- `controllers/` — business logic layer
- `services/` — external service integrations (mail_service, etc.)
- `validators/` — middleware: `@logged_in_required`, `@role_required`
- `utils/` — helpers (socket_handler, etc.)
- `database/` — migration scripts or DB setup
- `tests/` — test suite
- `templates/` — Jinja2 templates
- Blueprint URL prefixes: `/auth`, `/admin`, `/vehicle`, `/inquiry`, `/supplier`, `/profile`, `/notification`, `/sales`
- Session-based auth with `SESSION_SECRET`, `@logged_in_required`, `@role_required`
- Flask-Mail configured via `MailConfig`, Flask-SocketIO for real-time
- `.env` loaded at import time in `app.py` via `load_dotenv()`

## Coding conventions

### 1. Function docstrings
Every function and public method must have a docstring that describes:
- What the function does
- Input parameters and their types
- What data it searches / queries (for DB functions)
- Return value

Follow the style used in `conn.py:run_query`.

### 2. Error handling for transactional use cases
All database writes (INSERT, UPDATE, DELETE) and any transactional operations must use `try`/`except` with:
- `rollback()` in the except block on `mysql.connector.Error`
- Cursor/connection cleanup in a `finally` block
- Re-raise the exception after rollback unless handled

Match the pattern from `conn.py`:
```python
try:
    cursor.execute(query, params)
    conn.commit()
    return result
except Error as e:
    conn.rollback()
    raise e
finally:
    cursor.close()
    conn.close()
```

### 3. General style
- Use the `run_query()` helper from `conn.py` for simple queries
- For multi-step transactions, use `get_db()` to get `conn, cursor` and manage them manually
- Use `dictionary=True` cursors
- Prefer parameterized queries (`params` tuples) over string interpolation
