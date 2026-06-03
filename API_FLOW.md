

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 1
## AUTOMATIK
Flask API Flow Document
v2 Final — All Panelist Critiques Resolved
Stack: Python Flask · mysql-connector-python · Session Auth · Bcrypt · MySQLConnectionPool
Roles: ADMIN · AGENT · CUSTOMER · PUBLIC
## RESOLVED #1
HTTP status codes on every
endpoint
GET→200, POST→201, DELETE→204, conflict→409,
validation→422
RESOLVED #2Input validation rules documented
Per-field rules, rejection codes, sanitization notes
## RESOLVED #3
FOR UPDATE + lock timeout
handling
OperationalError catch, 503 response pattern
## RESOLVED #4
Amortization recompute uses
remaining balance
start_period + remaining_balance params added
RESOLVED #5Flask session security config
HTTPONLY, SECURE, SAMESITE, SECRET_KEY policy
RESOLVED #6File storage strategy defined
Storage backend decision + orphan cleanup cron
RESOLVED #7intent_tag taxonomy defined
ENUM list + fallback for unknown intents
RESOLVED #8Notification channel matrix
in_app vs email vs sms trigger map
## RESOLVED #9
MySQLConnectionPool
documented
Pool config, size, connection reuse pattern
RESOLVED #10CSRF protection added
Flask-WTF token pattern, exemptions for API routes

