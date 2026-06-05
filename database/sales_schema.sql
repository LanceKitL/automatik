-- Sales Module Schema
-- Run this AFTER the base schema (users, vehicles, etc.)

-- Sales
CREATE TABLE IF NOT EXISTS sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT NOT NULL,
    customer_id INT NOT NULL,
    agent_id INT NULL,
    payment_type ENUM('cash', 'installment') NOT NULL,
    selling_price DECIMAL(12, 2) NOT NULL,
<<<<<<< HEAD
    status ENUM('pending', 'completed', 'cancelled') DEFAULT 'pending',
=======
    status ENUM('pending', 'active', 'completed', 'cancelled') DEFAULT 'pending',
>>>>>>> 7814b6bb5884f40f3aed5c4c24d32be40cc3482d
    sale_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE RESTRICT,
    FOREIGN KEY (customer_id) REFERENCES users(user_id) ON DELETE RESTRICT,
    FOREIGN KEY (agent_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- Sales Contracts
CREATE TABLE IF NOT EXISTS sales_contracts (
    contract_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL UNIQUE,
    status ENUM('draft', 'signed') DEFAULT 'draft',
    signed_at DATETIME NULL,
    reviewed_by INT NULL,
    FOREIGN KEY (sale_id) REFERENCES sales(sale_id) ON DELETE CASCADE,
    FOREIGN KEY (reviewed_by) REFERENCES users(user_id) ON DELETE SET NULL
);

-- Loan Details
CREATE TABLE IF NOT EXISTS loan_details (
    loan_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL UNIQUE,
<<<<<<< HEAD
=======
    down_payment DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
>>>>>>> 7814b6bb5884f40f3aed5c4c24d32be40cc3482d
    loan_amount DECIMAL(12, 2) NOT NULL,
    interest_rate DECIMAL(5, 2) NOT NULL,
    term_months INT NOT NULL,
    monthly_amortization DECIMAL(12, 2) NULL,
<<<<<<< HEAD
    bank_approval_status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
=======
    bank_name VARCHAR(100) DEFAULT 'automatik_financing',
    bank_approval_status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
>>>>>>> 7814b6bb5884f40f3aed5c4c24d32be40cc3482d
    FOREIGN KEY (sale_id) REFERENCES sales(sale_id) ON DELETE CASCADE
);

-- Amortization Schedule
CREATE TABLE IF NOT EXISTS amortization_schedule (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    loan_id INT NOT NULL,
<<<<<<< HEAD
    period_number INT NOT NULL,
    due_date DATE NOT NULL,
    amount_due DECIMAL(12, 2) NOT NULL,
    principal_component DECIMAL(12, 2) NOT NULL,
    interest_component DECIMAL(12, 2) NOT NULL,
    remaining_balance DECIMAL(12, 2) NOT NULL,
    status ENUM('unpaid', 'paid', 'overdue') DEFAULT 'unpaid',
    FOREIGN KEY (loan_id) REFERENCES loan_details(loan_id) ON DELETE CASCADE
);
=======
    month_number INT NOT NULL,
    due_date DATE NOT NULL,
    principal DECIMAL(12, 2) NOT NULL,
    interest DECIMAL(12, 2) NOT NULL,
    total_due DECIMAL(12, 2) NOT NULL,
    running_balance DECIMAL(12, 2) NOT NULL,
    status ENUM('unpaid', 'paid', 'overdue') DEFAULT 'unpaid',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (loan_id) REFERENCES loan_details(loan_id) ON DELETE CASCADE,
    UNIQUE KEY uq_loan_month (loan_id, month_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
>>>>>>> 7814b6bb5884f40f3aed5c4c24d32be40cc3482d

-- Payments
CREATE TABLE IF NOT EXISTS payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    schedule_id INT NULL,
    amount_paid DECIMAL(12, 2) NOT NULL,
<<<<<<< HEAD
    payment_method ENUM('cash', 'bank_transfer', 'credit_card', 'cheque') NOT NULL,
=======
    payment_method ENUM('cash', 'bank_transfer', 'check', 'online') NOT NULL,
>>>>>>> 7814b6bb5884f40f3aed5c4c24d32be40cc3482d
    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    recorded_by INT NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES sales(sale_id) ON DELETE RESTRICT,
    FOREIGN KEY (schedule_id) REFERENCES amortization_schedule(schedule_id) ON DELETE SET NULL,
    FOREIGN KEY (recorded_by) REFERENCES users(user_id) ON DELETE RESTRICT
);

-- Insurance Records
CREATE TABLE IF NOT EXISTS insurance_records (
    insurance_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    provider VARCHAR(100) NOT NULL,
    policy_number VARCHAR(50) NOT NULL,
    coverage_start DATE NOT NULL,
    coverage_end DATE NOT NULL,
    status ENUM('active', 'expired', 'cancelled') DEFAULT 'active',
    FOREIGN KEY (sale_id) REFERENCES sales(sale_id) ON DELETE CASCADE
);

-- Agent Commissions
CREATE TABLE IF NOT EXISTS agent_commissions (
    commission_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    agent_id INT NOT NULL,
<<<<<<< HEAD
    amount DECIMAL(10, 2) NOT NULL,
    commission_rate DECIMAL(5, 2) NOT NULL,
    is_paid TINYINT(1) DEFAULT 0,
    paid_at DATETIME NULL,
    FOREIGN KEY (sale_id) REFERENCES sales(sale_id) ON DELETE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES users(user_id) ON DELETE RESTRICT
);
=======
    rate_applied DECIMAL(5, 2) NOT NULL,
    commission_amount DECIMAL(10, 2) NOT NULL,
    is_paid TINYINT(1) NOT NULL DEFAULT 0,
    paid_at TIMESTAMP NULL DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sale_id) REFERENCES sales(sale_id) ON DELETE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES agent_details(user_id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
>>>>>>> 7814b6bb5884f40f3aed5c4c24d32be40cc3482d
