# AutoMatik Dealership Management System

## Overview
AutoMatik is a full-stack dealership management platform. It handles vehicle inventory, sales, financing, service bookings, warranty claims, agent commissions, customer portal, and staff dashboards.

## Tech Stack
- **Backend**: Flask (Python 3.14), session-based auth, mysql-connector-python
- **Frontend**: Svelte 5 (runes mode) with SvelteKit, Lucide icons
- **Database**: MySQL 5.7+ (27 tables)
- **Email**: Flask-Mail with Jinja2 HTML templates (15 templates)
- **Real-time**: Flask-SocketIO
- **AI Chatbot**: NVIDIA AI via langchain_nvidia_ai_endpoints (minimaxai/minimax-m3)

---

## User Roles & Capabilities

### `admin` — System administrator
Full access to everything: user management, vehicle inventory, sales, payments, commissions, service bookings, warranty claims, settings, audit logs, notifications, suppliers, supplies, documents.

### `agent` — Salesperson
Dashboard with assigned inquiries, tasks, commissions. Can manage inquiries (self-assign, convert to sale, resolve), create tasks, manage test drives (assign, confirm, complete, cancel), view vehicle inventory, and list their commissions.

### `customer` — End customer
Portal access: view vehicles, submit inquiries, reserve vehicles, pay reservation fees, track payments, view amortization schedule, download documents, book/maintenance/repair/test-drive appointments, submit warranty claims, update profile.

### `finance_staff` — Finance & insurance
Manage loans (approve/reject/review), payments (verify/reject), insurance policies, overdue amortizations, and view dashboard KPIs (pending reviews, total financed, delinquency rate).

### `service_advisor` — Service department lead
Dashboard, manage all service bookings, create estimates, transmit estimates to customers, assign bookings to technicians, update booking statuses, manage warranty claims.

### `service_staff` — Service technician
Dashboard, view/cancel bookings, create maintenance bookings, update technician notes, review/approve/reject/resolve warranty claims. Shares most endpoints with service_advisor.

### Guest / Public (no login)
Browse vehicles, submit inquiries, reserve vehicles, pay reservation fees, book test drives, submit contact form, use chatbot.

---

## Database Tables (27 tables)

### Users & Auth
- **users** — user_id, username, hashed_password, email, role (admin/agent/customer/finance_staff/service_advisor), email_verified, is_active, last_login
- **user_profile** — user_id, full_name, phone_number, address, city, province, zip_code, date_of_birth, gender
- **access_tokens** — token_id, user_id, token_hash, token_type (portal_access/email_verify/password_reset), expires_at, used_at
- **agent_details** — user_id, employee_number, hire_date, default_commission_rate
- **customer_details** — user_id, customer_number, preferred_contact_method, preferred_payment_method, notes

### Inventory
- **vehicles** — vehicle_id, supplier_id, vin, brand, model, year, color, body_type, seating_capacity, transmission (manual/automatic), fuel_type (gasoline/diesel/electric/hybrid), price, status (available/reserved/discontinued/delivered), specs_json
- **vehicle_photos** — photo_id, vehicle_id, photo_url, sort_order
- **suppliers** — supplier_id, company_name, contact_name, contact_email, contact_phone, address, is_active
- **supplies** — supply_id, supplier_id, part_name, part_number, unit_cost, stock_qty, reorder_level

### Sales & Finance
- **sales** — sale_id, vehicle_id, customer_id, agent_id, inquiry_id, selling_price, payment_type (full_payment/installment), sale_date, status (pending/active/completed/cancelled)
- **sales_contracts** — contract_id, sale_id, contract_url, status (draft/pending_signature/signed/cancelled), signed_at, reviewed_by
- **loan_details** — loan_id, sale_id, down_payment, loan_amount, interest_rate, term_months, monthly_amortization, bank_name, bank_approval_status (pending/approved/rejected)
- **amortization_schedule** — schedule_id, loan_id, month_number, due_date, principal, interest, total_due, running_balance, status (unpaid/paid/overdue)
- **insurance_records** — insurance_id, vehicle_id, sale_id, customer_id, provider_name, policy_number, coverage_type, start_date, end_date, status (active/expired/cancelled)
- **payments** — payment_id, sale_id, schedule_id, amount_paid, payment_date, payment_method (cash/bank_transfer/check/online), reference, payment_allocation (service_fee/maintenance/repair/amortization/full_cash/downpayment/reservation_fee), proof_of_payment, recorded_by, review_status, notes
- **agent_commissions** — commission_id, sale_id, agent_id, rate_applied, commission_amount, is_paid, paid_at

