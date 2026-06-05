# Testing Guideline — Sales Module

## Prerequisites

1. **Run the schema migration**
   ```
   mysql -u <user> -p <database> < database/sales_schema.sql
   ```
   This creates: `sales`, `sales_contracts`, `loan_details`, `amortization_schedule`, `payments`, `insurance_records`, `agent_commissions`.

2. **Seed reference data** — ensure at least one `vehicles`, `users` (customer role), and `users` (agent role) exist before creating a sale.

3. **Authentication** — all admin routes require a logged-in user with `role = 'admin'`. Obtain a Session Token via `POST /auth/login` and pass it as:
   ```
   Authorization: Bearer <token>
   ```

4. **Email testing (optional)** — set `MAIL_*` env vars or use Mailtrap to capture outgoing emails without sending to real inboxes.

---

## 1. Sales CRUD

### `POST /admin/sales` — Create a sale (8-step transaction)

**Roles:** admin

**Request:**
```json
{
  "vehicle_id": 1,
  "customer_id": 3,
  "agent_id": 2,
  "payment_type": "cash",
  "selling_price": 750000.00
}
```

**For installment (creates loan + amortization schedule automatically):**
```json
{
  "vehicle_id": 1,
  "customer_id": 3,
  "agent_id": 2,
  "payment_type": "installment",
  "selling_price": 750000.00,
  "loan_amount": 600000.00,
  "term_months": 12,
  "interest_rate": 8.5
}
```

**Expected: `201 Created`**
```json
{
  "message": "Sale created successfully!",
  "payload": { "sale_id": 1 },
  "status": 201
}
```

**Verification:**
- Row inserted in `sales` with status `pending`
- Vehicle status updated to `sold`
- Commission row created in `agent_commissions` (if `agent_id` provided)
- In-app notification fired to customer + agent
- Email sent to customer + agent (if `MAIL_*` configured)

**Errors:**
| Status | Condition |
|--------|-----------|
| 400 | Missing required field (`vehicle_id`, `customer_id`, `payment_type`, `selling_price`) |
| 400 | Invalid `payment_type` (must be `"cash"` or `"installment"`) |
| 400 | Missing `loan_amount`/`term_months`/`interest_rate` when `payment_type == "installment"` |
| 400 | Vehicle already sold |
| 404 | Vehicle / Customer / Agent not found |
| 500 | DB error (transaction rolled back) |

---

### `GET /admin/sales` — List all sales

**Roles:** admin

**Expected: `200 OK`**
```json
{
  "message": "Sales retrieved successfully!",
  "payload": [
    {
      "id": 1,
      "vehicle_id": 1,
      "customer_id": 3,
      "agent_id": 2,
      "payment_type": "cash",
      "selling_price": 750000.0,
      "status": "pending",
      "created_at": "2026-06-03T10:00:00"
    }
  ],
  "status": 200
}
```

---

### `GET /admin/sales/<sale_id>` — Get single sale

**Roles:** admin

**Expected: `200 OK`** — same shape as above, single object in `payload`.

**Errors:**
| Status | Condition |
|--------|-----------|
| 404 | Sale not found |

---

### `PUT /admin/sales/<sale_id>/status` — Update sale status

**Roles:** admin

**Request:**
```json
{
  "status": "confirmed"
}
```

Valid statuses: `"confirmed"`, `"cancelled"`, `"completed"`.

**Expected: `200 OK`**
```json
{
  "message": "Sale status updated successfully!",
  "payload": { "sale_id": 1, "status": "confirmed" },
  "status": 200
}
```

**Errors:**
| Status | Condition |
|--------|-----------|
| 400 | Missing or invalid `status` |
| 404 | Sale not found |

---

### `GET /sales/my` — Current customer's sales

**Roles:** logged_in

Returns only sales where `customer_id` matches the logged-in user.

**Expected: `200 OK`**
```json
{
  "message": "My sales retrieved successfully!",
  "payload": [ ... ],
  "status": 200
}
```

### `GET /sales/my/<sale_id>` — Customer's single sale

**Roles:** logged_in

