-- phpMyAdmin SQL Dump -- version 5.2.1 -- https://www.phpmyadmin.net/
----------------------------------------------------------------------
-- Host: 127.0.0.1 -- Generation Time: May 06, 2026 at 04:30 PM -- Server version: 10.4.32-MariaDB -- PHP Version: 8.2.12

SET SQL\_MODE = "NO\_AUTO\_VALUE\_ON\_ZERO"; START TRANSACTION; SET time\_zone = "+00:00";

/\*!40101 SET @OLD\_CHARACTER\_SET\_CLIENT=@@CHARACTER\_SET\_CLIENT */; /*!40101 SET @OLD\_CHARACTER\_SET\_RESULTS=@@CHARACTER\_SET\_RESULTS */; /*!40101 SET @OLD\_COLLATION\_CONNECTION=@@COLLATION\_CONNECTION */; /*!40101 SET NAMES utf8mb4 \*/;
-- -- Database: `automatik`
---------------------------
-----
-- -- Table structure for table `access_tokens`
-----------------------------------------------
CREATE TABLE `access_tokens` ( `token_id` varchar(64) NOT NULL, `user_id` int(11) NOT NULL, `token_hash` varchar(255) NOT NULL, `token_type` enum('portal\_access','email\_verify','password\_reset') NOT NULL, `expires_at` timestamp NOT NULL DEFAULT current\_timestamp() ON UPDATE current\_timestamp(), `used_at` timestamp NULL DEFAULT NULL, `created_at` timestamp NOT NULL DEFAULT current\_timestamp() ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4\_unicode\_ci;

-----
-- -- Table structure for table `agent_commissions`
---------------------------------------------------
CREATE TABLE `agent_commissions` ( `commission_id` int(11) NOT NULL, `sale_id` int(11) NOT NULL, `agent_id` int(11) NOT NULL, `rate_applied` decimal(5,2) NOT NULL, `commission_amount` decimal(10,2) NOT NULL, `is_paid` tinyint(1) NOT NULL DEFAULT 0, `paid_at` timestamp NULL DEFAULT NULL, `created_at` timestamp NOT NULL DEFAULT current\_timestamp() ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4\_unicode\_ci;
-- -- Dumping data for table `agent_commissions`
------------------------------------------------
INSERT INTO `agent_commissions` (`commission_id`, `sale_id`, `agent_id`, `rate_applied`, `commission_amount`, `is_paid`, `paid_at`, `created_at`) VALUES (1, 1, 3, 3.00, 49440.00, 1, '2025-03-15 02:00:00', '2026-04-19 08:40:18'), (2, 2, 2, 3.50, 83650.00, 0, NULL, '2026-04-19 08:40:18');

-----
-- -- Table structure for table `agent_details`
-----------------------------------------------
CREATE TABLE `agent_details` ( `user_id` int(11) NOT NULL, `employee_number` varchar(20) NOT NULL, `hire_date` timestamp NOT NULL DEFAULT current\_timestamp() ON UPDATE current\_timestamp(), `default_commission_rate` decimal(5,2) NOT NULL DEFAULT 3.00 ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4\_unicode\_ci;
-- -- Dumping data for table `agent_details`
--------------------------------------------
INSERT INTO `agent_details` (`user_id`, `employee_number`, `hire_date`, `default_commission_rate`) VALUES (2, 'EMP-2024-001', '2024-01-15 00:00:00', 3.50), (3, 'EMP-2024-002', '2024-03-01 00:00:00', 3.00);

-----
-- -- Table structure for table `agent_tasks`
---------------------------------------------
CREATE TABLE `agent_tasks` ( `task_id` int(11) NOT NULL, `agent_id` int(11) NOT NULL, `inquiry_id` int(11) DEFAULT NULL, `task_type` enum('follow\_up','appointment','demo','document\_prep','other') NOT NULL, `title` varchar(200) NOT NULL, `due_date` timestamp NOT NULL DEFAULT current\_timestamp() ON UPDATE current\_timestamp(), `status` enum('pending','in\_progress','done','cancelled') NOT NULL DEFAULT 'pending', `notes` text DEFAULT NULL, `created_at` timestamp NOT NULL DEFAULT current\_timestamp() ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4\_unicode\_ci;
-- -- Dumping data for table `agent_tasks`
------------------------------------------
INSERT INTO `agent_tasks` (`task_id`, `agent_id`, `inquiry_id`, `task_type`, `title`, `due_date`, `status`, `notes`, `created_at`) VALUES (1, 2, 1, 'follow\_up', 'Follow up on Fortuner GR inquiry — Pedro Garcia', '2025-05-05 02:00:00', 'done', 'Customer confirmed interest, awaiting financing docs.', '2026-04-19 08:40:18'), (2, 2, NULL, 'appointment', 'Monthly review with branch manager', '2025-05-10 01:00:00', 'pending', NULL, '2026-04-19 08:40:18');

-----
-- -- Table structure for table `amortization_schedule`
-------------------------------------------------------
CREATE TABLE `amortization_schedule` ( `schedule_id` int(11) NOT NULL, `loan_id` int(11) NOT NULL, `month_number` int(11) NOT NULL, `due_date` date NOT NULL, `principal` decimal(12,2) NOT NULL, `interest` decimal(12,2) NOT NULL, `total_due` decimal(12,2) NOT NULL, `running_balance` decimal(12,2) NOT NULL, `status` enum('unpaid','paid','overdue') NOT NULL DEFAULT 'unpaid', `created_at` timestamp NOT NULL DEFAULT current\_timestamp() ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4\_unicode\_ci;
-- -- Dumping data for table `amortization_schedule`
----------------------------------------------------
INSERT INTO `amortization_schedule` (`schedule_id`, `loan_id`, `month_number`, `due_date`, `principal`, `interest`, `total_due`, `running_balance`, `status`, `created_at`) VALUES (1, 1, 1, '2025-05-15', 27015.12, 10358.33, 37373.45, 1884984.88, 'paid', '2026-04-19 08:40:18'), (2, 1, 2, '2025-06-15', 27161.99, 10211.46, 37373.45, 1857822.89, 'paid', '2026-04-19 08:40:18'), (3, 1, 3, '2025-07-15', 27309.65, 10063.80, 37373.45, 1830513.24, 'unpaid', '2026-04-19 08:40:18');

-----
-- -- Table structure for table `audit_logs`
--------------------------------------------
CREATE TABLE `audit_logs` ( `log_id` int(11) NOT NULL, `user_id` int(11) DEFAULT NULL, `action` varchar(100) NOT NULL, `table_name` varchar(50) NOT NULL, `record_id` int(11) DEFAULT NULL, `old_value` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4\_bin DEFAULT NULL CHECK (json\_valid(`old_value`)), `new_value` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4\_bin DEFAULT NULL CHECK (json\_valid(`new_value`)), `ip_address` varchar(45) DEFAULT NULL, `created_at` timestamp NOT NULL DEFAULT current\_timestamp() ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4\_unicode\_ci;
-- -- Dumping data for table `audit_logs`
-----------------------------------------
INSERT INTO `audit_logs` (`log_id`, `user_id`, `action`, `table_name`, `record_id`, `old_value`, `new_value`, `ip_address`, `created_at`) VALUES (1, 1, 'UPDATE', 'vehicles', 4, '{"status":"available"}', '{"status":"reserved"}', '192.168.1.10', '2026-04-19 08:40:18'), (2, 1, 'INSERT', 'sales', 2, NULL, '{"sale\_id":2,"status":"active"}', '192.168.1.10', '2026-04-19 08:40:18');

-----
-- -- Table structure for table `chatbot_logs`
----------------------------------------------
CREATE TABLE `chatbot_logs` ( `log_id` int(11) NOT NULL, `session_id` varchar(100) NOT NULL, `user_id` int(11) DEFAULT NULL, `inquiry_id` int(11) DEFAULT NULL, `user_message` text NOT NULL, `bot_response` text NOT NULL, `intent_tag` varchar(50) DEFAULT NULL, `created_at` timestamp NOT NULL DEFAULT current\_timestamp() ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4\_unicode\_ci;

-----
-- -- Table structure for table `customer_details`
--------------------------------------------------
CREATE TABLE `customer_details` ( `user_id` int(11) NOT NULL, `customer_number` varchar(20) NOT NULL, `preferred_contact_method` enum('email','sms','whatsapp') DEFAULT NULL, `preferred_payment_method` enum('cash','installment','bank\_transfer') DEFAULT NULL, `notes` text DEFAULT NULL ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4\_unicode\_ci;
-- -- Dumping data for table `customer_details`
-----------------------------------------------
INSERT INTO `customer_details` (`user_id`, `customer_number`, `preferred_contact_method`, `preferred_payment_method`, `notes`) VALUES (4, 'CUST-2025-001', 'email', 'installment', NULL), (5, 'CUST-2025-002', 'sms', 'cash', NULL);

-----
-- -- Table structure for table `documents`
-------------------------------------------
CREATE TABLE `documents` ( `document_id` int(11) NOT NULL, `sale_id` int(11) NOT NULL, `document_type` enum('OR','CR','warranty\_cert','amortization\_schedule','sales\_contract','other') NOT NULL, `file_url` varchar(500) NOT NULL, `is_accessible` tinyint(1) NOT NULL DEFAULT 1, `created_at` timestamp NOT NULL DEFAULT current\_timestamp() ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4\_unicode\_ci;
-- -- Dumping data for table `documents`
----------------------------------------
INSERT INTO `documents` (`document_id`, `sale_id`, `document_type`, `file_url`, `is_accessible`, `created_at`) VALUES (1, 1, 'OR', 'https://docs.automatik.ph/or/OR-2025-001.pdf', 1, '2026-04-19 08:40:18'), (2, 1, 'CR', 'https://docs.automatik.ph/cr/CR-2025-001.pdf', 1, '2026-04-19 08:40:18'), (3, 2, 'amortization\_schedule', 'https://docs.automatik.ph/amo/SCHED-2025-001.pdf', 1, '2026-04-19 08:40:18');

-----
-- -- Table structure for table `inquiries`
-------------------------------------------
CREATE TABLE `inquiries` ( `inquiry_id` int(11) NOT NULL, `user_id` int(11) DEFAULT NULL, `agent_id` int(11) DEFAULT NULL, `vehicle_id` int(11) NOT NULL, `guest_name` varchar(100) DEFAULT NULL, `guest_email` varchar(100) DEFAULT NULL, `guest_number` varchar(20) DEFAULT NULL, `message` text NOT NULL, `status` enum('open','assigned','resolved','closed') NOT NULL DEFAULT 'open', `created_at` timestamp NOT NULL DEFAULT current\_timestamp(), `resolved_at` timestamp NULL DEFAULT NULL ) ;
-- -- Dumping data for table `inquiries`
----------------------------------------
INSERT INTO `inquiries` (`inquiry_id`, `user_id`, `agent_id`, `vehicle_id`, `guest_name`, `guest_email`, `guest_number`, `message`, `status`, `created_at`, `resolved_at`) VALUES (1, 4, 2, 1, NULL, NULL, NULL, 'I am interested in the Fortuner GR. What is the best deal available?', 'assigned', '2026-04-19 08:40:18', NULL), (2, NULL, NULL, 3, 'Juan Buenaventura', 'juan.b@email.com', NULL, 'How much is the downpayment for CR-V RS?', 'open', '2026-04-19 08:40:18', NULL);

-----
-- -- Table structure for table `insurance_records`
---------------------------------------------------
CREATE TABLE `insurance_records` ( `insurance_id` int(11) NOT NULL, `vehicle_id` int(11) NOT NULL, `sale_id` int(11) NOT NULL, `customer_id` int(11) DEFAULT NULL, `provider_name` varchar(150) NOT NULL, `policy_number` varchar(100) NOT NULL, `coverage_type` varchar(100) DEFAULT NULL, `start_date` date NOT NULL, `end_date` date NOT NULL, `status` enum('active','expired','cancelled') NOT NULL DEFAULT 'active' ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4\_unicode\_ci;
-- -- Dumping data for table `insurance_records`
------------------------------------------------
INSERT INTO `insurance_records` (`insurance_id`, `vehicle_id`, `sale_id`, `customer_id`, `provider_name`, `policy_number`, `coverage_type`, `start_date`, `end_date`, `status`) VALUES (1, 4, 1, 5, 'Malayan Insurance', 'MAL-2025-VH-001', 'Comprehensive', '2025-03-10', '2026-03-10', 'active'), (2, 1, 2, 4, 'Pioneer Life Inc.', 'PIO-2025-VH-002', 'CTPL + Comprehensive', '2025-04-01', '2026-04-01', 'active');

-----
-- -- Table structure for table `loan_details`
----------------------------------------------
CREATE TABLE `loan_details` ( `loan_id` int(11) NOT NULL, `sale_id` int(11) NOT NULL, `down_payment` decimal(12,2) NOT NULL, `loan_amount` decimal(12,2) NOT NULL, `interest_rate` decimal(5,2) NOT NULL, `term_months` int(11) NOT NULL, `monthly_amortization` decimal(12,2) NOT NULL, `bank_name` varchar(100) DEFAULT NULL, `bank_approval_status` enum('pending','approved','rejected') NOT NULL DEFAULT 'pending', `created_at` timestamp NOT NULL DEFAULT current\_timestamp() ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4\_unicode\_ci;
-- -- Dumping data for table `loan_details`
-------------------------------------------
INSERT INTO `loan_details` (`loan_id`, `sale_id`, `down_payment`, `loan_amount`, `interest_rate`, `term_months`, `monthly_amortization`, `bank_name`, `bank_approval_status`, `created_at`) VALUES (1, 2, 478000.00, 1912000.00, 6.50, 60, 37327.45, 'BDO Unibank', 'approved', '2026-04-19 08:40:18');

-----
-- -- Table structure for table `notifications`
-----------------------------------------------
CREATE TABLE `notifications` ( `notification_id` int(11) NOT NULL, `user_id` int(11) NOT NULL, `title` varchar(200) NOT NULL, `message` text NOT NULL, `channel` enum('in\_app','email','sms') NOT NULL DEFAULT 'in\_app', `ref_type` varchar(50) DEFAULT NULL, `ref_id` int(11) DEFAULT NULL, `is_read` tinyint(1) NOT NULL DEFAULT 0, `created_at` timestamp NOT NULL DEFAULT current\_timestamp() ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4\_unicode\_ci;
-- -- Dumping data for table `notifications`
--------------------------------------------
INSERT INTO `notifications` (`notification_id`, `user_id`, `title`, `message`, `channel`, `ref_type`, `ref_id`, `is_read`, `created_at`) VALUES (1, 4, 'Amortization Due', 'Your payment of PHP 37,373.45 is due on July 15, 2025.', 'email', 'amortization\_schedule', 3, 0, '2026-04-19 08:40:18'), (2, 2, 'New Inquiry Assigned', 'A new inquiry has been assigned to you from Pedro Garcia.', 'in\_app', 'inquiries', 1, 0, '2026-04-19 08:40:18');

-----
-- -- Table structure for table `payments`
------------------------------------------
CREATE TABLE `payments` ( `payment_id` int(11) NOT NULL, `sale_id` int(11) NOT NULL, `schedule_id` int(11) DEFAULT NULL, `amount_paid` decimal(12,2) NOT NULL, `payment_date` timestamp NOT NULL DEFAULT current\_timestamp(), `payment_method` enum('cash','bank\_transfer','check','online') NOT NULL, `reference` varchar(100) DEFAULT NULL, `recorded_by` int(11) NOT NULL, `created_at` timestamp NOT NULL DEFAULT current\_timestamp() ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4\_unicode\_ci;
-- -- Dumping data for table `payments`
---------------------------------------
INSERT INTO `payments` (`payment_id`, `sale_id`, `schedule_id`, `amount_paid`, `payment_date`, `payment_method`, `reference`, `recorded_by`, `created_at`) VALUES (1, 1, NULL, 1648000.00, '2026-04-19 08:40:18', 'bank\_transfer', 'BDO-TXN-20250310-001', 1, '2026-04-19 08:40:18'), (2, 2, 1, 37373.45, '2026-04-19 08:40:18', 'online', 'BDO-AMO-20250515-001', 1, '2026-04-19 08:40:18'), (3, 2, 2, 37373.45, '2026-04-19 08:40:18', 'online', 'BDO-AMO-20250615-001', 1, '2026-04-19 08:40:18');

-----
-- -- Table structure for table `sales`
---------------------------------------
CREATE TABLE `sales` ( `sale_id` int(11) NOT NULL, `vehicle_id` int(11) NOT NULL, `customer_id` int(11) DEFAULT NULL, `agent_id` int(11) NOT NULL, `inquiry_id` int(11) DEFAULT NULL, `selling_price` decimal(12,2) NOT NULL, `payment_type` enum('cash','installment') NOT NULL, `sale_date` timestamp NOT NULL DEFAULT current\_timestamp(), `status` enum('pending','active','completed','cancelled') NOT NULL DEFAULT 'pending', `created_at` timestamp NOT NULL DEFAULT current\_timestamp() ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4\_unicode\_ci;
-- -- Dumping data for table `sales`
------------------------------------
INSERT INTO `sales` (`sale_id`, `vehicle_id`, `customer_id`, `agent_id`, `inquiry_id`, `selling_price`, `payment_type`, `sale_date`, `status`, `created_at`) VALUES (1, 4, 5, 3, NULL, 1648000.00, 'cash', '2026-04-19 08:40:18', 'completed', '2026-04-19 08:40:18'), (2, 1, 4, 2, 1, 2390000.00, 'installment', '2026-04-19 08:40:18', 'active', '2026-04-19 08:40:18');

-----
-- -- Table structure for table `sales_contracts`
-------------------------------------------------
CREATE TABLE `sales_contracts` ( `contract_id` int(11) NOT NULL, `sale_id` int(11) NOT NULL, `contract_url` varchar(500) DEFAULT NULL, `status` enum('draft','pending\_signature','signed','cancelled') NOT NULL DEFAULT 'draft', `signed_at` timestamp NULL DEFAULT NULL, `reviewed_by` int(11) DEFAULT NULL, `created_at` timestamp NOT NULL DEFAULT current\_timestamp() ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4\_unicode\_ci;
-- -- Dumping data for table `sales_contracts`
----------------------------------------------
INSERT INTO `sales_contracts` (`contract_id`, `sale_id`, `contract_url`, `status`, `signed_at`, `reviewed_by`, `created_at`) VALUES (1, 1, 'https://docs.automatik.ph/contracts/SC-2025-001.pdf', 'signed', '2025-03-10 06:00:00', 1, '2026-04-19 08:40:18'), (2, 2, 'https://docs.automatik.ph/contracts/SC-2025-002.pdf', 'signed', '2025-04-01 02:00:00', 1, '2026-04-19 08:40:18');

-----
-- -- Table structure for table `service_bookings`
--------------------------------------------------
CREATE TABLE `service_bookings` ( `booking_id` int(11) NOT NULL, `customer_id` int(11) DEFAULT NULL, `vehicle_id` int(11) NOT NULL, `slot_id` int(11) NOT NULL, `booking_type` enum('test\_drive','maintenance','repair') NOT NULL, `warranty_claim_id` int(11) DEFAULT NULL, `notes` text DEFAULT NULL, `status` enum('pending','confirmed','completed','cancelled') NOT NULL DEFAULT 'pending', `created_at` timestamp NOT NULL DEFAULT current\_timestamp() ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4\_unicode\_ci;
-- -- Dumping data for table `service_bookings`
-----------------------------------------------
INSERT INTO `service_bookings` (`booking_id`, `customer_id`, `vehicle_id`, `slot_id`, `booking_type`, `warranty_claim_id`, `notes`, `status`, `created_at`) VALUES (1, 4, 1, 1, 'test\_drive', NULL, 'Customer wants to test the Fortuner GR on NLEX.', 'confirmed', '2026-04-19 08:40:18');

-----
-- -- Table structure for table `service_slots`
-----------------------------------------------
CREATE TABLE `service_slots` ( `slot_id` int(11) NOT NULL, `slot_datetime` timestamp NOT NULL DEFAULT current\_timestamp() ON UPDATE current\_timestamp(), `slot_type` enum('test\_drive','maintenance','repair') NOT NULL, `capacity` int(11) NOT NULL DEFAULT 1, `is_available` tinyint(1) NOT NULL DEFAULT 1, `created_at` timestamp NOT NULL DEFAULT current\_timestamp() ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4\_unicode\_ci;
-- -- Dumping data for table `service_slots`
--------------------------------------------
INSERT INTO `service_slots` (`slot_id`, `slot_datetime`, `slot_type`, `capacity`, `is_available`, `created_at`) VALUES (1, '2025-05-20 01:00:00', 'test\_drive', 2, 1, '2026-04-19 08:40:18'), (2, '2025-05-20 06:00:00', 'maintenance', 3, 1, '2026-04-19 08:40:18'), (3, '2025-05-21 02:00:00', 'test\_drive', 2, 1, '2026-04-19 08:40:18');

-----
-- -- Table structure for table `suppliers`
-------------------------------------------
CREATE TABLE `suppliers` ( `supplier_id` int(11) NOT NULL, `company_name` varchar(150) NOT NULL, `contact_name` varchar(100) DEFAULT NULL, `contact_email` varchar(100) DEFAULT NULL, `contact_phone` varchar(20) DEFAULT NULL, `address` varchar(255) DEFAULT NULL, `is_active` tinyint(1) NOT NULL DEFAULT 1, `created_at` timestamp NOT NULL DEFAULT current\_timestamp() ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4\_unicode\_ci;
-- -- Dumping data for table `suppliers`
----------------------------------------
INSERT INTO `suppliers` (`supplier_id`, `company_name`, `contact_name`, `contact_email`, `contact_phone`, `address`, `is_active`, `created_at`) VALUES (1, 'Toyota Motors PH', 'Ramon Castillo', 'rcastillo@toyota.ph', '02-88001234', 'Santa Rosa, Laguna', 1, '2026-04-19 08:40:18'), (2, 'Honda Cars PH', 'Liza Villanueva', 'lvillanueva@honda.ph', '02-88005678', 'Pasig City, Metro Manila', 1, '2026-04-19 08:40:18'), (3, 'Hyundai Asia Resources', 'Kevin Ong', 'kong@hyundai.ph', '02-88009012', 'Mandaluyong, Metro Manila', 1, '2026-04-19 08:40:18');

-----
-- -- Table structure for table `supplies`
------------------------------------------
CREATE TABLE `supplies` ( `supply_id` int(11) NOT NULL, `supplier_id` int(11) NOT NULL, `part_name` varchar(150) NOT NULL, `part_number` varchar(50) NOT NULL, `unit_cost` decimal(10,2) NOT NULL, `stock_qty` int(11) NOT NULL DEFAULT 0, `reorder_level` int(11) NOT NULL DEFAULT 10, `updated_at` timestamp NOT NULL DEFAULT current\_timestamp() ON UPDATE current\_timestamp() ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4\_unicode\_ci;

-----
-- -- Table structure for table `system_settings`
-------------------------------------------------
CREATE TABLE `system_settings` ( `setting_id` int(11) NOT NULL, `setting_key` varchar(100) NOT NULL, `setting_value` text NOT NULL, `description` varchar(255) DEFAULT NULL, `updated_by` int(11) DEFAULT NULL, `updated_at` timestamp NOT NULL DEFAULT current\_timestamp() ON UPDATE current\_timestamp() ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4\_unicode\_ci;
-- -- Dumping data for table `system_settings`
----------------------------------------------
INSERT INTO `system_settings` (`setting_id`, `setting_key`, `setting_value`, `description`, `updated_by`, `updated_at`) VALUES (1, 'default\_commission\_rate', '3.00', 'Default agent commission rate in percent', 1, '2026-04-19 08:40:18'), (2, 'chatbot\_enabled', 'true', 'Toggle AI chatbot on/off', 1, '2026-04-19 08:40:18'), (3, 'max\_loan\_term\_months', '60', 'Maximum allowed loan term in months', 1, '2026-04-19 08:40:18');

-----
-- -- Table structure for table `users`
---------------------------------------
CREATE TABLE `users` ( `user_id` int(11) NOT NULL, `username` varchar(50) NOT NULL, `hashed_password` varchar(255) NOT NULL, `email` varchar(100) NOT NULL, `role` enum('admin','agent','customer') NOT NULL, `email_verified` tinyint(1) NOT NULL DEFAULT 0, `is_active` tinyint(1) NOT NULL DEFAULT 1, `last_login` timestamp NULL DEFAULT NULL, `created_at` timestamp NOT NULL DEFAULT current\_timestamp() ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4\_unicode\_ci;
-- -- Dumping data for table `users`
------------------------------------
INSERT INTO `users` (`user_id`, `username`, `hashed_password`, `email`, `role`, `email_verified`, `is_active`, `last_login`, `created_at`) VALUES (1, 'admin\_jose', '$2b$12$mockhashadmin001', 'jose.admin@automatik.ph', 'admin', 1, 1, NULL, '2026-04-19 08:40:18'), (2, 'agent\_miguel', '$2b$12$mockhashagent001', 'miguel.reyes@automatik.ph', 'agent', 1, 1, NULL, '2026-04-19 08:40:18'), (3, 'agent\_anna', '$2b$12$mockhashagent002', 'anna.santos@automatik.ph', 'agent', 1, 1, NULL, '2026-04-19 08:40:18'), (4, 'cust\_pedro', '$2b$12$mockhashcust001', 'pedro.garcia@gmail.com', 'customer', 1, 1, NULL, '2026-04-19 08:40:18'), (5, 'cust\_maria', '$2b$12$mockhashcust002', 'maria.dela.cruz@gmail.com', 'customer', 1, 1, NULL, '2026-04-19 08:40:18');

-----
-- -- Table structure for table `user_profile`
----------------------------------------------
CREATE TABLE `user_profile` ( `user_id` int(11) NOT NULL, `full_name` varchar(100) NOT NULL, `phone_number` varchar(20) DEFAULT NULL, `address` varchar(255) DEFAULT NULL, `city` varchar(100) DEFAULT NULL, `province` varchar(100) DEFAULT NULL, `zip_code` varchar(10) DEFAULT NULL, `date_of_birth` date DEFAULT NULL, `gender` enum('male','female','prefer\_not\_to\_say') DEFAULT NULL, `profile_picture_url` varchar(500) DEFAULT NULL, `updated_at` timestamp NOT NULL DEFAULT current\_timestamp() ON UPDATE current\_timestamp() ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4\_unicode\_ci;
-- -- Dumping data for table `user_profile`
-------------------------------------------
INSERT INTO `user_profile` (`user_id`, `full_name`, `phone_number`, `address`, `city`, `province`, `zip_code`, `date_of_birth`, `gender`, `profile_picture_url`, `updated_at`) VALUES (1, 'Jose Ramirez', '09171234567', '123 Rizal St', 'Manila', 'Metro Manila', '1000', NULL, 'male', NULL, '2026-04-19 08:40:18'), (2, 'Miguel Reyes', '09181234568', '456 Mabini Ave', 'Quezon City', 'Metro Manila', '1100', NULL, 'male', NULL, '2026-04-19 08:40:18'), (3, 'Anna Santos', '09191234569', '789 Luna Blvd', 'Makati', 'Metro Manila', '1200', NULL, 'female', NULL, '2026-04-19 08:40:18'), (4, 'Pedro Garcia', '09201234570', '12 Sampaguita St', 'Pasig', 'Metro Manila', '1600', NULL, 'male', NULL, '2026-04-19 08:40:18'), (5, 'Maria Dela Cruz', '09211234571', '34 Rosal Ave', 'Marikina', 'Metro Manila', '1800', NULL, 'female', NULL, '2026-04-19 08:40:18');

-----
-- -- Table structure for table `vehicles`
------------------------------------------
CREATE TABLE `vehicles` ( `vehicle_id` int(11) NOT NULL, `supplier_id` int(11) NOT NULL, `vin` varchar(17) NOT NULL, `brand` varchar(50) NOT NULL, `model` varchar(100) NOT NULL, `year` smallint(6) NOT NULL, `color` varchar(50) DEFAULT NULL, `body_type` varchar(20) DEFAULT NULL, `seating_capacity` int(11) DEFAULT NULL, `transmission` enum('manual','automatic') DEFAULT NULL, `fuel_type` enum('gasoline','diesel','electric','hybrid') DEFAULT NULL, `price` decimal(12,2) NOT NULL, `status` enum('available','reserved','discontinued','delivered') NOT NULL DEFAULT 'available', `specs_json` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4\_bin DEFAULT NULL CHECK (json\_valid(`specs_json`)), `created_at` timestamp NOT NULL DEFAULT current\_timestamp() ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4\_unicode\_ci;
-- -- Dumping data for table `vehicles`
---------------------------------------
INSERT INTO `vehicles` (`vehicle_id`, `supplier_id`, `vin`, `brand`, `model`, `year`, `color`, `body_type`, `seating_capacity`, `transmission`, `fuel_type`, `price`, `status`, `specs_json`, `created_at`) VALUES (1, 1, '1HGBH41JXMN109186', 'Toyota', 'Fortuner GR Sport', 2025, 'Phantom Brown', 'SUV', 7, 'automatic', 'diesel', 2390000.00, 'available', NULL, '2026-04-19 08:40:18'), (2, 1, '1HGBH41JXMN109187', 'Toyota', 'Vios XLE CVT', 2025, 'Pearl White', 'Sedan', 5, 'automatic', 'gasoline', 798000.00, 'available', NULL, '2026-04-19 08:40:18'), (3, 2, '2HGFB2F59DH519681', 'Honda', 'CR-V RS Turbo', 2024, 'Sonic Gray', 'SUV', 5, 'automatic', 'gasoline', 1899000.00, 'available', NULL, '2026-04-19 08:40:18'), (4, 3, '5NPE34AF8FH002518', 'Hyundai', 'Tucson HTRAC', 2025, 'Abyss Black', 'SUV', 5, 'automatic', 'gasoline', 1648000.00, 'reserved', NULL, '2026-04-19 08:40:18'), (5, 2, '2HGFB2F59DH519682', 'Honda', 'Civic RS Turbo', 2024, 'Rallye Red', 'Sedan', 5, 'manual', 'gasoline', 1249000.00, 'available', NULL, '2026-04-19 08:40:18');

-----
-- -- Table structure for table `vehicle_photos`
------------------------------------------------
CREATE TABLE `vehicle_photos` ( `photo_id` int(11) NOT NULL, `vehicle_id` int(11) NOT NULL, `photo_url` varchar(500) NOT NULL, `sort_order` int(11) NOT NULL DEFAULT 0, `uploaded_at` timestamp NOT NULL DEFAULT current\_timestamp() ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4\_unicode\_ci;
-- -- Dumping data for table `vehicle_photos`
---------------------------------------------
INSERT INTO `vehicle_photos` (`photo_id`, `vehicle_id`, `photo_url`, `sort_order`, `uploaded_at`) VALUES (1, 1, 'https://cdn.automatik.ph/vehicles/fortuner\_gr\_front.jpg', 1, '2026-04-19 08:40:18'), (2, 1, 'https://cdn.automatik.ph/vehicles/fortuner\_gr\_side.jpg', 2, '2026-04-19 08:40:18'), (3, 2, 'https://cdn.automatik.ph/vehicles/vios\_xle\_front.jpg', 1, '2026-04-19 08:40:18'), (4, 3, 'https://cdn.automatik.ph/vehicles/crv\_rs\_front.jpg', 1, '2026-04-19 08:40:18');

-----
-- -- Table structure for table `warranty_claims`
-------------------------------------------------
CREATE TABLE `warranty_claims` ( `claim_id` int(11) NOT NULL, `sale_id` int(11) NOT NULL, `vehicle_id` int(11) NOT NULL, `claim_type` enum('repair','replacement','refund') NOT NULL, `description` text NOT NULL, `status` enum('submitted','under\_review','approved','rejected','resolved') NOT NULL DEFAULT 'submitted', `reviewed_by` int(11) DEFAULT NULL, `resolution` text DEFAULT NULL, `submitted_at` timestamp NOT NULL DEFAULT current\_timestamp(), `resolved_at` timestamp NULL DEFAULT NULL ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4\_unicode\_ci;
-- -- Dumping data for table `warranty_claims`
----------------------------------------------
INSERT INTO `warranty_claims` (`claim_id`, `sale_id`, `vehicle_id`, `claim_type`, `description`, `status`, `reviewed_by`, `resolution`, `submitted_at`, `resolved_at`) VALUES (1, 1, 4, 'repair', 'Air conditioning unit not cooling properly after 2 months of use.', 'approved', 1, NULL, '2025-05-12 01:00:00', NULL);
-- -- Indexes for dumped tables
-------------------------------
-- -- Indexes for table `access_tokens`
---------------------------------------
ALTER TABLE `access_tokens` ADD PRIMARY KEY (`token_id`), ADD KEY `user_id` (`user_id`);
-- -- Indexes for table `agent_commissions`
-------------------------------------------
ALTER TABLE `agent_commissions` ADD PRIMARY KEY (`commission_id`), ADD KEY `sale_id` (`sale_id`), ADD KEY `agent_id` (`agent_id`);
-- -- Indexes for table `agent_details`
---------------------------------------
ALTER TABLE `agent_details` ADD PRIMARY KEY (`user_id`), ADD UNIQUE KEY `employee_number` (`employee_number`);
-- -- Indexes for table `agent_tasks`
-------------------------------------
ALTER TABLE `agent_tasks` ADD PRIMARY KEY (`task_id`), ADD KEY `agent_id` (`agent_id`), ADD KEY `inquiry_id` (`inquiry_id`);
-- -- Indexes for table `amortization_schedule`
-----------------------------------------------
ALTER TABLE `amortization_schedule` ADD PRIMARY KEY (`schedule_id`), ADD UNIQUE KEY `uq_loan_month` (`loan_id`,`month_number`);
-- -- Indexes for table `audit_logs`
------------------------------------
ALTER TABLE `audit_logs` ADD PRIMARY KEY (`log_id`);
-- -- Indexes for table `chatbot_logs`
--------------------------------------
ALTER TABLE `chatbot_logs` ADD PRIMARY KEY (`log_id`), ADD KEY `user_id` (`user_id`), ADD KEY `inquiry_id` (`inquiry_id`);
-- -- Indexes for table `customer_details`
------------------------------------------
ALTER TABLE `customer_details` ADD PRIMARY KEY (`user_id`), ADD UNIQUE KEY `customer_number` (`customer_number`);
-- -- Indexes for table `documents`
-----------------------------------
ALTER TABLE `documents` ADD PRIMARY KEY (`document_id`), ADD KEY `sale_id` (`sale_id`);
-- -- Indexes for table `inquiries`
-----------------------------------
ALTER TABLE `inquiries` ADD PRIMARY KEY (`inquiry_id`), ADD KEY `user_id` (`user_id`), ADD KEY `agent_id` (`agent_id`), ADD KEY `vehicle_id` (`vehicle_id`);
-- -- Indexes for table `insurance_records`
-------------------------------------------
ALTER TABLE `insurance_records` ADD PRIMARY KEY (`insurance_id`), ADD UNIQUE KEY `policy_number` (`policy_number`), ADD KEY `vehicle_id` (`vehicle_id`), ADD KEY `sale_id` (`sale_id`), ADD KEY `customer_id` (`customer_id`);
-- -- Indexes for table `loan_details`
--------------------------------------
ALTER TABLE `loan_details` ADD PRIMARY KEY (`loan_id`), ADD UNIQUE KEY `sale_id` (`sale_id`);
-- -- Indexes for table `notifications`
---------------------------------------
ALTER TABLE `notifications` ADD PRIMARY KEY (`notification_id`), ADD KEY `user_id` (`user_id`);
-- -- Indexes for table `payments`
----------------------------------
ALTER TABLE `payments` ADD PRIMARY KEY (`payment_id`), ADD KEY `sale_id` (`sale_id`), ADD KEY `schedule_id` (`schedule_id`), ADD KEY `recorded_by` (`recorded_by`);
-- -- Indexes for table `sales`
-------------------------------
ALTER TABLE `sales` ADD PRIMARY KEY (`sale_id`), ADD KEY `vehicle_id` (`vehicle_id`), ADD KEY `customer_id` (`customer_id`), ADD KEY `agent_id` (`agent_id`), ADD KEY `inquiry_id` (`inquiry_id`);
-- -- Indexes for table `sales_contracts`
-----------------------------------------
ALTER TABLE `sales_contracts` ADD PRIMARY KEY (`contract_id`), ADD KEY `sale_id` (`sale_id`), ADD KEY `reviewed_by` (`reviewed_by`);
-- -- Indexes for table `service_bookings`
------------------------------------------
ALTER TABLE `service_bookings` ADD PRIMARY KEY (`booking_id`), ADD KEY `customer_id` (`customer_id`), ADD KEY `vehicle_id` (`vehicle_id`), ADD KEY `slot_id` (`slot_id`), ADD KEY `warranty_claim_id` (`warranty_claim_id`);
-- -- Indexes for table `service_slots`
---------------------------------------
ALTER TABLE `service_slots` ADD PRIMARY KEY (`slot_id`);
-- -- Indexes for table `suppliers`
-----------------------------------
ALTER TABLE `suppliers` ADD PRIMARY KEY (`supplier_id`);
-- -- Indexes for table `supplies`
----------------------------------
ALTER TABLE `supplies` ADD PRIMARY KEY (`supply_id`), ADD UNIQUE KEY `part_number` (`part_number`), ADD KEY `supplier_id` (`supplier_id`);
-- -- Indexes for table `system_settings`
-----------------------------------------
ALTER TABLE `system_settings` ADD PRIMARY KEY (`setting_id`), ADD UNIQUE KEY `setting_key` (`setting_key`), ADD KEY `updated_by` (`updated_by`);
-- -- Indexes for table `users`
-------------------------------
ALTER TABLE `users` ADD PRIMARY KEY (`user_id`), ADD UNIQUE KEY `username` (`username`), ADD UNIQUE KEY `email` (`email`);
-- -- Indexes for table `user_profile`
--------------------------------------
ALTER TABLE `user_profile` ADD PRIMARY KEY (`user_id`);
-- -- Indexes for table `vehicles`
----------------------------------
ALTER TABLE `vehicles` ADD PRIMARY KEY (`vehicle_id`), ADD UNIQUE KEY `vin` (`vin`), ADD KEY `supplier_id` (`supplier_id`);
-- -- Indexes for table `vehicle_photos`
----------------------------------------
ALTER TABLE `vehicle_photos` ADD PRIMARY KEY (`photo_id`), ADD KEY `vehicle_id` (`vehicle_id`);
-- -- Indexes for table `warranty_claims`
-----------------------------------------
ALTER TABLE `warranty_claims` ADD PRIMARY KEY (`claim_id`), ADD KEY `fk_wc_sale` (`sale_id`), ADD KEY `fk_wc_vehicle` (`vehicle_id`), ADD KEY `fk_wc_admin` (`reviewed_by`);
-- -- AUTO\_INCREMENT for dumped tables
---------------------------------------
-- -- AUTO\_INCREMENT for table `agent_commissions`
---------------------------------------------------
ALTER TABLE `agent_commissions` MODIFY `commission_id` int(11) NOT NULL AUTO\_INCREMENT, AUTO\_INCREMENT=3;
-- -- AUTO\_INCREMENT for table `agent_tasks`
---------------------------------------------
ALTER TABLE `agent_tasks` MODIFY `task_id` int(11) NOT NULL AUTO\_INCREMENT, AUTO\_INCREMENT=3;
-- -- AUTO\_INCREMENT for table `amortization_schedule`
-------------------------------------------------------
ALTER TABLE `amortization_schedule` MODIFY `schedule_id` int(11) NOT NULL AUTO\_INCREMENT, AUTO\_INCREMENT=4;
-- -- AUTO\_INCREMENT for table `audit_logs`
--------------------------------------------
ALTER TABLE `audit_logs` MODIFY `log_id` int(11) NOT NULL AUTO\_INCREMENT, AUTO\_INCREMENT=3;
-- -- AUTO\_INCREMENT for table `chatbot_logs`
----------------------------------------------
ALTER TABLE `chatbot_logs` MODIFY `log_id` int(11) NOT NULL AUTO\_INCREMENT;
-- -- AUTO\_INCREMENT for table `documents`
-------------------------------------------
ALTER TABLE `documents` MODIFY `document_id` int(11) NOT NULL AUTO\_INCREMENT, AUTO\_INCREMENT=4;
-- -- AUTO\_INCREMENT for table `inquiries`
-------------------------------------------
ALTER TABLE `inquiries` MODIFY `inquiry_id` int(11) NOT NULL AUTO\_INCREMENT;
-- -- AUTO\_INCREMENT for table `insurance_records`
---------------------------------------------------
ALTER TABLE `insurance_records` MODIFY `insurance_id` int(11) NOT NULL AUTO\_INCREMENT, AUTO\_INCREMENT=3;
-- -- AUTO\_INCREMENT for table `loan_details`
----------------------------------------------
ALTER TABLE `loan_details` MODIFY `loan_id` int(11) NOT NULL AUTO\_INCREMENT, AUTO\_INCREMENT=2;
-- -- AUTO\_INCREMENT for table `notifications`
-----------------------------------------------
ALTER TABLE `notifications` MODIFY `notification_id` int(11) NOT NULL AUTO\_INCREMENT, AUTO\_INCREMENT=3;
-- -- AUTO\_INCREMENT for table `payments`
------------------------------------------
ALTER TABLE `payments` MODIFY `payment_id` int(11) NOT NULL AUTO\_INCREMENT, AUTO\_INCREMENT=4;
-- -- AUTO\_INCREMENT for table `sales`
---------------------------------------
ALTER TABLE `sales` MODIFY `sale_id` int(11) NOT NULL AUTO\_INCREMENT, AUTO\_INCREMENT=3;
-- -- AUTO\_INCREMENT for table `sales_contracts`
-------------------------------------------------
ALTER TABLE `sales_contracts` MODIFY `contract_id` int(11) NOT NULL AUTO\_INCREMENT, AUTO\_INCREMENT=3;
-- -- AUTO\_INCREMENT for table `service_bookings`
--------------------------------------------------
ALTER TABLE `service_bookings` MODIFY `booking_id` int(11) NOT NULL AUTO\_INCREMENT, AUTO\_INCREMENT=2;
-- -- AUTO\_INCREMENT for table `service_slots`
-----------------------------------------------
ALTER TABLE `service_slots` MODIFY `slot_id` int(11) NOT NULL AUTO\_INCREMENT, AUTO\_INCREMENT=4;
-- -- AUTO\_INCREMENT for table `suppliers`
-------------------------------------------
ALTER TABLE `suppliers` MODIFY `supplier_id` int(11) NOT NULL AUTO\_INCREMENT, AUTO\_INCREMENT=4;
-- -- AUTO\_INCREMENT for table `supplies`
------------------------------------------
ALTER TABLE `supplies` MODIFY `supply_id` int(11) NOT NULL AUTO\_INCREMENT;
-- -- AUTO\_INCREMENT for table `system_settings`
-------------------------------------------------
ALTER TABLE `system_settings` MODIFY `setting_id` int(11) NOT NULL AUTO\_INCREMENT, AUTO\_INCREMENT=4;
-- -- AUTO\_INCREMENT for table `users`
---------------------------------------
ALTER TABLE `users` MODIFY `user_id` int(11) NOT NULL AUTO\_INCREMENT, AUTO\_INCREMENT=6;
-- -- AUTO\_INCREMENT for table `vehicles`
------------------------------------------
ALTER TABLE `vehicles` MODIFY `vehicle_id` int(11) NOT NULL AUTO\_INCREMENT, AUTO\_INCREMENT=6;
-- -- AUTO\_INCREMENT for table `vehicle_photos`
------------------------------------------------
ALTER TABLE `vehicle_photos` MODIFY `photo_id` int(11) NOT NULL AUTO\_INCREMENT, AUTO\_INCREMENT=5;
-- -- AUTO\_INCREMENT for table `warranty_claims`
-------------------------------------------------
ALTER TABLE `warranty_claims` MODIFY `claim_id` int(11) NOT NULL AUTO\_INCREMENT, AUTO\_INCREMENT=2;
-- -- Constraints for dumped tables
-----------------------------------
-- -- Constraints for table `access_tokens`
-------------------------------------------
ALTER TABLE `access_tokens` ADD CONSTRAINT `access_tokens_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;
-- -- Constraints for table `agent_commissions`
-----------------------------------------------
ALTER TABLE `agent_commissions` ADD CONSTRAINT `agent_commissions_ibfk_1` FOREIGN KEY (`sale_id`) REFERENCES `sales` (`sale_id`), ADD CONSTRAINT `agent_commissions_ibfk_2` FOREIGN KEY (`agent_id`) REFERENCES `agent_details` (`user_id`);
-- -- Constraints for table `agent_details`
-------------------------------------------
ALTER TABLE `agent_details` ADD CONSTRAINT `agent_details_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;
-- -- Constraints for table `agent_tasks`
-----------------------------------------
ALTER TABLE `agent_tasks` ADD CONSTRAINT `agent_tasks_ibfk_1` FOREIGN KEY (`agent_id`) REFERENCES `agent_details` (`user_id`), ADD CONSTRAINT `agent_tasks_ibfk_2` FOREIGN KEY (`inquiry_id`) REFERENCES `inquiries` (`inquiry_id`) ON DELETE SET NULL;
-- -- Constraints for table `amortization_schedule`
---------------------------------------------------
ALTER TABLE `amortization_schedule` ADD CONSTRAINT `amortization_schedule_ibfk_1` FOREIGN KEY (`loan_id`) REFERENCES `loan_details` (`loan_id`);
-- -- Constraints for table `chatbot_logs`
------------------------------------------
ALTER TABLE `chatbot_logs` ADD CONSTRAINT `chatbot_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL, ADD CONSTRAINT `chatbot_logs_ibfk_2` FOREIGN KEY (`inquiry_id`) REFERENCES `inquiries` (`inquiry_id`) ON DELETE SET NULL;
-- -- Constraints for table `customer_details`
----------------------------------------------
ALTER TABLE `customer_details` ADD CONSTRAINT `customer_details_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;
-- -- Constraints for table `documents`
---------------------------------------
ALTER TABLE `documents` ADD CONSTRAINT `documents_ibfk_1` FOREIGN KEY (`sale_id`) REFERENCES `sales` (`sale_id`);
-- -- Constraints for table `inquiries`
---------------------------------------
ALTER TABLE `inquiries` ADD CONSTRAINT `inquiries_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL, ADD CONSTRAINT `inquiries_ibfk_2` FOREIGN KEY (`agent_id`) REFERENCES `agent_details` (`user_id`) ON DELETE SET NULL, ADD CONSTRAINT `inquiries_ibfk_3` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`vehicle_id`);
-- -- Constraints for table `insurance_records`
-----------------------------------------------
ALTER TABLE `insurance_records` ADD CONSTRAINT `insurance_records_ibfk_1` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`vehicle_id`), ADD CONSTRAINT `insurance_records_ibfk_2` FOREIGN KEY (`sale_id`) REFERENCES `sales` (`sale_id`), ADD CONSTRAINT `insurance_records_ibfk_3` FOREIGN KEY (`customer_id`) REFERENCES `customer_details` (`user_id`) ON DELETE SET NULL;
-- -- Constraints for table `loan_details`
------------------------------------------
ALTER TABLE `loan_details` ADD CONSTRAINT `loan_details_ibfk_1` FOREIGN KEY (`sale_id`) REFERENCES `sales` (`sale_id`);
-- -- Constraints for table `notifications`
-------------------------------------------
ALTER TABLE `notifications` ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;
-- -- Constraints for table `payments`
--------------------------------------
ALTER TABLE `payments` ADD CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`sale_id`) REFERENCES `sales` (`sale_id`), ADD CONSTRAINT `payments_ibfk_2` FOREIGN KEY (`schedule_id`) REFERENCES `amortization_schedule` (`schedule_id`) ON DELETE SET NULL, ADD CONSTRAINT `payments_ibfk_3` FOREIGN KEY (`recorded_by`) REFERENCES `users` (`user_id`);
-- -- Constraints for table `sales`
-----------------------------------
ALTER TABLE `sales` ADD CONSTRAINT `sales_ibfk_1` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`vehicle_id`), ADD CONSTRAINT `sales_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `customer_details` (`user_id`) ON DELETE SET NULL, ADD CONSTRAINT `sales_ibfk_3` FOREIGN KEY (`agent_id`) REFERENCES `agent_details` (`user_id`), ADD CONSTRAINT `sales_ibfk_4` FOREIGN KEY (`inquiry_id`) REFERENCES `inquiries` (`inquiry_id`) ON DELETE SET NULL;
-- -- Constraints for table `sales_contracts`
---------------------------------------------
ALTER TABLE `sales_contracts` ADD CONSTRAINT `sales_contracts_ibfk_1` FOREIGN KEY (`sale_id`) REFERENCES `sales` (`sale_id`), ADD CONSTRAINT `sales_contracts_ibfk_2` FOREIGN KEY (`reviewed_by`) REFERENCES `users` (`user_id`) ON DELETE SET NULL;
-- -- Constraints for table `service_bookings`
----------------------------------------------
ALTER TABLE `service_bookings` ADD CONSTRAINT `service_bookings_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customer_details` (`user_id`) ON DELETE SET NULL, ADD CONSTRAINT `service_bookings_ibfk_2` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`vehicle_id`), ADD CONSTRAINT `service_bookings_ibfk_3` FOREIGN KEY (`slot_id`) REFERENCES `service_slots` (`slot_id`), ADD CONSTRAINT `service_bookings_ibfk_4` FOREIGN KEY (`warranty_claim_id`) REFERENCES `warranty_claims` (`claim_id`) ON DELETE SET NULL;
-- -- Constraints for table `supplies`
--------------------------------------
ALTER TABLE `supplies` ADD CONSTRAINT `supplies_ibfk_1` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`supplier_id`);
-- -- Constraints for table `system_settings`
---------------------------------------------
ALTER TABLE `system_settings` ADD CONSTRAINT `system_settings_ibfk_1` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`) ON DELETE SET NULL;
-- -- Constraints for table `user_profile`
------------------------------------------
ALTER TABLE `user_profile` ADD CONSTRAINT `user_profile_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;
-- -- Constraints for table `vehicles`
--------------------------------------
ALTER TABLE `vehicles` ADD CONSTRAINT `vehicles_ibfk_1` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`supplier_id`);
-- -- Constraints for table `vehicle_photos`
--------------------------------------------
ALTER TABLE `vehicle_photos` ADD CONSTRAINT `vehicle_photos_ibfk_1` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`vehicle_id`) ON DELETE CASCADE;
-- -- Constraints for table `warranty_claims`
---------------------------------------------
ALTER TABLE `warranty_claims` ADD CONSTRAINT `fk_wc_admin` FOREIGN KEY (`reviewed_by`) REFERENCES `users` (`user_id`) ON DELETE SET NULL, ADD CONSTRAINT `fk_wc_sale` FOREIGN KEY (`sale_id`) REFERENCES `sales` (`sale_id`), ADD CONSTRAINT `fk_wc_vehicle` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`vehicle_id`); COMMIT;

/\*!40101 SET CHARACTER\_SET\_CLIENT=@OLD\_CHARACTER\_SET\_CLIENT */; /*!40101 SET CHARACTER\_SET\_RESULTS=@OLD\_CHARACTER\_SET\_RESULTS */; /*!40101 SET COLLATION\_CONNECTION=@OLD\_COLLATION\_CONNECTION \*/;