### Service
- **service_slots** — slot_id, slot_datetime, slot_type (test_drive/maintenance/repair), capacity, is_available
- **service_bookings** — booking_id, customer_id, vehicle_id, slot_id, booking_type (test_drive/maintenance/repair), warranty_claim_id, notes, status (pending/confirmed/completed/cancelled/draft_estimate/awaiting_signature/in_progress/pending_supplement/ready_for_testing/ready_for_checkout), assigned_to, technician_notes, estimate_data
- **warranty_claims** — claim_id, sale_id, vehicle_id, claim_type (repair/replacement/refund), description, status (submitted/under_review/approved/rejected/resolved), reviewed_by, resolution

### Customer Relations
- **inquiries** — inquiry_id, user_id, agent_id, vehicle_id, guest_name, guest_email, guest_number, message, status (open/assigned/resolved/closed)

### System
- **documents** — document_id, sale_id, document_type (OR/CR/warranty_cert/amortization_schedule/sales_contract/other), file_url, is_accessible
- **notifications** — notification_id, user_id, title, message, channel (in_app/email/sms), ref_type, ref_id, is_read
- **system_settings** — setting_id, setting_key, setting_value, description
- **audit_logs** — log_id, user_id, action, table_name, record_id, old_value, new_value, ip_address
- **chatbot_logs** — log_id, session_id, user_id, inquiry_id, user_message, bot_response, intent_tag

---

## Frontend Routes

### Public (no login)
| Route | Page |
|-------|------|
| `/` | Landing page with hero carousel, search dock, featured vehicles |
| `/vehicles` | Browse all vehicles with filters (body, brand, color, year, seats, sort, search) |
| `/loan-calculator` | Amortization calculator with schedule table |
| `/about` | Company info, team, mission |
| `/contact` | Contact form + info cards |
| `/auth/login` | Login form |
| `/auth/forgot-password` | Password reset request |
| `/auth/reset-password` | Password reset with token |
| `/auth/how_to_get_an_account` | Instructions |

### Admin (`/admin`)
Dashboard, Users, Vehicles (inventory), Sales, Inquiries, Payments, Commissions, Loans, Service Bookings, Warranty Claims, Documents, Notifications, Audit Logs, Settings, Suppliers.

### Agent (`/agent`)
Dashboard, Inquiries, Tasks, Vehicles, Test Drives, Commissions, Sales.

### Finance (`/finance_staff`)
Dashboard, Loans (list/detail/review), Payments, Insurance, Amortization.

### Service Staff (`/service_staff`)
Dashboard, Repairs, Maintenance, History, Warranty Claims.

### Customer Portal (`/portal`)
Dashboard, Vehicles, My Vehicles, Inquiries, Payments, Amortization, Documents, Service, Appointments, Warranty Claims, Notifications, Profile.

---

## Key Business Logic

### Commission Calculation
When a sale is created with `payment_type = "full_payment"` and `status = "completed"`, the system calculates: `commission = selling_price * (agent_rate / 100)`. The agent's `default_commission_rate` (from `agent_details`) is used. A record is inserted into `agent_commissions` with `is_paid = 0`. Admins can mark commissions as paid via `PUT /admin/commissions/<id>/pay`.

### Amortization Schedule Generation
For installment sales, `generate_amortization_schedule()` creates monthly payment records using: `monthly_payment = principal * (rate/100/12) / (1 - (1 + rate/100/12)^-n)`. Each period's interest = running_balance * monthly_rate, principal = monthly_payment - interest. Records are stored in `amortization_schedule` with status "unpaid".

