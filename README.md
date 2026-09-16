# AutoMatik

**Integrated Web-Based Car Dealership and Management System**
Polytechnic University of the Philippines — College of Computer and Information Sciences
Capstone Project, A.Y. 2025–2026

---

## Table of Contents

1. [Overview](#overview)
2. [Core Features](#core-features)
3. [User Roles](#user-roles)
4. [Tech Stack](#tech-stack)
5. [System Architecture](#system-architecture)
6. [Database](#database)
7. [Prerequisites](#prerequisites)
8. [Setup](#setup)
9. [Environment Variables](#environment-variables)
10. [Project Structure](#project-structure)
11. [API Overview](#api-overview)
12. [Git Workflow](#git-workflow)
13. [Team](#team)
14. [Project Constraints](#project-constraints)
15. [License](#license)

---

## Overview

AutoMatik is a full-stack web application for single-branch car dealership operations. It replaces manual, paper-based workflows with a unified system that lets customers browse inventory and book services, lets sales agents manage inquiries and commissions, and lets administrators oversee inventory, transactions, and staff records — all without requiring a dealership visit for routine interactions.

---

## Core Features

- **Vehicle Inventory Management** — car listings with brand, model, year, price, specs, and photos; status lifecycle (`available` → `reserved` → `delivered`/`discontinued`)
- **Inquiries** — an online inquiry form for guests and customers, routed to available sales agents, with an AI chatbot for quick responses and query redirection
- **Service Bookings** — test drive and maintenance/repair appointments against a slot-based availability system
- **Document Processing** — Official Receipts, Certificates of Registration, Sales Contracts, and Customer Records, accessible via the Customer Portal
- **Warranty Claims** — customer-submitted claims tied to a purchased vehicle, reviewed and resolved by admins
- **Insurance Records** — per-vehicle insurance policies linked to a sale
- **Purchase & Financing** — cash or installment payments, with auto-generated amortization schedules and a standalone payment calculator
- **Sales & Commissions** — sales recorded per agent, with fixed-rate commission computation and payout tracking
- **Supplier & Supplies Management** — tracking of parts/materials suppliers and stock levels, with low-stock alerts
- **Notifications** — automated alerts to customers and dealers on key events (new inquiry, payment received, amortization due, etc.)
- **Audit Logging** — change history (old/new value diffs) on critical tables for accountability

---

## User Roles

| Role | Access |
|---|---|
| **Guest / Public** | Browse vehicles, submit inquiries, view available service slots |
| **Customer** | Portal access (granted after first purchase) — sales, payments, amortization, documents, warranty claims, bookings, notifications |
| **Sales Agent** | Assigned inquiries, tasks, commissions, sales performance |
| **Administrator** | Full system management — inventory, sales, financing, documents, suppliers, users, settings, audit logs |

---

## Tech Stack

**Backend**
- Python / Flask (application factory pattern)
- PeeWee ORM
- MySQL 8.0, via `mysql-connector-python`
- Session-based auth (Flask signed cookies), role-based access control via decorators (`@login_required`, `@role_required`)

**Frontend**
- React
- Vite
- Tailwind CSS

**Tooling**
- Git / GitHub (feature branches → `develop`)
- Postman / curl / pytest for API testing

---

## System Architecture

AutoMatik is organized around 8 logical modules, backed by 26 relational tables:

1. **Authentication & Users** — accounts, tokens, profiles, agent/customer detail records
2. **Inventory** — vehicles, vehicle photos, suppliers, supplies
3. **Inquiries & Chatbot** — inquiries, chatbot logs, agent tasks
4. **Sales & Contracts** — sales, sales contracts, documents, insurance records
5. **Financing** — loan details, amortization schedules
6. **Payments** — payment records tied to sales/schedules
7. **Service & Warranty** — service slots, service bookings, warranty claims
8. **System** — notifications, system settings, audit logs

Authentication uses server-side Flask sessions (not JWT) with `session['user_id']` and `session['role']`; access control is enforced via stackable route decorators. Customers do not self-register — portal access is issued via a token after a completed purchase, and the customer sets a permanent password on first login.

---

## Database

- **26 tables** across the 8 modules above
- Key relationship examples:
  - `sales` joins `vehicles`, `customer_details`, and `agent_details` for full transaction context
  - `loan_details` → `amortization_schedule` → `payments` for the financing lifecycle
  - `inquiries` → `agent_tasks` for agent follow-up work
  - `warranty_claims` → `service_bookings` for approved repair claims
- Schema DDL lives in `schema/automatik_schema.sql`

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Git

---

## Setup

### 1. Clone

```bash
git clone https://github.com/LanceKitL/automatik.git
cd automatik
```

### 2. Database

```bash
mysql -u root -p
```

```sql
CREATE DATABASE automatik CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

```bash
mysql -u root -p automatik < schema/automatik_schema.sql
```

### 3. Backend

```bash
cd backend
python -m venv venv
```

Activate the virtual environment:

```bash
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt. Then install dependencies:

```bash
pip install -r requirements.txt
```

Create `backend/.env` (see [Environment Variables](#environment-variables)), then run:

```bash
python run.py
```

Backend runs at `http://localhost:5000`.

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

> Frontend is under active development.

---

## Environment Variables

`backend/.env`:

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
DB_HOST=localhost
DB_PORT=3306
DB_NAME=automatik
DB_USER=root
DB_PASSWORD=your-password
```

| Variable | Description |
|---|---|
| `FLASK_ENV` | `development` or `production` |
| `SECRET_KEY` | Used to sign session cookies |
| `DB_HOST` / `DB_PORT` | MySQL connection host and port |
| `DB_NAME` | Database name (`automatik`) |
| `DB_USER` / `DB_PASSWORD` | MySQL credentials |

---

## Project Structure

```
automatik/
├── backend/
│   ├── app/                 # Flask app factory, blueprints, models
│   ├── requirements.txt
│   ├── run.py
│   └── .env
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── schema/
│   └── automatik_schema.sql
└── README.md
```

---

## API Overview

The API is organized into the following route groups (see the full API flow document for endpoint-level detail):

| # | Module | Example Endpoints |
|---|---|---|
| 1 | Auth & Sessions | `/auth/register`, `/auth/login`, `/auth/me` |
| 2 | Users & Profiles | `/admin/users`, `/profile`, `/admin/agents` |
| 3 | Vehicles & Inventory | `/vehicles`, `/admin/vehicles/<id>` |
| 4 | Inquiries & Chatbot | `/inquiries`, `/chatbot/message` |
| 5 | Sales & Contracts | `/admin/sales`, `/admin/sales/<id>/contract` |
| 6 | Financing | `/admin/loans`, `/admin/loans/<id>/schedule` |
| 7 | Payments | `/admin/sales/<id>/payments`, `/payments/my` |
| 8 | Agent Module | `/agent/dashboard`, `/agent/commissions` |
| 9 | Customer Portal | `/portal/dashboard`, `/portal/documents` |
| 10 | Service Bookings | `/service/slots`, `/service/bookings` |
| 11 | Warranty Claims | `/warranty`, `/admin/warranty/<id>/approve` |
| 12 | Documents | `/admin/documents`, `/portal/documents/<id>` |
| 13 | Suppliers & Supplies | `/admin/suppliers`, `/admin/supplies/low-stock` |
| 14 | Notifications | `/notifications`, `/notifications/read-all` |
| 15 | Audit Logs | `/admin/audit-logs` |
| 16 | System Settings | `/admin/settings` |

Roughly 80 endpoints in total, split across Public, Customer, Agent, and Admin access levels.

---

## Git Workflow

- Feature branches merge into `develop` via pull request
- No direct pushes to `main`
- Open a PR early for visibility across the team

---

## Team

**System Analysts**
- Sean Marcus Cruzado (Lead)
- Joseph Mari Quinto
- Israel Arold Salino
- Jaffy Salvador
- Scott Lance Sanclaria

**Database Developers**
- Justin Rain Abucay (Lead)
- Xavier Kim Decatoria
- Marwin Sapo-an
- Stephen Lance Tercino
- Ahrold Johnrie Buen
- Mhigz Justine Tupaz

**Development & Data Compliance**
- Alfonso — Flask / Authentication
- Oraba — ORM
- Pabica — Data Analysis Lead, Data Compliance Lead
- Banela, Sarmiento — Data Compliance
- Alavazo, Alba, Lim, Mendoza — UI/UX

*Project team totals roughly 45 members across analysis, development, compliance, and design workstreams.*

---

## Project Constraints

- The dealership modeled is **single-branch only**
- AI-generated content/code is capped at **15%** of the project, enforced by the academic panel

---

## License

Academic capstone project — Polytechnic University of the Philippines, College of Computer and Information Sciences. Not licensed for external distribution unless stated otherwise by the team.