**Errors:**
| Status | Condition |
|--------|-----------|
| 403 | Sale does not belong to this customer |
| 404 | Sale not found |

---

## 2. Contracts

### `POST /admin/sales/<sale_id>/contract` — Create contract

**Roles:** admin

**Request body:** None (contract is built from sale data automatically).

**Expected: `201 Created`**
```json
{
  "message": "Contract created successfully!",
  "payload": { "contract_id": 1, "status": "draft" },
  "status": 201
}
```

**Verification:** Row inserted in `sales_contracts` with `status = 'draft'`.

**Errors:**
| Status | Condition |
|--------|-----------|
| 400 | Contract already exists for this sale |
| 404 | Sale not found |

---

### `GET /admin/sales/<sale_id>/contract` — Get contract

**Roles:** admin, agent

**Expected: `200 OK`**
```json
{
  "message": "Contract retrieved successfully!",
  "payload": {
    "id": 1,
    "sale_id": 1,
    "contract_ref": "CTR-20260603-0001",
    "status": "draft",
    "created_at": "2026-06-03T10:00:00"
  },
  "status": 200
}
```

**Errors:**
| Status | Condition |
|--------|-----------|
| 404 | Contract not found |

---

### `PUT /admin/sales/<sale_id>/contract/sign` — Sign contract

**Roles:** admin

**Request body:** None.

**Expected: `200 OK`**
```json
{
  "message": "Contract signed successfully!",
  "payload": { "contract_id": 1, "signed_at": "2026-06-03T10:05:00" },
  "status": 200
}
```

**Verification:** `status` → `"signed"`, `signed_at` populated.

**Errors:**
| Status | Condition |
|--------|-----------|
| 404 | Sale or contract not found |

---

## 3. Insurance

### `POST /admin/sales/<sale_id>/insurance` — Attach insurance

**Roles:** admin

**Request:**
```json
{
  "provider": "Prudential Guarantee",
  "policy_number": "POL-2026-001",
  "coverage_start": "2026-06-03",
  "coverage_end": "2027-06-02"
}
```

**Expected: `201 Created`**
```json
{
  "message": "Insurance added successfully!",
  "payload": { "insurance_id": 1 },
  "status": 201
}
```

**Errors:**
| Status | Condition |
|--------|-----------|
| 400 | Missing required field |
| 404 | Sale not found |

---

### `GET /admin/insurance` — List all insurance

**Roles:** admin

**Expected: `200 OK`** — array of insurance records in `payload`.

---

### `PUT /admin/insurance/<insurance_id>` — Update insurance

**Roles:** admin

**Request (all fields optional, at least one required):**
```json
{
  "status": "active"
}
```
Valid statuses: `"active"`, `"expired"`, `"cancelled"`.

**Expected: `200 OK`**

**Errors:**
| Status | Condition |
|--------|-----------|
| 400 | No fields provided or invalid `status` |
| 404 | Insurance not found |

---

## 4. Loans & Amortization

### `POST /admin/sales/<sale_id>/loan` — Create loan

**Roles:** admin

**Request:**
```json
{
  "loan_amount": 600000.00,
  "interest_rate": 8.5,
  "term_months": 12
}
```

**Expected: `201 Created`**
```json
{
  "message": "Loan created with amortization schedule!",
  "payload": { "loan_id": 1, "schedule_entries": 12 },
  "status": 201
}
```

**Verification:**
- Row inserted in `loan_details` with `status = 'active'`
- `term_months` rows inserted in `amortization_schedule` with auto-calculated `principal_component`, `interest_component`, `total_due`
- In-app notification sent to customer
- Email sent to customer (if `MAIL_*` configured)

**Errors:**
| Status | Condition |
|--------|-----------|
| 400 | Missing required field |
| 400 | Loan already exists for this sale |
| 400 | Invalid `term_months` (must be positive integer) |
| 404 | Sale not found |

---

### `GET /admin/loans` — List all loans

### `GET /admin/loans/<loan_id>` — Get single loan

### `GET /loans/my` — Customer's loans

### `GET /admin/loans/<loan_id>/schedule` — Get amortization schedule