### Service Slot Auto-Generation
When listing slots, `_ensure_slots_exist()` checks if any maintenance/repair slots exist for the next 30 days. If not, it generates 3 slots per day (10:00, 14:00, 16:00) for Monday–Saturday. Test drive slots are created manually by staff.

### Inquiry-to-Sale Flow
1. Guest submits inquiry → stored in `inquiries` with status "open"
2. Agent self-assigns via `PUT /inquiries/self-assign/<id>`
3. Agent creates sale via `/admin/sales` linking to the inquiry
4. Inquiry status updated to "resolved" or "closed"

### Warranty Claim Lifecycle
submitted → under_review → approved/rejected → resolved. Approvals can trigger a service booking (warranty_claim_id FK). Rejections include resolution notes.

### Payment Verification Flow
Payments have `review_status` (pending_verification → verified/rejected). Finance staff reviews proof-of-payment images. Verified payments update `amortization_schedule.status = "paid"`.

---

## API Endpoints (Key Groups)

### Auth (`/auth`)
`POST /login`, `POST /logout`, `GET /me`, `PUT /changePassword`, `POST /forgot-password`, `POST /reset-password`

### Vehicles (`/vehicles`)
`GET /` (public listing), `POST /<id>/reserve` (guest), `POST /<id>/pay-reservation` (guest), `POST /contact`, `POST /chatbot`
Admin: `POST /create`, `PUT /update/<id>`, `DELETE /delete/<id>`, `PUT /update/status/<id>`

### Inquiries (`/inquiries`)
`POST /` (guest submit), `GET /` (list), `GET /my` (customer), `PUT /assign/<id>`, `PUT /self-assign/<id>`, `PUT /close/<id>`, `DELETE /<id>`, `PUT /convert-to-sale/<id>`, `PUT /resolve/<id>`

### Admin (`/admin`)
Dashboard, users CRUD, agents, customers, inventory, sales, payments, commissions, service bookings, warranty, documents, notifications, audit logs, settings, suppliers, supplies.

### Agent (`/agent`)
Dashboard, inquiries, tasks CRUD, vehicles, test drives CRUD, commissions.

### Customer Portal (`/portal`)
Dashboard, vehicles, inquiries, payments, amortization, documents, service bookings, warranty claims, profile.

### Finance Staff (`/finance_staff`)
Dashboard, loans CRUD, payments review, insurance CRUD, amortization overdue.

### Service (`/service`)
`GET /slots` (public), `GET /bookings/my` (customer), `POST /bookings` (create), `POST /bookings/guest`, `PUT /bookings/<id>/cancel`, `PUT /bookings/<id>/sign`, `PUT /bookings/<id>/acknowledge`

### Notifications (`/notifications`)
`GET /recent`, `GET /all`, `PUT /read/<id>`

---

## Email System

15 Jinja2 HTML templates in `templates/email/`:
- **Customer-facing (13)**: welcome, email_verification, submitInquiry, inquiry_assigned, reservation_fee, payment_receipt, sale_confirmation, booking_confirmed, test_drive_confirmed, loan_status, warranty_approved, warranty_rejected, password_reset
- **Staff notifications (2)**: new_inquiry, new_warranty_claim

All extend `templates/email/_base.html` (logo header, gold accent, white card, blue buttons, footer with address/phone/email).

Emails sent via Flask-Mail with threading (`@copy_current_request_context`) to avoid blocking API responses. Sender: "AutoMatik <AutoMatik@services.com>".

---

## Dealership Info
- **Address**: 123 AutoMall Drive, Makati City, Philippines
- **Phone**: +63 (2) 8123 4567
- **Email**: info@automatik.com
- **Hours**: Monday – Saturday, 8:00 AM – 6:00 PM (Closed Sundays)
- **Brands Sold**: BYD, Honda, Hyundai, Mitsubishi, Toyota
- **Financing**: In-house with competitive rates, minimum down payment, flexible terms
- **Inventory Statuses**: available, reserved, discontinued, delivered
