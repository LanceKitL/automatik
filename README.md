# AutoMatik
**Integrated Web-Based Car Dealership and Management System**
Polytechnic University of the Philippines | 2025–2026

---

AutoMatik is a full-stack web application for car dealership management. It serves four user roles — **Guest**, **Customer**, **Sales Agent**, and **Administrator** — covering vehicle inventory, sales processing, loan and amortization management, document generation, service bookings, warranty claims, and agent commission tracking.

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
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
DB_HOST=localhost
DB_PORT=3306
DB_NAME=automatik
DB_USER=root
DB_PASSWORD=your-password
```

```bash
python run.py
```

Runs at `http://localhost:5000`.

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

Backend runs at `http://localhost:5000`
Frontend runs at `http://localhost:5173`

`frontend is under development`