**Expected: `200 OK`**
```json
{
  "message": "Schedule retrieved successfully!",
  "payload": [
    {
      "id": 1,
      "loan_id": 1,
      "period": 1,
      "due_date": "2026-07-03",
      "total_due": 54388.81,
      "principal_component": 49888.81,
      "interest_component": 4500.00,
      "remaining_balance": 550111.19,
      "status": "pending"
    }
  ],
  "status": 200
}
```

---

### `PUT /admin/loans/<loan_id>` — Update loan status (bank approval)

**Roles:** admin

**Request:**
```json
{
  "bank_approval_status": "approved"
}
```
Valid values: `"approved"`, `"rejected"`.

**Expected: `200 OK`**

**Verification:**
- `bank_approval_status` updated
- In-app notification + email sent to customer

**Errors:**
| Status | Condition |
|--------|-----------|
| 400 | Missing or invalid `bank_approval_status` |
| 404 | Loan not found |

---

### `PUT /admin/amortization/<schedule_id>/status` — Update schedule status

**Roles:** admin

**Request:**
```json
{
  "status": "overdue"
}
```
Valid values: `"paid"`, `"overdue"`.

**Expected: `200 OK`**

**Errors:**
| Status | Condition |
|--------|-----------|
| 400 | Missing or invalid `status` |
| 404 | Schedule entry not found |

---

### `GET /admin/amortization/overdue` — List overdue schedules

**Roles:** admin

Returns all amortization entries with `status = 'overdue'`.

**Expected: `200 OK`**
```json
{
  "message": "Overdue amortizations retrieved successfully!",
  "payload": [ ... ],
  "status": 200
}
```

---

### `POST /admin/loans/<loan_id>/compute` — Recompute amortization

**Roles:** admin

Used after partial prepayments or interest rate changes. Paid periods are preserved; remaining balance is derived from `SUM(principal_component)` of unpaid periods.

**Request:**
```json
{
  "interest_rate": 7.5,
  "term_months": 10
}
```

**Expected: `200 OK`**
```json
{
  "message": "Amortization recomputed successfully!",
  "payload": { "schedule_entries": 10 },
  "status": 200
}
```

**Verification:**
- Old unpaid schedule entries deleted
- New schedule generated with updated `interest_rate` and `term_months`
- Paid periods preserved

**Errors:**
| Status | Condition |
|--------|-----------|
| 400 | Missing required field |
| 404 | Loan not found |

---

## 5. Payments

### `POST /admin/sales/<sale_id>/payments` — Record payment

**Roles:** admin

5-step cascade:
1. Validate sale exists
2. Create payment record
3. Fetch unpaid amortization entry (earliest if `schedule_id` omitted)
4. Mark amortization as `paid`
5. Fire notification + email

**Request:**
```json
{
  "amount_paid": 54388.81,
  "payment_method": "bank_transfer",
  "schedule_id": 1
}
```
- `schedule_id` is optional — if omitted, the earliest unpaid schedule is auto-selected.
- `payment_method` valid values: `"cash"`, `"bank_transfer"`, `"credit_card"`, `"cheque"`.

**Expected: `201 Created`**
```json
{
  "message": "Payment recorded successfully!",
  "payload": { "payment_id": 1, "schedule_id": 1, "status": "paid" },
  "status": 201
}
```

**Errors:**
| Status | Condition |
|--------|-----------|
| 400 | Missing required field or invalid `payment_method` |
| 400 | No unpaid schedules found for this sale |
| 400 | Specified `schedule_id` is already paid |
| 404 | Sale not found |

---

### `GET /admin/payments` — List all payments

### `GET /admin/payments/<payment_id>` — Get single payment

### `GET /admin/sales/<sale_id>/payments` — Get payments for a sale

### `GET /payments/my` — Customer's payments

### `GET /admin/payments/summary` — Payment summary

**Expected: `200 OK`**
```json
{
  "message": "Payment summary retrieved successfully!",
  "payload": {
    "total_collected": 54388.81,
    "cash": 0,
    "bank_transfer": 54388.81,
    "credit_card": 0,
    "cheque": 0
  },
  "status": 200
}
```