AUTOMATIK Flask API Flow — v2 Final (Panelist Resolved)
## 2
## TABLE OF CONTENTS
A. Technology Justification Flask vs alternatives — why this stack
B. Security Configuration Session hardening + CSRF + connection pool
- Authentication & Session Management token types, rate-limiting, portal magic-link
- Users & Profiles multi-table transaction pattern
- Vehicles & Inventory status transitions + FOR UPDATE + lock timeout
- Inquiries & Chatbot guest linking, chatbot_enabled gate, intent_tag ENUM
- Sales & Contracts 8-step transaction chain, validation rules
- Financing: Loans & Amortization H recompute with remaining_balance fix
- Payments cascade + completion checks
- Agent Module commission fallback, dashboard aggregates
- Customer Portal magic-link session, document access
- Service Bookings & Slots capacity + lock timeout
- Warranty Claims status chain, service booking link
- Documents file storage strategy, orphan cleanup
- Suppliers & Supplies low-stock threshold
- Notifications channel matrix, delivery strategy
- Audit Logs log_action() pattern
- System Settings key registry
- Table Join Reference critical JOINs
C. HTTP Status Code Reference full code registry
D. Input Validation Rules per-module field rules
E. Panelist Resolution Checklist all 10 issues addressed

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 3
## A
## Technology Justification
Why Flask + mysql-connector-python over alternatives
## PM NOTE
This section addresses the panelist requirement for a formal technology rationale. Required by most
PUP/Mapua capstone panels under 'Feasibility & Technology Justification.'
Architecture Decision: Monolithic Flask + MySQL
Automatik is a single-organisation dealership management system with a bounded user base (staff + registered customers). A
monolithic architecture with a relational database is appropriate for this scope. Microservices would introduce unnecessary
operational overhead for a capstone-scale project.
ConcernChosenAlternatives ConsideredDecision Rationale
## Backend
## Framework
Flask (Python)Django, FastAPI,
## Express.js
Flask gives explicit control over routing and
session management with minimal magic.
Django's ORM abstracts SQL in ways that
conflict with mysql-connector-python's direct
cursor model. FastAPI requires async patterns
that increase complexity for the team. Flask
matches team skill level and keeps SQL visible
for academic review.
## Database Drivermysql-connector-p
ython
SQLAlchemy, PyMySQLmysql-connector-python is the official Oracle
driver — no third-party risk. SQLAlchemy ORM
was evaluated but deferred: direct SQL keeps
query logic auditable by panelists and avoids
N+1 query patterns hidden behind ORM
abstraction.
DatabaseMySQL 8.xPostgreSQL, SQLiteMySQL is the standard RDBMS taught at PUP
and available on shared hosting. PostgreSQL
offers better concurrency (MVCC) but requires
infrastructure the team does not control.
SQLite is unsuitable for multi-user concurrent
writes.
Auth StrategyServer-side Flask
session
JWT, OAuth2Session auth is simpler to implement securely
for a server-rendered or same-origin SPA
setup. JWT requires token revocation
infrastructure (blacklist or short expiry) that
adds scope. Sessions are invalidated
immediately on logout.
File StorageCloud storage (see
## §12)
Local diskLocal disk storage is not suitable for
production — files are lost on server rebuild.
Cloud storage (S3-compatible or Cloudinary)
stores file_url in DB; files persist independently
of the application server.

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 4
## B
## Security Configuration
Session hardening · CSRF · Connection pool · Rate limiting
## RESOLVED #5
## + #9 + #10
Addresses session security, CSRF, and MySQLConnectionPool — all flagged as major gaps by
panelist.
## B.1 — Flask Session Security
# config.py — required production settings
import os, secrets
class Config:
# CRITICAL: strong, rotated secret key
SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
# Session cookie hardening
SESSION_COOKIE_HTTPONLY  = True   # JS cannot read cookie
SESSION_COOKIE_SECURE    = True   # HTTPS only (set False in local de
v only)
SESSION_COOKIE_SAMESITE  = "Lax"  # CSRF mitigation for same-site for
ms
SESSION_COOKIE_NAME      = "automatik_session"
PERMANENT_SESSION_LIFETIME = 3600  # 1 hour idle timeout (seconds)
# SECRET_KEY rotation policy:
# Rotate every 90 days. All existing sessions invalidate on rotation.
# Use environment variable; never hardcode in source.
B.2 — CSRF Protection
## RESOLVED #10
Flask-WTF CSRF tokens protect state-changing routes. Pure JSON API routes are exempt via
@csrf.exempt — they rely on SameSite + Content-Type: application/json as CSRF mitigation.
# app/__init__.py
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect()
def create_app():
app = Flask(__name__)
app.config.from_object(Config)
csrf.init_app(app)
return app
# On HTML forms — include CSRF token

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 5
# <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
# For JSON API routes consumed by frontend (fetch/axios):
@app.route("/api/some-route", methods=["POST"])
@csrf.exempt   # exempt JSON API routes
## @login_required
def api_route():
# CSRF still mitigated by:
# 1. SESSION_COOKIE_SAMESITE = Lax
# 2. Checking Content-Type: application/json header
if request.content_type != "application/json":
return jsonify({"error": "Invalid content type"}), 400
## ...
# Verify CSRF token explicitly for sensitive non-JSON operations:
from flask_wtf.csrf import validate_csrf
try:
validate_csrf(request.form.get("csrf_token"))
except:
return jsonify({"error": "CSRF validation failed"}), 403
B.3 — MySQL Connection Pool
## RESOLVED #9
Raw connections per request cause exhaustion under concurrent load. MySQLConnectionPool
maintains a fixed set of reusable connections.
# db.py — connection pool setup
import mysql.connector.pooling
from flask import g
POOL = mysql.connector.pooling.MySQLConnectionPool(
pool_name      = "automatik_pool",
pool_size      = 10,          # max concurrent connections
pool_reset_session = True,    # reset session state on return
host           = "localhost",
database       = "automatik_db",
user           = os.environ.get("DB_USER"),
password       = os.environ.get("DB_PASSWORD"),
autocommit     = False,       # explicit transaction control
connection_timeout = 30,      # seconds before OperationalError
## )

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 6
def get_db():
if "db" not in g:
g.db = POOL.get_connection()
return g.db
def close_db(e=None):
db = g.pop("db", None)
if db is not None:
db.close()   # returns connection to pool, not destroyed
# Register teardown in app factory
app.teardown_appcontext(close_db)
# Pool sizing guidance:
# pool_size = (expected concurrent users / 5) + 2
# For a dealership: 5 agents + 1 admin + 20 customers → pool_size=10 is safe
B.4 — Rate Limiting (Auth Routes)
## RESOLVED #1
## (auth)
Without rate limiting, /auth/forgot-password and /auth/resend-verify are brute-force / spam vectors.
# Using Flask-Limiter
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
limiter = Limiter(get_remote_address, app=app,
default_limits=["200 per day", "50 per hour"])
@app.route("/auth/forgot-password", methods=["POST"])
@limiter.limit("3 per hour")   # max 3 resets per IP per hour
def forgot_password(): ...
@app.route("/auth/resend-verify", methods=["POST"])
@limiter.limit("3 per hour")   # max 3 resend attempts per IP per hour
def resend_verify(): ...
# On limit exceeded: Flask-Limiter returns 429 Too Many Requests automatically
# Response body: {"error": "Rate limit exceeded. Try again in X seconds."}

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 7
## 1
## Authentication & Session Management
Tables: users, access_tokens, user_profile
## COMPLEX
Three token types share one table. Each has expiry + used_at logic. Portal magic-link bridges
guest→session. Validate: not expired AND used_at IS NULL.
## Metho
d
EndpointRoleDescriptionHTTP
## POST
## /auth/register
## Public
INSERT users (role=customer,
email_verified=0). bcrypt.hashpw().
Generate email_verify token →
INSERT access_tokens. Send
verification email. Validation: email
format (regex), password min 8 chars,
email uniqueness.
## 201
## 400 409
## POST
## /auth/login
## Public
SELECT user WHERE email.
bcrypt.checkpw(). Reject if is_active=0
(403) or email_verified=0 (403 with
message). SET session keys.
Validation: email required, password
required.
## 200
## 400 401 403
## POST
## /auth/logout
## Any
session.clear(). Returns 200 with
redirect URL.
## 200
## GET
## /auth/me
## Any
SELECT users JOIN user_profile
WHERE user_id=session['user_id'].
Return safe fields only (no
hashed_password).
## 200
## 401
## POST
## /auth/verify-email
## Public
Validate token (not expired, not used).
UPDATE users SET email_verified=1.
UPDATE access_tokens SET
used_at=NOW().
## 200
## 400 410
## POST
## /auth/forgot-password
## Public
Rate-limited: 3/hour per IP. Invalidate
old tokens. Generate password_reset
token (expires 1hr). INSERT
access_tokens. Send email. Always
return 200 (don't leak email existence).
## 200
## 429
## POST
## /auth/reset-password
## Public
Validate token.
bcrypt.hashpw(new_pw). UPDATE
users. Mark token used. Validation:
password min 8 chars, confirm match.
## 200
## 400 410
## POST
## /auth/resend-verify
## Public
Rate-limited: 3/hour per IP. Invalidate
old token. Generate new. Re-send
email.
## 200
## 429
## GET
## /portal/access
## Public
Consume portal_access token. SET
session['user_id'],
session['role']='customer'. Redirect to
/portal/dashboard. Single-use token.
## 302
## 400 410
## Session Logic

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 8
## # Decorators
from functools import wraps
from flask import session, jsonify, redirect, url_for
def login_required(f):
## @wraps(f)
def decorated(*args, **kwargs):
if "user_id" not in session:
return jsonify({"error": "Authentication required"}), 401
return f(*args, **kwargs)
return decorated
def role_required(*roles):
def decorator(f):
## @wraps(f)
def decorated(*args, **kwargs):
if session.get("role") not in roles:
return jsonify({"error": "Forbidden"}), 403
return f(*args, **kwargs)
return decorated
return decorator
# access_tokens: validate before consuming
def consume_token(cur, token, token_type):
cur.execute(
"SELECT t.*, u.is_active FROM access_tokens t "
"JOIN users u ON t.user_id = u.user_id "
"WHERE t.token = %s AND t.token_type = %s "
"AND t.used_at IS NULL AND t.expires_at > NOW()",
(token, token_type)
## )
row = cur.fetchone()
if not row:
return None, 410   # Gone: expired or already used
if not row["is_active"]:
return None, 403   # Forbidden: deactivated account
cur.execute("UPDATE access_tokens SET used_at = NOW() WHERE token_id = %s",
## (row["token_id"],))

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 9
return row, 200

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 10
## 2
## Users & Profiles
Tables: users, user_profile, customer_details, agent_details
## Metho
d
EndpointRoleDescriptionHTTP
## GET
## /admin/users
## Admin
List all users. Filter: ?role=,
## ?is_active=, ?search= (full_name
LIKE). Paginate: ?page=&per;_page=.
JOIN user_profile.
## 200
## 401 403
## GET
## /admin/users/<id>
## Admin
Single user + role-specific detail table.
404 if not found.
## 200
## 401 403 404
## POST
## /admin/users
## Admin
Multi-table INSERT in transaction.
Validation: email unique, role in enum,
required fields. Returns created
user_id.
## 201
## 400 409
## PUT
## /admin/users/<id>
## Admin
UPDATE users. Cannot change own
role. Log old→new in audit_logs.
## 200
## 400 403 404
## DELET
## E
## /admin/users/<id>
## Admin
Soft delete: UPDATE is_active=0.
Cannot delete self. Log audit.
## 204
## 403 404 409
## GET
## /profile
## Any
Own record: users JOIN user_profile
WHERE user_id=session['user_id'].
## 200
## 401
## PUT
## /profile
## Any
UPDATE user_profile only. Cannot
change role or email here.
## 200
## 400 401
## PUT
## /profile/password
## Any
Verify old password (bcrypt.checkpw).
Hash new. UPDATE. Validation: min 8
chars.
## 200
## 400 401
## GET
## /admin/agents
## Admin
JOIN users + user_profile +
agent_details WHERE role='agent'.
## 200
## 401 403
## POST
## /admin/agents
## Admin
Same as POST /admin/users
enforcing role=agent.
## 201
## 400 409
## PUT
## /admin/agents/<id>
## Admin
UPDATE agent_details
(commission_rate, hire_date). Validate
rate 0-100.
## 200
## 400 404
## GET
## /admin/customers
## Admin
JOIN users + user_profile +
customer_details WHERE
role='customer'.
## 200
## 401 403
## GET
## /admin/customers/<id>
## Admin
Detail + sales history.
## 200
## 401 403 404
## PUT
## /admin/customers/<id>
## Admin
UPDATE customer_details.
## 200
## 400 404
# Input validation helper (reusable)
import re
## VALIDATORS = {
"email":    lambda v: bool(re.match(r"^[^@]+@[^@]+\.[^@]+$", v)),

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 11
"phone":    lambda v: bool(re.match(r"^(\+63|0)9\d{9}$", v)),  # PH mobile
"password": lambda v: len(v) >= 8,
"role":     lambda v: v in ("admin", "agent", "customer"),
"rate":     lambda v: 0.0 <= float(v) <= 100.0,
## }
def validate(data, rules):
errors = {}
for field, checks in rules.items():
val = data.get(field)
if "required" in checks and not val:
errors[field] = "Required field missing"
continue
if val and "email" in checks and not VALIDATORS["email"](val):
errors[field] = "Invalid email format"
if val and "password" in checks and not VALIDATORS["password"](val):
errors[field] = "Password must be at least 8 characters"
if errors:
return None, jsonify({"error": "Validation failed", "fields": errors}), 422
return data, None, None

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 12
## 3
## Vehicles & Inventory
Tables: vehicles, vehicle_photos, suppliers
## COMPLEX +
## RESOLVED #3
Status transitions use SELECT...FOR UPDATE. Lock timeout is caught and returns 503 Service
Unavailable, not a raw 500.
## Metho
d
EndpointRoleDescriptionHTTP
## GET
## /vehicles
## Public
Filter: brand, model, fuel_type, status,
price_min, price_max. JOIN first photo
(MIN sort_order). Paginate.
## 200
## GET
## /vehicles/<id>
## Public
All photos ORDER BY sort_order +
supplier.company_name.
## 200
## 404
## POST
## /admin/vehicles
## Admin
INSERT vehicles. Validate: supplier_id
EXISTS, price > 0, status in enum.
Default status=available.
## 201
## 400 404 422
## PUT
## /admin/vehicles/<id>
## Admin
UPDATE. Log audit. Validate
specs_json parses as valid JSON.
## 200
## 400 404 422
## DELET
## E
## /admin/vehicles/<id>
## Admin
Check no active sales (status IN
pending,active). If clear:
status=discontinued. Else: 409.
## 204
## 403 404 409
## POST
## /admin/vehicles/<id>/photos
## Admin
INSERT vehicle_photos. Validate:
sort_order >= 0, URL not empty.
## 201
## 400 404
## DELET
## E
## /admin/vehicles/<id>/photos/
## <pid>
## Admin
DELETE WHERE photo_id=? AND
vehicle_id=? (ownership check).
## 204
## 404
## PUT
## /admin/vehicles/<id>/status
## Admin
Manual status override. Validate
transition legal. Log audit.
## 200
## 400 404 409
## GET
## /admin/vehicles/low-stock
## Admin
WHERE status=available. Compare
count vs
system_settings:low_stock_threshold.
## 200
## 401 403
# Vehicle status transition with lock timeout handling
import mysql.connector
## TRANSITIONS = {
## "available":    ["reserved", "discontinued"],
## "reserved":     ["available", "discontinued"],
## "delivered":    ["discontinued"],
## "discontinued": [],
## }
def transition_vehicle(vehicle_id, new_status, conn):
cur = conn.cursor(dictionary=True)
try:
cur.execute(

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 13
"SELECT status FROM vehicles WHERE vehicle_id=%s FOR UPDATE",
## (vehicle_id,))
row = cur.fetchone()
if not row:
return None, 404
if new_status not in TRANSITIONS[row["status"]]:
return {"error": f"Invalid transition: {row['status']} -> {new_status}"}, 409
cur.execute(
"UPDATE vehicles SET status=%s WHERE vehicle_id=%s",
(new_status, vehicle_id))
return {"status": new_status}, 200
except mysql.connector.errors.OperationalError as e:
if "Lock wait timeout" in str(e):
# RESOLVED #3: Return 503, not raw 500
return {"error": "Resource temporarily locked. Retry in a moment."}, 503
raise

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 14
## 4
## Inquiries & Chatbot
Tables: inquiries, chatbot_logs, agent_tasks
## RESOLVED #7
## + #8
intent_tag now has a defined ENUM taxonomy with unknown fallback. chatbot_enabled gate
documented. Guest session linking on register added.
## Metho
d
EndpointRoleDescriptionHTTP
## POST
## /inquiries
## Public
If logged-in: link user_id. Guest:
require guest_name (max 100 chars),
guest_email (valid format). Set
status=open. Validate vehicle_id exists
if provided.
## 201
## 400 422
## GET
## /inquiries
## Admin
## JOIN
inquiries+vehicles+user_profile+agent.
Filter: status, agent_id, date range.
## Paginate.
## 200
## 401 403
## GET
## /inquiries/my
## Customer
WHERE user_id=session['user_id'].
JOIN vehicles.
## 200
## 401
## GET
## /inquiries/<id>
Admin/Agen
t
Full detail + chatbot_logs WHERE
inquiry_id=?.
## 200
## 401 403 404
## PUT
## /admin/inquiries/<id>/assign
## Admin
UPDATE agent_id + status=assigned.
Notify agent. Reject if status=closed or
resolved.
## 200
## 400 404 409
## PUT
## /inquiries/<id>/resolve
## Agent
Verify agent owns inquiry. UPDATE
status=resolved, resolved_at=NOW().
## 200
## 401 403 404
## PUT
## /inquiries/<id>/close
## Admin
UPDATE status=closed. Only valid
from resolved.
## 200
## 400 404 409
## POST
## /chatbot/message
## Public
Check chatbot_enabled setting. Call
AI API. INSERT chatbot_logs. Return
response.
## 200
## 400 503
## GET
## /admin/chatbot/logs
## Admin
Filter: session_id, user_id, intent_tag
(from ENUM). Paginate.
## 200
## 401 403
## GET
## /admin/chatbot/logs/<id>
## Admin
Single log entry.
## 200
## 401 403 404
intent_tag ENUM Taxonomy
## RESOLVED #7
Exhaustive list below. DB column: VARCHAR(50) with application-level ENUM check. Unknown
intents → store as 'unclassified' + log for review.
Tag ValueTrigger DescriptionExample Message
price_inquiryUser asks about vehicle price /
payment
How much is the Civic?
test_driveUser wants to schedule a test driveCan I test drive the SUV?
availabilityUser asks if a vehicle is in stockIs the Fortuner available?
financingQuestions about loans or
installment
What are the monthly payments?

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 15
Tag ValueTrigger DescriptionExample Message
warrantyWarranty coverage questionsWhat does the warranty cover?
service_bookingService or maintenance schedulingI want to book a PMS.
document_requestOR, CR, or contract inquiryWhere is my Official Receipt?
complaintDissatisfaction or issue reportMy car has a problem.
general_inquiryCatch-all for unmatched polite
queries
Hello, I need help.
unclassifiedAI could not determine intent
## (fallback)
(any unrecognized pattern)
## INTENT_TAGS = {
## "price_inquiry","test_drive","availability","financing",
## "warranty","service_booking","document_request","complaint",
## "general_inquiry","unclassified"
## }
@app.route("/chatbot/message", methods=["POST"])
def chatbot_message():
# RESOLVED: check chatbot_enabled gate
cur = get_db().cursor(dictionary=True)
cur.execute("SELECT setting_value FROM system_settings WHERE setting_key='chatbot_enabled'")
setting = cur.fetchone()
if not setting or setting["setting_value"] != "1":
return jsonify({"error": "Chatbot is currently unavailable."}), 503
data = request.get_json()
message = data.get("message", "").strip()
if not message:
return jsonify({"error": "Message is required."}), 400
# Call AI API, get response + intent
ai_response, intent = call_ai_api(message)
# Sanitise intent
if intent not in INTENT_TAGS:
intent = "unclassified"
user_id    = session.get("user_id")
session_id = data.get("session_id")   # UUID from client localStorage
inquiry_id = data.get("inquiry_id")
cur.execute("""INSERT INTO chatbot_logs

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 16
(user_id, session_id, inquiry_id, user_message, bot_response, intent_tag)
VALUES (%s, %s, %s, %s, %s, %s)""",
(user_id, session_id, inquiry_id, message, ai_response, intent))
get_db().commit()
return jsonify({"response": ai_response, "intent": intent}), 200
# Guest session linking on registration
def link_guest_chatbot_logs(cur, new_user_id, session_id):
if session_id:
cur.execute(
"UPDATE chatbot_logs SET user_id=%s WHERE user_id IS NULL AND session_id=%s",
(new_user_id, session_id))

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 17
## 5
## Sales & Contracts
Tables: sales, sales_contracts, documents, insurance_records
## COMPLEX —
8-Step
## Transaction
Full rollback on any failure. Optional step (commission) handled without aborting required steps — see
pattern below.
## Metho
d
EndpointRoleDescriptionHTTP
## GET
## /admin/sales
## Admin
JOIN sales+vehicles+customer_profile
+agent_profile. Filter: status,
payment_type, date range.
## 200
## 401 403
## GET
## /admin/sales/<id>
## Admin
Full detail: +contracts+loan+payments
## +insurance+documents.
## 200
## 401 403 404
## POST
## /admin/sales
## Admin
8-step chain (all in transaction).
Validation: vehicle_id exists &
status=available, customer_id exists,
selling_price > 0, payment_type in
enum, if installment: loan_amount > 0,
term_months 1-60, interest_rate 0-30.
## 201
## 400 404 409
## 422
## PUT
## /admin/sales/<id>/status
## Admin
Validate transition. Log audit. Side
effects: cancel restores vehicle to
available.
## 200
## 400 404 409
## GET
## /sales/my
## Customer
WHERE customer_id=session. JOIN
vehicles+contracts.
## 200
## 401
## GET
## /sales/my/<id>
## Customer
Verify ownership. Full sale detail.
## 200
## 401 403 404
## GET
## /admin/sales/<id>/contract
Admin/Agen
t
Get contract record + status.
## 200
## 401 403 404
## POST
## /admin/sales/<id>/contract
## Admin
INSERT sales_contracts status=draft.
## 201
## 400 404 409
## PUT
## /admin/sales/<id>/contract/s
ign
## Admin
UPDATE status=signed,
signed_at=NOW(),
reviewed_by=session user.
## 200
## 400 404 409
## GET
## /admin/insurance
## Admin
JOIN insurance_records+sales+vehicl
es+customers.
## 200
## 401 403
## POST
## /admin/sales/<id>/insurance
## Admin
INSERT insurance record.
## 201
## 400 404
## PUT
## /admin/insurance/<id>
## Admin
UPDATE status, coverage dates.
## 200
## 400 404
## Sale Creation — Input Validation Rules
FieldTypeRuleError if Invalid
vehicle_idINTMust exist AND status='available'404 or 409 (already reserved)
customer_idINTMust exist, role=customer, is_active=1404
agent_idINTMust exist, role=agent, is_active=1;
nullable
404 if provided & not found
payment_typeENUMcash | installment422

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 18
FieldTypeRuleError if Invalid
selling_priceDECIMALMust be > 0422
loan_amountDECIMALRequired if installment. Must be > 0
and <= selling_price
## 422
term_monthsINTRequired if installment. Range: 6–60422
interest_rateDECIMALRequired if installment. Range:
## 0.0–30.0
## 422
Optional Steps in Required Transactions
# Pattern: wrap optional steps (commission) in inner try-except
# so a missing agent_id doesn't abort the whole sale
conn.autocommit = False
cur = conn.cursor(dictionary=True)
try:
# --- Required steps 1-3 ---
cur.execute("SELECT status FROM vehicles WHERE vehicle_id=%s FOR UPDATE",(vid,))
v = cur.fetchone()
if not v or v["status"] != "available":
conn.rollback()
return jsonify({"error":"Vehicle not available"}), 409
cur.execute(
"INSERT INTO sales (vehicle_id,customer_id,agent_id,payment_type,"
"selling_price,status,sale_date) VALUES (%s,%s,%s,%s,%s,'pending',NOW())",
(vid, cid, aid, ptype, price))
sale_id = cur.lastrowid
cur.execute("UPDATE vehicles SET status='reserved' WHERE vehicle_id=%s",(vid,))
# --- Step 4: optional installment branch ---
if ptype == "installment":
cur.execute(
"INSERT INTO loan_details (sale_id,loan_amount,interest_rate,"
"term_months,bank_approval_status) VALUES (%s,%s,%s,%s,'pending')",
(sale_id, loan_amount, interest_rate, term_months))
loan_id = cur.lastrowid
generate_amortization_schedule(cur, loan_id, loan_amount,
interest_rate, term_months, sale_date)
## # --- Step 5 ---

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 19
cur.execute("INSERT INTO sales_contracts (sale_id,status) VALUES (%s,'draft')",(sale_id,))
# --- Step 6: commission — optional, non-fatal ---
if aid:
try:
insert_agent_commission(cur, sale_id, aid, price)
except Exception as comm_err:
# Log but don't abort sale
app.logger.warning(f"Commission insert skipped: {comm_err}")
## # --- Steps 7-8 ---
log_action(cur, session["user_id"], "INSERT", "sales", sale_id, None,
{"sale_id": sale_id, "vehicle_id": vid})
notify(cur, cid, "sales", sale_id, f"Your sale has been created.")
conn.commit()
return jsonify({"sale_id": sale_id}), 201
except mysql.connector.errors.OperationalError as e:
conn.rollback()
if "Lock wait timeout" in str(e):
return jsonify({"error": "Resource locked. Retry."}), 503
raise
except Exception:
conn.rollback()
raise

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 20
## 6
## Financing: Loans & Amortization
Tables: loan_details, amortization_schedule
## RESOLVED #4
## — Critical Bug
## Fixed
Recompute now accepts remaining_balance + start_period. Passing original loan_amount after partial
payments produces mathematically wrong schedules. Fix: query SUM(principal_component) of paid
rows to derive remaining balance.
## Metho
d
EndpointRoleDescriptionHTTP
## GET
## /admin/loans
## Admin
JOIN loan_details+sales+customer_pr
ofile+vehicles. Filter:
bank_approval_status.
## 200
## 401 403
## GET
## /admin/loans/<id>
## Admin
Loan detail + full
amortization_schedule ORDER BY
period_number.
## 200
## 401 403 404
## POST
## /admin/sales/<id>/loan
## Admin
Create loan + generate schedule.
Validation: term_months 6-60,
interest_rate 0-30, loan_amount > 0.
## 201
## 400 404 422
## PUT
## /admin/loans/<id>
## Admin
UPDATE bank_approval_status.
Notify customer. Log audit.
## 200
## 400 404
## GET
## /admin/loans/<id>/schedule
## Admin
Full schedule for loan. Include:
period_number, due_date,
amount_due, principal, interest,
balance, status.
## 200
## 401 403 404
## GET
## /loans/my
## Customer
Own loan + schedule. Verify
ownership via sales.customer_id.
## 200
## 401 404
## PUT
## /admin/amortization/<id>/sta
tus
## Admin
Mark paid/overdue. Notify customer.
Validate: only unpaid rows can be
marked paid.
## 200
## 400 404 409
## GET
## /admin/amortization/overdue
## Admin
WHERE status=unpaid AND due_date
< NOW(). JOIN loan+sales+customer.
## 200
## 401 403
## POST
## /admin/loans/<id>/compute
## Admin
Recompute with remaining_balance
fix. See code below.
## 200
## 400 404 422
Amortization Generator (Decimal-safe, start_period support)
from decimal import Decimal, ROUND_HALF_UP
from dateutil.relativedelta import relativedelta
def generate_amortization_schedule(
cur, loan_id, loan_amount, interest_rate,
term_months, sale_date,
start_period=1,        # for recompute: first new period number
remaining_balance=None # for recompute: balance after paid periods
## ):
## """

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 21
Generates amortization_schedule rows.
- For new loans:    start_period=1, remaining_balance=None (uses loan_amount)
- For recompute:    start_period=N, remaining_balance=actual_remaining
## """
principal = Decimal(str(remaining_balance if remaining_balance else loan_amount))
rate      = Decimal(str(interest_rate))
monthly_r = rate / Decimal("100") / Decimal("12")
n         = term_months  # remaining months to schedule
if monthly_r == 0:
monthly_pay = (principal / Decimal(n)).quantize(
Decimal("0.01"), ROUND_HALF_UP)
else:
monthly_pay = (
principal * monthly_r /
(1 - (1 + monthly_r) ** -n)
).quantize(Decimal("0.01"), ROUND_HALF_UP)
running_bal = principal
rows = []
for i in range(n):
period   = start_period + i
interest = (running_bal * monthly_r).quantize(Decimal("0.01"), ROUND_HALF_UP)
princ    = monthly_pay - interest
if i == n - 1:           # last payment: absorb rounding
princ      = running_bal
monthly_pay = princ + interest
running_bal -= princ
due_date = sale_date + relativedelta(months=period)
rows.append((loan_id, period, due_date,
float(monthly_pay), float(princ), float(interest),
float(max(running_bal, Decimal("0"))), "unpaid"))
cur.executemany("""
INSERT INTO amortization_schedule
(loan_id, period_number, due_date, amount_due,
principal_component, interest_component, remaining_balance, status)

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 22
VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""", rows)
cur.execute("UPDATE loan_details SET monthly_amortization=%s WHERE loan_id=%s",
(float(monthly_pay), loan_id))
def recompute_amortization(cur, loan_id, new_rate, new_term, sale_date):
"""Recompute schedule after rate/term change, preserving paid periods."""
# 1. Get paid periods to find remaining balance
cur.execute("""
SELECT COALESCE(SUM(principal_component), 0) AS paid_principal,
COUNT(*) AS paid_count,
MAX(period_number) AS last_paid_period
FROM amortization_schedule
WHERE loan_id=%s AND status='paid'""", (loan_id,))
paid = cur.fetchone()
cur.execute("SELECT loan_amount FROM loan_details WHERE loan_id=%s", (loan_id,))
loan = cur.fetchone()
# RESOLVED #4: remaining_balance = original - paid principal
remaining = float(loan["loan_amount"]) - float(paid["paid_principal"])
start_p   = int(paid["last_paid_period"] or 0) + 1
new_n     = new_term - int(paid["paid_count"])
# 2. Delete only unpaid rows
cur.execute(
"DELETE FROM amortization_schedule WHERE loan_id=%s AND status='unpaid'",
## (loan_id,))
# 3. Regenerate from correct starting point
generate_amortization_schedule(
cur, loan_id, loan["loan_amount"], new_rate, new_n,
sale_date, start_period=start_p, remaining_balance=remaining)
cur.execute("UPDATE loan_details SET interest_rate=%s, term_months=%s WHERE loan_id=%s",
(new_rate, new_term, loan_id))

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 23
## 7
## Payments
Tables: payments, amortization_schedule
## COMPLEX
Payment cascade touches 4 tables. Entire flow must be in one transaction.
## Metho
d
EndpointRoleDescriptionHTTP
## GET
## /admin/payments
## Admin
JOIN payments+sales+users(as
recorder)+amortization. Filter: method,
date range.
## 200
## 401 403
## GET
## /admin/payments/<id>
## Admin
Single payment with full context.
## 200
## 401 403 404
## POST
## /admin/sales/<id>/payments
## Admin
Record payment. 5-step cascade.
Validation: amount_paid > 0,
payment_method in enum,
schedule_id must be unpaid if
provided.
## 201
## 400 404 409
## 422
## GET
## /payments/my
## Customer
Own payments JOIN sales+schedule.
Verify via sales.customer_id.
## 200
## 401
## GET
## /admin/sales/<id>/payments
## Admin
All payments for one sale ORDER BY
payment_date DESC.
## 200
## 401 403 404
## GET
## /admin/payments/summary
## Admin
## GROUP BY YEAR/MONTH.
SUM(amount_paid). Filter: ?year=.
Returns monthly totals.
## 200
## 401 403
# Payment validation rules
def validate_payment(cur, sale_id, schedule_id, amount_paid):
if amount_paid <= 0:
return "amount_paid must be greater than 0", 422
if schedule_id:
cur.execute(
"SELECT status FROM amortization_schedule WHERE schedule_id=%s AND loan_id="
"(SELECT loan_id FROM loan_details WHERE sale_id=%s)",
(schedule_id, sale_id))
row = cur.fetchone()
if not row:
return "Schedule row not found for this sale", 404
if row["status"] == "paid":
return "This schedule row is already paid", 409
return None, None

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 24
## 8
## Agent Module
Tables: agent_details, agent_commissions, agent_tasks
## Metho
d
EndpointRoleDescriptionHTTP
## GET
## /agent/dashboard
## Agent
Aggregate: COUNT assigned
inquiries, COUNT pending tasks, SUM
unpaid commissions, 5 recent sales.
## 200
## 401 403
## GET
## /agent/inquiries
## Agent
WHERE agent_id=session. JOIN
vehicles+customer_profile.
## 200
## 401 403
## GET
## /agent/tasks
## Agent
WHERE agent_id=session. JOIN
inquiries(LEFT). Filter: status,
task_type.
## 200
## 401 403
## POST
## /agent/tasks
## Agent
INSERT task. Validate inquiry belongs
to this agent if inquiry_id provided.
## 201
## 400 403 422
## PUT
## /agent/tasks/<id>
## Agent
UPDATE. Verify ownership.
## 200
## 401 403 404
## DELET
## E
## /agent/tasks/<id>
## Agent
Soft delete: status=cancelled. Verify
ownership.
## 204
## 401 403 404
## GET
## /agent/commissions
## Agent
WHERE agent_id=session. JOIN
sales+vehicles.
## 200
## 401 403
## GET
## /admin/commissions
## Admin
All commissions. Filter: agent_id,
is_paid.
## 200
## 401 403
## PUT
## /admin/commissions/<id>/pay
## Admin
UPDATE is_paid=1, paid_at=NOW().
Notify agent.
## 200
## 401 403 404
## GET
## /admin/agents/<id>/performan
ce
## Admin
Aggregate: total_sales, revenue,
commission_total, avg_rate over date
range.
## 200
## 401 403 404

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 25
## 9
## Customer Portal
Tables: customer_details, sales, loan_details, amortization_schedule, documents, notifications
## NOTE
All /portal/* routes: @login_required + @role_required('customer'). Ownership verified on every
sale/document/inquiry query.
## Metho
d
EndpointRoleDescriptionHTTP
## GET
## /portal/dashboard
## Customer
Active sales count, next due
date+amount (MIN due_date WHERE
status=unpaid), open inquiry count,
unread notification count.
## 200
## 401 403
## GET
## /portal/vehicles
## Customer
Public vehicle list. No extra restriction.
## 200
## 401
## GET
## /portal/sales
## Customer
WHERE customer_id=session. JOIN
vehicles+contracts.
## 200
## 401
## GET
## /portal/sales/<id>
## Customer
Verify ownership. Full detail: contract+l
oan+schedule+payments+docs.
## 200
## 401 403 404
## GET
## /portal/payments
## Customer
Own payment history JOIN
sales+schedule.
## 200
## 401
## GET
## /portal/amortization
## Customer
Own active loan schedule. ORDER BY
due_date.
## 200
## 401
## GET
## /portal/documents
## Customer
WHERE is_accessible=1 AND sale in
own sales.
## 200
## 401
## GET
## /portal/documents/<id>
## Customer
Return file_url. Verify is_accessible=1
AND ownership.
## 200
## 401 403 404
## GET
## /portal/inquiries
## Customer
WHERE user_id=session.
## 200
## 401
## POST
## /portal/inquiries
## Customer
INSERT with user_id=session. No
guest fields needed.
## 201
## 400 422
## GET
## /portal/notifications
## Customer
ORDER BY created_at DESC. Filter:
## ?is_read=.
## 200
## 401
## PUT
## /portal/notifications/<id>/r
ead
## Customer
UPDATE is_read=1. Verify user_id.
## 200
## 401 404
## PUT
## /portal/profile
## Customer
UPDATE user_profile +
customer_details.
## 200
## 400 401 422
## GET
## /portal/insurance
## Customer
Own insurance JOIN vehicles+sales.
## 200
## 401
## GET
## /portal/warranty
## Customer
Own warranty claims.
## 200
## 401
## POST
## /portal/warranty
## Customer
Verify sale ownership. INSERT
warranty_claims status=submitted.
## 201
## 400 403 404
## 422

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 26
## 10
## Service Bookings & Slots
Tables: service_bookings, service_slots
## RESOLVED #3
## (slots)
Slot capacity uses FOR UPDATE. Lock timeout → 503. Cancel restores capacity atomically.
## Metho
d
EndpointRoleDescriptionHTTP
## GET
## /service/slots
## Public
WHERE is_available=1 AND
slot_datetime >= NOW(). Show
remaining=capacity-booked.
## 200
## GET
## /service/slots/<id>
## Public
Slot detail + remaining count.
## 200
## 404
## POST
## /admin/service/slots
## Admin
INSERT slot. Validate: capacity > 0,
slot_type in enum.
## 201
## 400 422
## PUT
## /admin/service/slots/<id>
## Admin
UPDATE capacity or is_available. If
reducing capacity < current bookings:
## 409.
## 200
## 400 404 409
## DELET
## E
## /admin/service/slots/<id>
## Admin
Check no confirmed/pending
bookings. If clear: DELETE. Else: 409.
## 204
## 404 409
## GET
## /admin/service/bookings
## Admin
## JOIN
bookings+customers+vehicles+slots.
## 200
## 401 403
## GET
## /service/bookings/my
## Customer
WHERE customer_id=session.
## 200
## 401
## POST
## /service/bookings
## Customer
Atomic 4-step with FOR UPDATE. On
lock timeout: 503.
## 201
## 400 404 409
## 422 503
## PUT
## /admin/service/bookings/<id>
## /confirm
## Admin
UPDATE status=confirmed. Notify
customer.
## 200
## 401 403 404
## PUT
## /admin/service/bookings/<id>
## /complete
## Admin
UPDATE status=completed.
## 200
## 401 403 404
## PUT
## /service/bookings/<id>/cance
l
## Customer
Verify ownership. UPDATE
status=cancelled. Restore slot
capacity.
## 200
## 401 403 404
## 409

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 27
## 11
## Warranty Claims
Tables: warranty_claims, sales, vehicles, service_bookings
## Metho
d
EndpointRoleDescriptionHTTP
## GET
## /admin/warranty
## Admin
JOIN warranty_claims+sales+vehicles
+customer+reviewer(LEFT). Filter:
status.
## 200
## 401 403
## GET
## /admin/warranty/<id>
## Admin
Detail + linked service_bookings.
## 200
## 401 403 404
## POST
## /warranty
## Customer
Verify sale ownership. INSERT
status=submitted. Validate:
issue_description not empty, max
1000 chars.
## 201
## 400 403 404
## 422
## GET
## /warranty/my
## Customer
WHERE customer_id=session. JOIN
vehicles+sales.
## 200
## 401
## PUT
## /admin/warranty/<id>/review
## Admin
UPDATE status=under_review,
reviewed_by=session. Log audit.
## 200
## 401 403 404
## PUT
## /admin/warranty/<id>/approve
## Admin
UPDATE status=approved. Notify
customer.
## 200
## 401 403 404
## 409
## PUT
## /admin/warranty/<id>/reject
## Admin
UPDATE status=rejected,
resolution_notes required. Notify
customer.
## 200
## 400 401 403
## 404
## PUT
## /admin/warranty/<id>/resolve
## Admin
UPDATE status=resolved,
resolved_at=NOW(). Notify customer.
## 200
## 401 403 404
## 409

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 28
## 12
## Documents
Tables: documents, sales
## RESOLVED #6
File storage strategy now defined. Orphan file cleanup strategy documented.
## Metho
d
EndpointRoleDescriptionHTTP
## GET
## /admin/documents
## Admin
Filter: document_type, sale_id. JOIN
sales+customer.
## 200
## 401 403
## GET
## /admin/documents/<id>
## Admin
Return file_url + metadata.
## 200
## 401 403 404
## POST
## /admin/sales/<id>/documents
## Admin
INSERT document record. file_url =
cloud storage URL (see below).
Validate: document_type in enum.
## 201
## 400 404 422
## PUT
## /admin/documents/<id>
## Admin
UPDATE file_url or is_accessible
toggle.
## 200
## 400 404
## DELET
## E
## /admin/documents/<id>
## Admin
DELETE DB record only. Physical file
NOT deleted by this route.
## 204
## 404
## GET
## /portal/documents
## Customer
WHERE is_accessible=1 AND in own
sales.
## 200
## 401
## File Storage Strategy
AspectDecisionNotes
Storage BackendS3-compatible (AWS S3,
Cloudflare R2, or
## Backblaze B2)
file_url stored in documents.file_url as full HTTPS URL. Files survive
server rebuilds.
Upload FlowServer-side signed URL or
direct upload
Option A: Server calls S3 PUT, stores returned URL. Option B:
Generate pre-signed URL, client uploads directly, server stores URL.
Access Controlis_accessible flag in DB +
ownership check
File URL itself may be public CDN URL or requires signed download
URL per request.
Orphan CleanupNightly cron jobSELECT file_url FROM documents. Compare with S3 bucket listing.
DELETE S3 objects not in documents table.
Local DevFlask serves from /uploads/
static folder
Acceptable for development only. Switch to cloud before production.

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 29
## 13
## Suppliers & Supplies
Tables: suppliers, supplies
## Metho
d
EndpointRoleDescriptionHTTP
## GET
## /admin/suppliers
## Admin
Filter: is_active. COUNT vehicles per
supplier.
## 200
## 401 403
## GET
## /admin/suppliers/<id>
## Admin
Detail + vehicle count + supplies list.
## 200
## 401 403 404
## POST
## /admin/suppliers
## Admin
INSERT. Validate: company_name not
empty, email valid.
## 201
## 400 422
## PUT
## /admin/suppliers/<id>
## Admin
UPDATE contact info, toggle is_active.
## 200
## 400 404
## GET
## /admin/supplies
## Admin
JOIN suppliers. Filter: ?low_stock=1
(WHERE stock_qty<=reorder_level).
## 200
## 401 403
## GET
## /admin/supplies/<id>
## Admin
Supply detail + supplier info.
## 200
## 401 403 404
## POST
## /admin/supplies
## Admin
INSERT. Validate: supplier_id exists,
unit_cost>0, stock_qty>=0,
reorder_level>=0.
## 201
## 400 404 422
## PUT
## /admin/supplies/<id>
## Admin
UPDATE. Same validations.
## 200
## 400 404 422
## DELET
## E
## /admin/supplies/<id>
## Admin
DELETE. Check no active service
booking refs this part.
## 204
## 404 409
## GET
## /admin/supplies/low-stock
## Admin
WHERE stock_qty<=reorder_level.
JOIN supplier contact.
## 200
## 401 403

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 30
## 14
## Notifications
Tables: notifications
## RESOLVED #8
Notification channel matrix now defined. in_app is always created. Email/SMS fire based on trigger
type and user preference.
## Metho
d
EndpointRoleDescriptionHTTP
## GET
## /notifications
## Any
Own notifications. Filter: is_read,
channel. ORDER BY created_at
DESC. Paginate.
## 200
## 401
## GET
## /notifications/unread-count
## Any
COUNT WHERE is_read=0. For
badge display.
## 200
## 401
## PUT
## /notifications/<id>/read
## Any
UPDATE is_read=1 WHERE
notification_id=? AND
user_id=session.
## 200
## 401 404
## PUT
## /notifications/read-all
## Any
UPDATE is_read=1 WHERE
user_id=session AND is_read=0.
## 200
## 401
## POST
## /admin/notifications
## Admin
Broadcast to user_id or all users of a
role.
## 201
## 400 422
## DELET
## E
## /notifications/<id>
## Any
DELETE WHERE notification_id=?
AND user_id=session.
## 204
## 401 404
## Notification Channel Matrix
Trigger Eventin_appEmailSMSNotes
Sale created33—Email: sale confirmation with vehicle details
Inquiry assigned3——Agent only, in-app sufficient
Amortization due (3 days)333All channels — financial reminder
Amortization overdue333All channels — escalate
Payment received33—Email: receipt-style confirmation
Warranty approved33—Email: includes service booking link
Booking confirmed33—Email: include date/time/location
Commission paid3——Agent in-app only
Loan status updated33—Email if approved or rejected
Password reset—3—Email only (security event)
Email: use Flask-Mail or SMTP relay (e.g. SendGrid, Mailgun). SMS: optional — use Semaphore SMS (PH-based, common in PUP
capstones) or Twilio. Check preferred_contact_method from customer_details before sending SMS.

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 31
## 15
## Audit Logs
Tables: audit_logs
## Metho
d
EndpointRoleDescriptionHTTP
## GET
## /admin/audit-logs
## Admin
Filter: action, table_name, user_id,
date range. Paginate.
## 200
## 401 403
## GET
## /admin/audit-logs/<id>
## Admin
Return old_value + new_value JSON
diff.
## 200
## 401 403 404
import json
from flask import request, session
# Critical tables requiring audit logging:
## AUDITED_TABLES = {
## "vehicles","sales","users","loan_details",
## "payments","warranty_claims","system_settings"
## }
def log_action(cur, user_id, action, table_name, record_id,
old_val=None, new_val=None):
cur.execute("""
INSERT INTO audit_logs
(user_id, action, table_name, record_id,
old_value, new_value, ip_address, created_at)
VALUES (%s,%s,%s,%s,%s,%s,%s,NOW())""",
(user_id, action, table_name, record_id,
json.dumps(old_val) if old_val else None,
json.dumps(new_val) if new_val else None,
request.remote_addr))
## 16
## System Settings
Tables: system_settings
## Metho
d
EndpointRoleDescriptionHTTP
## GET
## /admin/settings
## Admin
All settings as key-value pairs.
## 200
## 401 403
## GET
## /admin/settings/<key>
## Admin
Single setting by key. 404 if not found.
## 200
## 401 403 404
## PUT
## /admin/settings/<key>
## Admin
UPDATE value. Log audit (old→new).
UPDATE updated_by, updated_at.
## 200
## 400 401 403
## 404

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 32
## Metho
d
EndpointRoleDescriptionHTTP
## POST
## /admin/settings
## Admin
INSERT new key. Must be unique. 409
if duplicate.
## 201
## 400 409 422
KeyTypeDefaultUsed In
default_commission_rateDECIMAL(5,2)5.00agent_commissions INSERT fallback
chatbot_enabledTINYINT(1)1POST /chatbot/message gate
max_loan_term_monthsINT60loan creation validation cap
low_stock_thresholdINT3GET /admin/vehicles/low-stock
email_verify_expiry_hoursINT24access_tokens expires_at for email_verify
portal_token_expiry_daysINT7access_tokens expires_at for portal_access
session_lifetime_secondsINT3600PERMANENT_SESSION_LIFETIME config

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 33
## 17
## Table Join Reference
Critical JOINs per module
Primary TableJoined WithPurpose
usersuser_profileFull name, phone, address for any user
usersagent_detailsemployee_number, commission_rate
userscustomer_detailscustomer_number, preferences,
contact_method
vehiclesvehicle_photosPhotos ORDER BY sort_order; first photo for
listings
vehiclessupplierssupplier company_name per vehicle
inquiriesvehicles + users + agent_detailsFull inquiry: vehicle, customer, assigned
agent
salesvehicles + customer_details +
agent_details
Sale with all parties
salessales_contractsContract status per sale
salesloan_detailsFinancing for installment sales
salesinsurance_recordsInsurance per sale
salesdocumentsOR, CR, warranty docs per sale
loan_detailsamortization_scheduleFull payment breakdown; ORDER BY
period_number
amortization_schedulepaymentsMatch payments to schedule rows
paymentsusers AS recorded_byWho recorded each payment
agent_commissionssales + agent_details + user_profileAgent payout report
agent_tasksinquiries + vehiclesTask with linked inquiry context
service_bookingsservice_slots + vehicles +
customer_details
Full booking detail
warranty_claimssales + vehicles + users AS reviewed_byClaim with review context
chatbot_logsusers + inquiriesChatbot thread linked to user and inquiry
notificationsusersNotification with recipient name
suppliessuppliersPart with supplier contact info
audit_logsusers AS actorLog with actor name
system_settingsusers AS updaterWho last changed this setting
access_tokensusersToken validation with user status check

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 34
## C
HTTP Status Code Reference
All codes used in Automatik API
CodeNameWhen Used in Automatik
200OKSuccessful GET, PUT, DELETE (with body)
201CreatedSuccessful POST that creates a resource
204No ContentSuccessful DELETE (no body)
302Found (Redirect)Portal magic-link redirect after token consumption
400Bad RequestMissing required field, malformed JSON, invalid body
401UnauthorizedNo active session / not logged in
403ForbiddenLogged in but wrong role, or account deactivated
404Not FoundResource does not exist in DB
409ConflictDuplicate (email, key), invalid state transition, slot full
410GoneToken expired or already consumed (access_tokens)
422Unprocessable EntityValidation failure — field-level error with details
429Too Many RequestsRate limit exceeded (auth routes)
503Service Unavailablechatbot_enabled=0, or database lock timeout
500Internal Server ErrorUnhandled exception — should never reach client in prod
## D
## Input Validation Rules
Per-module field rules
ModuleFieldRuleError
Auth — RegisteremailValid format, unique in users
table
## 422 / 409
Auth — RegisterpasswordMin 8 characters422
## Auth — Reset
## Password
passwordMin 8 chars; confirm must
match
## 422
Users — CreateroleENUM: admin|agent|customer422
Users — CreateemailValid format, unique422 / 409
Agent — Updatecommission_rateDECIMAL 0.00–100.00422
Vehicles — CreatepriceDECIMAL > 0422
Vehicles — CreatestatusENUM: available|reserved|disco
ntinued|delivered
## 422
Vehicles — Createspecs_jsonValid JSON string or NULL422
Vehicles — Createsupplier_idMust exist in suppliers table404
Sales — Createselling_priceDECIMAL > 0422
Sales — Createpayment_typeENUM: cash|installment422
Sales — Create (loan)loan_amountDECIMAL > 0, <= selling_price422
Sales — Create (loan)term_monthsINT 6–60422
Sales — Create (loan)interest_rateDECIMAL 0.0–30.0422

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 35
ModuleFieldRuleError
Payments — Recordamount_paidDECIMAL > 0422
Payments — Recordpayment_methodENUM:
cash|bank_transfer|check|online
## 422
Service SlotscapacityINT > 0422
Warranty — Submitissue_descriptionNot empty, max 1000 chars422
Settings — Updatesetting_valueNot null or empty422
Suppliers — CreateemailValid format422
Inquiries — Guestguest_emailValid format422
Inquiries — Guestguest_nameNot empty, max 100 chars422

AUTOMATIKFlask API Flow — v2 Final (Panelist Resolved)
## 36
## E
## Panelist Resolution Checklist
Verification that all 10 critique items are addressed
#Critique ItemStatusLocation in Document
1HTTP status codes on every endpointRESOLVEDAll endpoint tables now include HTTP column with success + error codes
2Input validation rulesRESOLVEDAppendix D: full per-field rule table. §2 validator helper code.
3FOR UPDATE lock timeout handlingRESOLVED§3 vehicle transition, §10 slot booking — catch OperationalError → 503
4Amortization recompute remaining balance bugRESOLVED§6: recompute_amortization() uses remaining_balance + start_period params
5Flask session security configRESOLVEDAppendix B.1: HTTPONLY, SECURE, SAMESITE, SECRET_KEY rotation policy
6File storage strategyRESOLVED§12: S3-compatible storage, orphan cleanup cron, local dev fallback
7intent_tag taxonomyRESOLVED§4: 10-value ENUM table + unclassified fallback + sanitisation code
8Notification channel matrixRESOLVED§14: per-event channel table (in_app / email / SMS) + delivery note
9MySQLConnectionPoolRESOLVEDAppendix B.3: pool setup code, sizing guidance, teardown registration
10CSRF protectionRESOLVEDAppendix B.2: Flask-WTF setup, exempt pattern for JSON API routes
BONUSTechnology justification sectionADDEDAppendix A: Flask vs Django vs FastAPI, MySQL vs PostgreSQL decision table
AUTOMATIK — Flask API Flow Document v2 Final · Python Flask + mysql-connector-python + Session Auth · All Panelist Critiques Resolved