---

## 6. End-to-End Test Scenario: Installment Sale

```
Step 1: POST /admin/sales
        { "vehicle_id": 1, "customer_id": 3, "agent_id": 2,
          "payment_type": "installment", "selling_price": 750000,
          "loan_amount": 600000, "term_months": 12, "interest_rate": 8.5 }
        → 201, sale_id=1

Step 2: PUT /admin/sales/1/status
        { "status": "confirmed" }
        → 200

Step 3: POST /admin/sales/1/contract
        (no body) → 201, contract_id=1

Step 4: PUT /admin/sales/1/contract/sign
        (no body) → 200, signed_at=...

Step 5: GET /admin/sales/1/contract
        → Verify contract_ref, status="signed"

Step 6: POST /admin/sales/1/insurance
        { "provider": "Prudential", "policy_number": "POL-001",
          "coverage_start": "2026-06-03", "coverage_end": "2027-06-02" }
        → 201, insurance_id=1

Step 7: POST /admin/sales/1/loan
        { "loan_amount": 600000, "interest_rate": 8.5, "term_months": 12 }
        → 201, loan_id=1, schedule_entries=12

Step 8: GET /admin/loans/1/schedule
        → Verify 12 rows, first due_date = next month

Step 9: PUT /admin/loans/1
        { "bank_approval_status": "approved" }
        → 200 (notification + email sent)

Step 10: POST /admin/sales/1/payments
         { "amount_paid": 54388.81, "payment_method": "bank_transfer" }
         → 201, schedule_id=1 marked paid

Step 11: GET /admin/sales/1/payments
         → Verify payment record exists
```

## 7. cURL Templates

### Auth header
```bash
TOKEN="<your-jwt-token>"
AUTH="Authorization: Bearer $TOKEN"
```

### Create sale (cash)
```bash
curl -X POST http://localhost:5000/admin/sales \
  -H "$AUTH" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": 1,
    "customer_id": 3,
    "payment_type": "cash",
    "selling_price": 750000.00
  }'
```

### Create sale (installment)
```bash
curl -X POST http://localhost:5000/admin/sales \
  -H "$AUTH" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": 1,
    "customer_id": 3,
    "agent_id": 2,
    "payment_type": "installment",
    "selling_price": 750000.00,
    "loan_amount": 600000.00,
    "term_months": 12,
    "interest_rate": 8.5
  }'
```

### Update sale status
```bash
curl -X PUT http://localhost:5000/admin/sales/1/status \
  -H "$AUTH" \
  -H "Content-Type: application/json" \
  -d '{"status": "confirmed"}'
```

### Contract
```bash
curl -X POST http://localhost:5000/admin/sales/1/contract -H "$AUTH"
curl -X PUT http://localhost:5000/admin/sales/1/contract/sign -H "$AUTH"
```

### Insurance
```bash
curl -X POST http://localhost:5000/admin/sales/1/insurance \
  -H "$AUTH" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "Prudential",
    "policy_number": "POL-001",
    "coverage_start": "2026-06-03",
    "coverage_end": "2027-06-02"
  }'
```

### Loan
```bash
curl -X POST http://localhost:5000/admin/sales/1/loan \
  -H "$AUTH" \
  -H "Content-Type: application/json" \
  -d '{"loan_amount": 600000, "interest_rate": 8.5, "term_months": 12}'

curl -X PUT http://localhost:5000/admin/loans/1 \
  -H "$AUTH" \
  -H "Content-Type: application/json" \
  -d '{"bank_approval_status": "approved"}'
```

### Payment
```bash
curl -X POST http://localhost:5000/admin/sales/1/payments \
  -H "$AUTH" \
  -H "Content-Type: application/json" \
  -d '{"amount_paid": 54388.81, "payment_method": "bank_transfer"}'
```

### Customer endpoints (same token with customer role)
```bash
curl http://localhost:5000/sales/my -H "$AUTH"
curl http://localhost:5000/loans/my -H "$AUTH"
curl http://localhost:5000/payments/my -H "$AUTH"
```
