-- phpMyAdmin SQL Dump
-- version 5.2.3-2.fc44
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Jun 15, 2026 at 03:13 AM
-- Server version: 11.8.6-MariaDB
-- PHP Version: 8.5.7

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `automatik`
--

-- --------------------------------------------------------

--
-- Table structure for table `access_tokens`
--

CREATE TABLE `access_tokens` (
  `token_id` varchar(64) NOT NULL,
  `user_id` int(11) NOT NULL,
  `token_hash` varchar(255) NOT NULL,
  `token_type` enum('portal_access','email_verify','password_reset') NOT NULL,
  `expires_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `used_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `access_tokens`
--

INSERT INTO `access_tokens` (`token_id`, `user_id`, `token_hash`, `token_type`, `expires_at`, `used_at`, `created_at`) VALUES
('5c2facfd6c78cdc76ecc6acca060440c', 46, 'bb23bf74a97b886946191d2b681f171ad5eda4caab5e57af43036987c3e35515', 'password_reset', '2026-06-09 22:47:28', '2026-06-09 14:47:27', '2026-06-09 22:46:30'),
('8c60d13f5c62a2d06495ed822c0a35bf', 30, 'ac87538844d58b3015af96b6deb8edfef1e07faa1dd8e36c722d338d9f2d8dc7', 'email_verify', '2026-05-21 14:55:43', '2026-05-21 06:55:43', '2026-05-21 14:55:27'),
('9e4fd17c4dff9cf20bf1f779cf122b13', 30, 'e23a14101d6aaf9159bf296b7d6a27b0bcdbf66e1ddb2ca8fc6339f8fb4101d4', 'password_reset', '2026-06-15 02:46:11', '2026-06-14 18:46:11', '2026-06-15 02:45:48'),
('b098a2551f34b47d976aea19917c59c6', 54, 'cc9af0be4cbf00227725b45fdb6904af6210521072d9b25a92764953ac3b9f8b', 'password_reset', '2026-06-14 20:02:51', NULL, '2026-06-15 03:02:51'),
('b82b713f92887493481968d3d29af616', 29, 'b64c03ca35db041df90cbe83338ddeb45ae3c635d82cfb918ad0bcc4215563cd', 'email_verify', '2026-05-20 09:36:59', NULL, '2026-05-20 17:31:59'),
('d4ad98d79852d58ef2200fc7673032a0', 30, 'a23d6e9d47345a91a66555c96dbf654b215227fc735e0f4828a01c2ffea5bdfd', 'password_reset', '2026-06-09 22:37:48', '2026-06-09 14:37:48', '2026-06-09 22:36:52'),
('e65fb1737bcc5815fc3a81aa1305b5e9', 28, '119678b6cec3aabb20352e482744d6ab19ea045f2db4e713975017529135a68c', 'email_verify', '2026-05-20 17:23:16', '2026-05-20 09:23:16', '2026-05-20 17:22:43'),
('f27b428f198ce532406794d6be847c8a', 33, '91986ea4b1bc4af7082bf5a3a5d5ea360daefecf726fea1e71858d3a9d324efa', 'email_verify', '2026-05-25 10:46:26', NULL, '2026-05-25 18:41:26'),
('f759ee7e378efb7247bec6560796b68c', 30, 'cc38222c89be50b9be1d295d2e0bf3f643d71778a44b69e3b5b74bce3fb56fd7', 'password_reset', '2026-06-15 02:45:34', '2026-06-14 18:45:33', '2026-06-15 02:44:47'),
('fb6e373ae5516bc2a1a6aad5d342a26e', 30, '3b5a2a17e5dbdf2e9c5379339635522360c9bb8923e0e414ba4c473dcf8f4406', 'password_reset', '2026-06-14 00:36:28', NULL, '2026-06-14 07:36:28');

-- --------------------------------------------------------

--
-- Table structure for table `agent_commissions`
--

CREATE TABLE `agent_commissions` (
  `commission_id` int(11) NOT NULL,
  `sale_id` int(11) NOT NULL,
  `agent_id` int(11) NOT NULL,
  `rate_applied` decimal(5,2) NOT NULL,
  `commission_amount` decimal(10,2) NOT NULL,
  `is_paid` tinyint(1) NOT NULL DEFAULT 0,
  `paid_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `agent_commissions`
--

INSERT INTO `agent_commissions` (`commission_id`, `sale_id`, `agent_id`, `rate_applied`, `commission_amount`, `is_paid`, `paid_at`, `created_at`) VALUES
(1, 1, 3, 3.00, 49440.00, 1, '2026-06-14 09:19:48', '2026-04-19 08:40:18'),
(2, 2, 2, 3.50, 83650.00, 1, '2026-06-14 09:19:48', '2026-04-19 08:40:18'),
(20, 24, 30, 3.00, 71700.00, 1, '2026-06-14 09:19:48', '2026-06-05 10:14:05'),
(21, 25, 33, 3.00, 23940.00, 1, '2026-06-14 09:19:48', '2026-06-05 17:05:32'),
(22, 26, 30, 3.00, 54000.00, 0, NULL, '2026-06-14 09:38:50'),
(23, 27, 30, 3.00, 30000.00, 0, NULL, '2026-06-14 19:18:27');

-- --------------------------------------------------------

--
-- Table structure for table `agent_details`
--

CREATE TABLE `agent_details` (
  `user_id` int(11) NOT NULL,
  `employee_number` varchar(20) NOT NULL,
  `hire_date` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `default_commission_rate` decimal(5,2) NOT NULL DEFAULT 3.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `agent_details`
--

INSERT INTO `agent_details` (`user_id`, `employee_number`, `hire_date`, `default_commission_rate`) VALUES
(2, 'EMP-2024-001', '2024-01-15 00:00:00', 3.50),
(3, 'EMP-2024-002', '2024-03-01 00:00:00', 3.00),
(28, 'EMP-2026-28', '2026-05-20 17:22:43', 3.00),
(29, 'EMP-2026-29', '2026-05-20 17:31:59', 3.00),
(30, 'EMP-2026-30', '2026-05-21 14:55:27', 3.00),
(33, 'EMP-2026-33', '2026-05-25 18:41:26', 3.00),
(50, 'EMP-50', '2026-06-13 18:05:02', 3.00);

-- --------------------------------------------------------

--
-- Table structure for table `agent_tasks`
--

CREATE TABLE `agent_tasks` (
  `task_id` int(11) NOT NULL,
  `agent_id` int(11) NOT NULL,
  `inquiry_id` int(11) DEFAULT NULL,
  `task_type` enum('follow_up','appointment','demo','document_prep','other') NOT NULL,
  `title` varchar(200) NOT NULL,
  `due_date` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `status` enum('pending','in_progress','done','cancelled') NOT NULL DEFAULT 'pending',
  `notes` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `agent_tasks`
--

INSERT INTO `agent_tasks` (`task_id`, `agent_id`, `inquiry_id`, `task_type`, `title`, `due_date`, `status`, `notes`, `created_at`) VALUES
(1, 2, 1, 'follow_up', 'Follow up on Fortuner GR inquiry — Pedro Garcia', '2025-05-05 02:00:00', 'done', 'Customer confirmed interest, awaiting financing docs.', '2026-04-19 08:40:18'),
(2, 2, NULL, 'appointment', 'Monthly review with branch manager', '2025-05-10 01:00:00', 'pending', NULL, '2026-04-19 08:40:18'),
(3, 28, NULL, 'follow_up', 'tesing', '2026-01-25 02:00:00', 'pending', NULL, '2026-06-03 16:34:10'),
(4, 28, 3, 'follow_up', 'tesing', '2026-01-25 02:00:00', 'pending', NULL, '2026-06-03 16:38:40'),
(5, 28, 10, 'follow_up', 'tesing', '2026-01-25 02:00:00', 'pending', NULL, '2026-06-03 16:38:44');

-- --------------------------------------------------------

--
-- Table structure for table `amortization_schedule`
--

CREATE TABLE `amortization_schedule` (
  `schedule_id` int(11) NOT NULL,
  `loan_id` int(11) NOT NULL,
  `month_number` int(11) NOT NULL,
  `due_date` date NOT NULL,
  `principal` decimal(12,2) NOT NULL,
  `interest` decimal(12,2) NOT NULL,
  `total_due` decimal(12,2) NOT NULL,
  `running_balance` decimal(12,2) NOT NULL,
  `status` enum('unpaid','paid','overdue') NOT NULL DEFAULT 'unpaid',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `amortization_schedule`
--

INSERT INTO `amortization_schedule` (`schedule_id`, `loan_id`, `month_number`, `due_date`, `principal`, `interest`, `total_due`, `running_balance`, `status`, `created_at`) VALUES
(1, 1, 1, '2025-05-15', 27015.12, 10358.33, 37373.45, 1884984.88, 'paid', '2026-04-19 08:40:18'),
(2, 1, 2, '2025-06-15', 27161.99, 10211.46, 37373.45, 1857822.89, 'paid', '2026-04-19 08:40:18'),
(14, 1, 3, '2026-07-19', 180957.50, 10837.30, 191794.80, 1676865.39, 'unpaid', '2026-06-04 05:59:15'),
(15, 1, 4, '2026-08-19', 182013.09, 9781.71, 191794.80, 1494852.30, 'unpaid', '2026-06-04 05:59:15'),
(16, 1, 5, '2026-09-19', 183074.83, 8719.97, 191794.80, 1311777.46, 'unpaid', '2026-06-04 05:59:15'),
(17, 1, 6, '2026-10-19', 184142.77, 7652.04, 191794.80, 1127634.70, 'unpaid', '2026-06-04 05:59:15'),
(18, 1, 7, '2026-11-19', 185216.94, 6577.87, 191794.80, 942417.76, 'unpaid', '2026-06-04 05:59:15'),
(19, 1, 8, '2026-12-19', 186297.37, 5497.44, 191794.80, 756120.39, 'unpaid', '2026-06-04 05:59:15'),
(20, 1, 9, '2027-01-19', 187384.10, 4410.70, 191794.80, 568736.29, 'unpaid', '2026-06-04 05:59:15'),
(21, 1, 10, '2027-02-19', 188477.18, 3317.63, 191794.80, 380259.12, 'unpaid', '2026-06-04 05:59:15'),
(22, 1, 11, '2027-03-19', 189576.63, 2218.18, 191794.80, 190682.49, 'unpaid', '2026-06-04 05:59:15'),
(23, 1, 12, '2027-04-19', 190682.49, 1112.31, 191794.80, 0.00, 'unpaid', '2026-06-04 05:59:15'),
(24, 2, 1, '2026-05-19', 8087.98, 541.67, 8629.64, 91912.02, 'paid', '2026-06-04 05:59:15'),
(25, 2, 2, '2026-06-19', 8131.78, 497.86, 8629.64, 83780.24, 'unpaid', '2026-06-04 05:59:15'),
(26, 2, 3, '2026-07-19', 8175.83, 453.81, 8629.64, 75604.41, 'unpaid', '2026-06-04 05:59:15'),
(27, 2, 4, '2026-08-19', 8220.12, 409.52, 8629.64, 67384.29, 'unpaid', '2026-06-04 05:59:15'),
(28, 2, 5, '2026-09-19', 8264.64, 365.00, 8629.64, 59119.65, 'unpaid', '2026-06-04 05:59:15'),
(29, 2, 6, '2026-10-19', 8309.41, 320.23, 8629.64, 50810.24, 'unpaid', '2026-06-04 05:59:15'),
(30, 2, 7, '2026-11-19', 8354.42, 275.22, 8629.64, 42455.82, 'unpaid', '2026-06-04 05:59:15'),
(31, 2, 8, '2026-12-19', 8399.67, 229.97, 8629.64, 34056.14, 'unpaid', '2026-06-04 05:59:15'),
(32, 2, 9, '2027-01-19', 8445.17, 184.47, 8629.64, 25610.97, 'unpaid', '2026-06-04 05:59:15'),
(33, 2, 10, '2027-02-19', 8490.92, 138.73, 8629.64, 17120.06, 'unpaid', '2026-06-04 05:59:15'),
(34, 2, 11, '2027-03-19', 8536.91, 92.73, 8629.64, 8583.15, 'unpaid', '2026-06-04 05:59:15'),
(35, 2, 12, '2027-04-19', 8583.15, 46.49, 8629.64, 0.00, 'unpaid', '2026-06-04 05:59:15'),
(576, 13, 1, '2026-07-05', 27053.81, 10356.67, 37410.48, 1884946.19, 'paid', '2026-06-05 10:14:05'),
(577, 13, 2, '2026-08-05', 27200.35, 10210.13, 37410.48, 1857745.84, 'paid', '2026-06-05 10:14:05'),
(578, 13, 3, '2026-09-05', 27347.69, 10062.79, 37410.48, 1830398.15, 'paid', '2026-06-05 10:14:05'),
(579, 13, 4, '2026-10-05', 27495.82, 9914.66, 37410.48, 1802902.33, 'paid', '2026-06-05 10:14:05'),
(580, 13, 5, '2026-11-05', 27644.76, 9765.72, 37410.48, 1775257.57, 'unpaid', '2026-06-05 10:14:05'),
(581, 13, 6, '2026-12-05', 27794.50, 9615.98, 37410.48, 1747463.07, 'unpaid', '2026-06-05 10:14:05'),
(582, 13, 7, '2027-01-05', 27945.06, 9465.42, 37410.48, 1719518.01, 'unpaid', '2026-06-05 10:14:05'),
(583, 13, 8, '2027-02-05', 28096.42, 9314.06, 37410.48, 1691421.59, 'unpaid', '2026-06-05 10:14:05'),
(584, 13, 9, '2027-03-05', 28248.61, 9161.87, 37410.48, 1663172.98, 'unpaid', '2026-06-05 10:14:05'),
(585, 13, 10, '2027-04-05', 28401.63, 9008.85, 37410.48, 1634771.35, 'unpaid', '2026-06-05 10:14:05'),
(586, 13, 11, '2027-05-05', 28555.47, 8855.01, 37410.48, 1606215.88, 'unpaid', '2026-06-05 10:14:05'),
(587, 13, 12, '2027-06-05', 28710.14, 8700.34, 37410.48, 1577505.74, 'unpaid', '2026-06-05 10:14:05'),
(588, 13, 13, '2027-07-05', 28865.66, 8544.82, 37410.48, 1548640.08, 'unpaid', '2026-06-05 10:14:05'),
(589, 13, 14, '2027-08-05', 29022.01, 8388.47, 37410.48, 1519618.07, 'unpaid', '2026-06-05 10:14:05'),
(590, 13, 15, '2027-09-05', 29179.22, 8231.26, 37410.48, 1490438.85, 'unpaid', '2026-06-05 10:14:05'),
(591, 13, 16, '2027-10-05', 29337.27, 8073.21, 37410.48, 1461101.58, 'unpaid', '2026-06-05 10:14:05'),
(592, 13, 17, '2027-11-05', 29496.18, 7914.30, 37410.48, 1431605.40, 'unpaid', '2026-06-05 10:14:05'),
(593, 13, 18, '2027-12-05', 29655.95, 7754.53, 37410.48, 1401949.45, 'unpaid', '2026-06-05 10:14:05'),
(594, 13, 19, '2028-01-05', 29816.59, 7593.89, 37410.48, 1372132.86, 'unpaid', '2026-06-05 10:14:05'),
(595, 13, 20, '2028-02-05', 29978.09, 7432.39, 37410.48, 1342154.77, 'unpaid', '2026-06-05 10:14:05'),
(596, 13, 21, '2028-03-05', 30140.47, 7270.01, 37410.48, 1312014.30, 'unpaid', '2026-06-05 10:14:05'),
(597, 13, 22, '2028-04-05', 30303.74, 7106.74, 37410.48, 1281710.56, 'unpaid', '2026-06-05 10:14:05'),
(598, 13, 23, '2028-05-05', 30467.88, 6942.60, 37410.48, 1251242.68, 'unpaid', '2026-06-05 10:14:05'),
(599, 13, 24, '2028-06-05', 30632.92, 6777.56, 37410.48, 1220609.76, 'unpaid', '2026-06-05 10:14:05'),
(600, 13, 25, '2028-07-05', 30798.84, 6611.64, 37410.48, 1189810.92, 'unpaid', '2026-06-05 10:14:05'),
(601, 13, 26, '2028-08-05', 30965.67, 6444.81, 37410.48, 1158845.25, 'unpaid', '2026-06-05 10:14:05'),
(602, 13, 27, '2028-09-05', 31133.40, 6277.08, 37410.48, 1127711.85, 'unpaid', '2026-06-05 10:14:05'),
(603, 13, 28, '2028-10-05', 31302.04, 6108.44, 37410.48, 1096409.81, 'unpaid', '2026-06-05 10:14:05'),
(604, 13, 29, '2028-11-05', 31471.59, 5938.89, 37410.48, 1064938.22, 'unpaid', '2026-06-05 10:14:05'),
(605, 13, 30, '2028-12-05', 31642.06, 5768.42, 37410.48, 1033296.16, 'unpaid', '2026-06-05 10:14:05'),
(606, 13, 31, '2029-01-05', 31813.46, 5597.02, 37410.48, 1001482.70, 'unpaid', '2026-06-05 10:14:05'),
(607, 13, 32, '2029-02-05', 31985.78, 5424.70, 37410.48, 969496.92, 'unpaid', '2026-06-05 10:14:05'),
(608, 13, 33, '2029-03-05', 32159.04, 5251.44, 37410.48, 937337.88, 'unpaid', '2026-06-05 10:14:05'),
(609, 13, 34, '2029-04-05', 32333.23, 5077.25, 37410.48, 905004.65, 'unpaid', '2026-06-05 10:14:05'),
(610, 13, 35, '2029-05-05', 32508.37, 4902.11, 37410.48, 872496.28, 'unpaid', '2026-06-05 10:14:05'),
(611, 13, 36, '2029-06-05', 32684.46, 4726.02, 37410.48, 839811.82, 'unpaid', '2026-06-05 10:14:05'),
(612, 13, 37, '2029-07-05', 32861.50, 4548.98, 37410.48, 806950.32, 'unpaid', '2026-06-05 10:14:05'),
(613, 13, 38, '2029-08-05', 33039.50, 4370.98, 37410.48, 773910.82, 'unpaid', '2026-06-05 10:14:05'),
(614, 13, 39, '2029-09-05', 33218.46, 4192.02, 37410.48, 740692.36, 'unpaid', '2026-06-05 10:14:05'),
(615, 13, 40, '2029-10-05', 33398.40, 4012.08, 37410.48, 707293.96, 'unpaid', '2026-06-05 10:14:05'),
(616, 13, 41, '2029-11-05', 33579.30, 3831.18, 37410.48, 673714.66, 'unpaid', '2026-06-05 10:14:05'),
(617, 13, 42, '2029-12-05', 33761.19, 3649.29, 37410.48, 639953.47, 'unpaid', '2026-06-05 10:14:05'),
(618, 13, 43, '2030-01-05', 33944.07, 3466.41, 37410.48, 606009.40, 'unpaid', '2026-06-05 10:14:05'),
(619, 13, 44, '2030-02-05', 34127.93, 3282.55, 37410.48, 571881.47, 'unpaid', '2026-06-05 10:14:05'),
(620, 13, 45, '2030-03-05', 34312.79, 3097.69, 37410.48, 537568.68, 'unpaid', '2026-06-05 10:14:05'),
(621, 13, 46, '2030-04-05', 34498.65, 2911.83, 37410.48, 503070.03, 'unpaid', '2026-06-05 10:14:05'),
(622, 13, 47, '2030-05-05', 34685.52, 2724.96, 37410.48, 468384.51, 'unpaid', '2026-06-05 10:14:05'),
(623, 13, 48, '2030-06-05', 34873.40, 2537.08, 37410.48, 433511.11, 'unpaid', '2026-06-05 10:14:05'),
(624, 13, 49, '2030-07-05', 35062.29, 2348.19, 37410.48, 398448.82, 'unpaid', '2026-06-05 10:14:05'),
(625, 13, 50, '2030-08-05', 35252.22, 2158.26, 37410.48, 363196.60, 'unpaid', '2026-06-05 10:14:05'),
(626, 13, 51, '2030-09-05', 35443.17, 1967.31, 37410.48, 327753.43, 'unpaid', '2026-06-05 10:14:05'),
(627, 13, 52, '2030-10-05', 35635.15, 1775.33, 37410.48, 292118.28, 'unpaid', '2026-06-05 10:14:05'),
(628, 13, 53, '2030-11-05', 35828.17, 1582.31, 37410.48, 256290.11, 'unpaid', '2026-06-05 10:14:05'),
(629, 13, 54, '2030-12-05', 36022.24, 1388.24, 37410.48, 220267.87, 'unpaid', '2026-06-05 10:14:05'),
(630, 13, 55, '2031-01-05', 36217.36, 1193.12, 37410.48, 184050.51, 'unpaid', '2026-06-05 10:14:05'),
(631, 13, 56, '2031-02-05', 36413.54, 996.94, 37410.48, 147636.97, 'unpaid', '2026-06-05 10:14:05'),
(632, 13, 57, '2031-03-05', 36610.78, 799.70, 37410.48, 111026.19, 'unpaid', '2026-06-05 10:14:05'),
(633, 13, 58, '2031-04-05', 36809.09, 601.39, 37410.48, 74217.10, 'unpaid', '2026-06-05 10:14:05'),
(634, 13, 59, '2031-05-05', 37008.47, 402.01, 37410.48, 37208.63, 'unpaid', '2026-06-05 10:14:05'),
(635, 13, 60, '2031-06-05', 37208.63, 201.55, 37410.18, 0.00, 'unpaid', '2026-06-05 10:14:05');

-- --------------------------------------------------------

--
-- Table structure for table `audit_logs`
--

CREATE TABLE `audit_logs` (
  `log_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `action` varchar(100) NOT NULL,
  `table_name` varchar(50) NOT NULL,
  `record_id` int(11) DEFAULT NULL,
  `old_value` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`old_value`)),
  `new_value` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`new_value`)),
  `ip_address` varchar(45) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `audit_logs`
--

INSERT INTO `audit_logs` (`log_id`, `user_id`, `action`, `table_name`, `record_id`, `old_value`, `new_value`, `ip_address`, `created_at`) VALUES
(1, 1, 'UPDATE', 'vehicles', 4, '{\"status\":\"available\"}', '{\"status\":\"reserved\"}', '192.168.1.10', '2026-04-19 08:40:18'),
(2, 1, 'INSERT', 'sales', 2, NULL, '{\"sale_id\":2,\"status\":\"active\"}', '192.168.1.10', '2026-04-19 08:40:18'),
(3, 6, 'POST', 'users, access_tokens, agent_details', 20, NULL, NULL, '127.0.0.1', '2026-05-20 10:26:06'),
(4, 6, 'POST', 'users, access_tokens, agent_details', 21, NULL, NULL, '127.0.0.1', '2026-05-20 16:52:51'),
(5, 6, 'POST', 'users, access_tokens, agent_details', 28, NULL, NULL, '127.0.0.1', '2026-05-20 17:22:49'),
(6, 6, 'POST', 'users, access_tokens, agent_details', 29, NULL, NULL, '127.0.0.1', '2026-05-20 17:32:04'),
(7, 6, 'POST', 'users, access_tokens, agent_details', 30, NULL, NULL, '192.168.1.46', '2026-05-21 14:55:32'),
(8, 6, 'POST', 'customer', 31, NULL, NULL, '192.168.1.46', '2026-05-25 18:39:48'),
(9, 6, 'POST', 'users, access_tokens, agent_details', 33, NULL, NULL, '192.168.1.46', '2026-05-25 18:41:27'),
(10, NULL, 'POST', 'inquiries', 7, NULL, NULL, '192.168.1.46', '2026-05-28 21:05:20'),
(11, NULL, 'POST', 'inquiries', 9, NULL, '{\"guest_name\": \"lance kit gom-os\", \"guest_email\": \"lancegomoa@gmail.com\", \"guest_number\": null}', '192.168.1.46', '2026-05-28 21:09:34'),
(12, 28, 'PUT', 'inquiries', 3, 'null', '28', '192.168.1.46', '2026-05-30 13:07:25'),
(13, 6, 'POST', 'sales', 7, NULL, '{\"vehicle_id\": 3, \"customer_id\": 5, \"agent_id\": 3, \"payment_type\": \"cash\", \"selling_price\": 1800000.0, \"status\": \"pending\"}', '192.168.1.46', '2026-06-05 06:31:22'),
(15, 6, 'POST', 'sales', 9, NULL, '{\"vehicle_id\": 3, \"customer_id\": 5, \"agent_id\": 3, \"payment_type\": \"cash\", \"selling_price\": 1800000.0, \"status\": \"pending\"}', '192.168.1.46', '2026-06-05 06:32:16'),
(16, NULL, 'POST', 'inquiries', 12, NULL, '{\"guest_name\": \"Tanjiro Kamado\", \"guest_email\": \"tanjirokamado22222@gmail.com\", \"guest_number\": null}', '192.168.1.46', '2026-06-05 08:55:43'),
(17, 6, 'PUT', 'inquiries', 12, '\"open\"', '{\"agent_id\": 28, \"status\": \"assigned\"}', '192.168.1.46', '2026-06-05 08:56:19'),
(18, 6, 'POST', 'sales', 13, NULL, '{\"vehicle_id\": 1, \"customer_id\": 39, \"agent_id\": 28, \"payment_type\": \"installment\", \"selling_price\": 2390000.0, \"status\": \"pending\"}', '192.168.1.46', '2026-06-05 08:57:05'),
(19, 6, 'PUT', 'loan_details', 3, '\"pending\"', '{\"bank_approval_status\": \"approved\"}', '192.168.1.46', '2026-06-05 09:03:23'),
(20, NULL, 'POST', 'inquiries', 13, NULL, '{\"guest_name\": \"Tanjiro Kamado\", \"guest_email\": \"tanjiro22222@gmail.com\", \"guest_number\": null}', '192.168.1.46', '2026-06-05 09:12:37'),
(21, NULL, 'POST', 'inquiries', 14, NULL, '{\"guest_name\": \"Tanjiro Kamado\", \"guest_email\": \"tanjiro22222@gmail.com\", \"guest_number\": null}', '192.168.1.46', '2026-06-05 09:12:55'),
(22, 6, 'PUT', 'inquiries', 14, '\"open\"', '{\"agent_id\": 28, \"status\": \"assigned\"}', '192.168.1.46', '2026-06-05 09:13:42'),
(23, 6, 'POST', 'sales', 14, NULL, '{\"vehicle_id\": 1, \"customer_id\": 40, \"agent_id\": 28, \"payment_type\": \"installment\", \"selling_price\": 2390000.0, \"status\": \"pending\"}', '192.168.1.46', '2026-06-05 09:14:44'),
(24, 6, 'PUT', 'loan_details', 4, '\"pending\"', '{\"bank_approval_status\": \"approved\"}', '192.168.1.46', '2026-06-05 09:14:44'),
(25, NULL, 'POST', 'inquiries', 15, NULL, '{\"guest_name\": \"Tanjiro Kamado\", \"guest_email\": \"tanjirokamado22222@gmail.com\", \"guest_number\": null}', '192.168.1.46', '2026-06-05 09:20:26'),
(26, 6, 'PUT', 'inquiries', 15, '\"open\"', '{\"agent_id\": 28, \"status\": \"assigned\"}', '192.168.1.46', '2026-06-05 09:22:01'),
(27, 6, 'POST', 'sales', 16, NULL, '{\"vehicle_id\": 1, \"customer_id\": 28, \"agent_id\": 28, \"payment_type\": \"installment\", \"selling_price\": 2390000.0, \"status\": \"pending\"}', '192.168.1.46', '2026-06-05 09:22:35'),
(28, 6, 'PUT', 'loan_details', 5, '\"pending\"', '{\"bank_approval_status\": \"approved\"}', '192.168.1.46', '2026-06-05 09:23:10'),
(29, NULL, 'POST', 'inquiries', 16, NULL, '{\"guest_name\": \"Tanjiro Kamado\", \"guest_email\": \"tanjirokamado22222@gmail.com\", \"guest_number\": null}', '192.168.1.46', '2026-06-05 09:25:37'),
(30, 6, 'PUT', 'inquiries', 16, '\"open\"', '{\"agent_id\": 30, \"status\": \"assigned\"}', '192.168.1.46', '2026-06-05 09:25:40'),
(31, 6, 'POST', 'sales', 17, NULL, '{\"vehicle_id\": 1, \"customer_id\": 28, \"agent_id\": 30, \"payment_type\": \"installment\", \"selling_price\": 2390000.0, \"status\": \"pending\"}', '192.168.1.46', '2026-06-05 09:25:43'),
(32, 6, 'PUT', 'loan_details', 6, '\"pending\"', '{\"bank_approval_status\": \"approved\"}', '192.168.1.46', '2026-06-05 09:25:43'),
(33, NULL, 'POST', 'inquiries', 17, NULL, '{\"guest_name\": \"Tanjiro Kamado\", \"guest_email\": \"tanjirokamado22222@gmail.com\", \"guest_number\": null}', '192.168.1.46', '2026-06-05 09:45:05'),
(34, 6, 'PUT', 'inquiries', 17, '\"open\"', '{\"agent_id\": 30, \"status\": \"assigned\"}', '192.168.1.46', '2026-06-05 09:45:12'),
(35, 6, 'POST', 'sales', 18, NULL, '{\"vehicle_id\": 1, \"customer_id\": 28, \"agent_id\": 30, \"payment_type\": \"installment\", \"selling_price\": 2390000.0, \"status\": \"pending\"}', '192.168.1.46', '2026-06-05 09:45:26'),
(36, NULL, 'POST', 'inquiries', 18, NULL, '{\"guest_name\": \"Tanjiro Kamado\", \"guest_email\": \"tanjirokamado22222@gmail.com\", \"guest_number\": null}', '192.168.1.46', '2026-06-05 09:46:17'),
(37, 6, 'POST', 'sales', 19, NULL, '{\"vehicle_id\": 1, \"customer_id\": 28, \"agent_id\": 30, \"payment_type\": \"installment\", \"selling_price\": 2390000.0, \"status\": \"pending\"}', '192.168.1.46', '2026-06-05 09:46:19'),
(38, 6, 'PUT', 'loan_details', 8, '\"pending\"', '{\"bank_approval_status\": \"approved\"}', '192.168.1.46', '2026-06-05 09:46:32'),
(39, 6, 'POST', 'insurance_records', 3, NULL, '{\"provider\": \"Prudential Guarantee\", \"policy_number\": \"PRU-2026-1234\", \"coverage_start\": \"2026-06-05\", \"coverage_end\": \"2027-06-05\", \"coverage_type\": \"Comprehensive\"}', '192.168.1.46', '2026-06-05 09:46:35'),
(40, NULL, 'POST', 'inquiries', 19, NULL, '{\"guest_name\": \"Tanjiro Kamado\", \"guest_email\": \"tanjirokamado22222@gmail.com\", \"guest_number\": null}', '192.168.1.46', '2026-06-05 09:54:14'),
(41, 6, 'PUT', 'inquiries', 19, '\"open\"', '{\"agent_id\": 30, \"status\": \"assigned\"}', '192.168.1.46', '2026-06-05 09:54:18'),
(42, 6, 'POST', 'sales', 20, NULL, '{\"vehicle_id\": 1, \"customer_id\": 41, \"agent_id\": 30, \"payment_type\": \"installment\", \"selling_price\": 2390000.0, \"status\": \"pending\"}', '192.168.1.46', '2026-06-05 09:54:24'),
(43, 6, 'PUT', 'loan_details', 9, '\"pending\"', '{\"bank_approval_status\": \"approved\"}', '192.168.1.46', '2026-06-05 09:55:40'),
(44, NULL, 'POST', 'inquiries', 20, NULL, '{\"guest_name\": \"Tanjiro Kamado\", \"guest_email\": \"tanjirokamado22222@gmail.com\", \"guest_number\": null}', '192.168.1.46', '2026-06-05 09:59:04'),
(45, 6, 'PUT', 'inquiries', 20, '\"open\"', '{\"agent_id\": 30, \"status\": \"assigned\"}', '192.168.1.46', '2026-06-05 09:59:06'),
(46, 6, 'POST', 'sales', 21, NULL, '{\"vehicle_id\": 1, \"customer_id\": 42, \"agent_id\": 30, \"payment_type\": \"installment\", \"selling_price\": 2390000.0, \"status\": \"pending\"}', '192.168.1.46', '2026-06-05 09:59:12'),
(47, NULL, 'POST', 'inquiries', 21, NULL, '{\"guest_name\": \"Tanjiro Kamado\", \"guest_email\": \"tanjirokamado22222@gmail.com\", \"guest_number\": null}', '192.168.1.46', '2026-06-05 10:06:36'),
(48, 6, 'PUT', 'inquiries', 21, '\"open\"', '{\"agent_id\": 30, \"status\": \"assigned\"}', '192.168.1.46', '2026-06-05 10:06:39'),
(49, 6, 'POST', 'sales', 22, NULL, '{\"vehicle_id\": 1, \"customer_id\": 43, \"agent_id\": 30, \"payment_type\": \"installment\", \"selling_price\": 2390000.0, \"status\": \"pending\"}', '192.168.1.46', '2026-06-05 10:07:35'),
(50, NULL, 'POST', 'inquiries', 22, NULL, '{\"guest_name\": \"Tanjiro Kamado\", \"guest_email\": \"tanjirokamado22222@gmail.com\", \"guest_number\": null}', '192.168.1.46', '2026-06-05 10:08:08'),
(51, 6, 'PUT', 'inquiries', 22, '\"open\"', '{\"agent_id\": 30, \"status\": \"assigned\"}', '192.168.1.46', '2026-06-05 10:08:11'),
(52, NULL, 'POST', 'inquiries', 23, NULL, '{\"guest_name\": \"Tanjiro Kamado\", \"guest_email\": \"tanjirokamado22222@gmail.com\", \"guest_number\": null}', '192.168.1.46', '2026-06-05 10:11:01'),
(53, 6, 'PUT', 'inquiries', 23, '\"open\"', '{\"agent_id\": 30, \"status\": \"assigned\"}', '192.168.1.46', '2026-06-05 10:11:08'),
(54, 6, 'POST', 'sales', 23, NULL, '{\"vehicle_id\": 1, \"customer_id\": 45, \"agent_id\": 30, \"payment_type\": \"installment\", \"selling_price\": 2390000.0, \"status\": \"pending\"}', '192.168.1.46', '2026-06-05 10:12:08'),
(55, NULL, 'POST', 'inquiries', 24, NULL, '{\"guest_name\": \"Tanjiro Kamado\", \"guest_email\": \"tanjirokamado22222@gmail.com\", \"guest_number\": null}', '192.168.1.46', '2026-06-05 10:13:05'),
(56, 6, 'PUT', 'inquiries', 24, '\"open\"', '{\"agent_id\": 30, \"status\": \"assigned\"}', '192.168.1.46', '2026-06-05 10:13:09'),
(57, NULL, 'POST', 'inquiries', 25, NULL, '{\"guest_name\": \"Tanjiro Kamado\", \"guest_email\": \"tanjirokamado22222@gmail.com\", \"guest_number\": null}', '192.168.1.46', '2026-06-05 10:13:51'),
(58, 6, 'PUT', 'inquiries', 25, '\"open\"', '{\"agent_id\": 30, \"status\": \"assigned\"}', '192.168.1.46', '2026-06-05 10:13:58'),
(59, 6, 'POST', 'sales', 24, NULL, '{\"vehicle_id\": 1, \"customer_id\": 46, \"agent_id\": 30, \"payment_type\": \"installment\", \"selling_price\": 2390000.0, \"status\": \"pending\"}', '192.168.1.46', '2026-06-05 10:14:05'),
(60, 6, 'PUT', 'loan_details', 13, '\"pending\"', '{\"bank_approval_status\": \"approved\"}', '192.168.1.46', '2026-06-05 10:14:18'),
(61, 6, 'POST', 'insurance_records', 4, NULL, '{\"provider\": \"Prudential\", \"policy_number\": \"PRU-001\", \"coverage_start\": \"2026-06-05\", \"coverage_end\": \"2027-06-05\", \"coverage_type\": \"Comprehensive\"}', '192.168.1.46', '2026-06-05 10:14:21'),
(62, 6, 'PUT', 'sales', 24, '\"pending\"', '{\"status\": \"completed\"}', '192.168.1.46', '2026-06-05 10:14:24'),
(63, 6, 'PUT', 'system_settings', 1, '3.00', '3.5', '192.168.1.46', '2026-06-06 12:39:40'),
(64, 6, 'PUT', 'users', 30, '{\"user_id\": 30, \"username\": \"gianna252\", \"hashed_password\": \"scrypt:32768:8:1$DeeMbEG9atFv6rM8$017ea236fea113b1cd58ef02e88b23dc4b3b8db5736e2fa1ac055cce6f8c76261fff9846dd1b083ecb47e7c08b1040769d8ce0c8e0208c4a62e118d8041a7156\", \"email\": \"lancegomoa@gmail.com\", \"role\": \"agent\", \"email_verified\": 1, \"is_active\": 0, \"last_login\": \"2026-06-10 07:27:08\", \"created_at\": \"2026-05-21 22:55:27\"}', '{\"user_id\": 30, \"username\": \"gianna252\", \"hashed_password\": \"scrypt:32768:8:1$DeeMbEG9atFv6rM8$017ea236fea113b1cd58ef02e88b23dc4b3b8db5736e2fa1ac055cce6f8c76261fff9846dd1b083ecb47e7c08b1040769d8ce0c8e0208c4a62e118d8041a7156\", \"email\": \"lancegomoa@gmail.com\", \"role\": \"agent\", \"email_verified\": 1, \"is_active\": 1, \"last_login\": \"2026-06-10 07:27:08\", \"created_at\": \"2026-05-21 22:55:27\"}', '192.168.1.46', '2026-06-10 00:00:06'),
(65, 6, 'PUT', 'users', 30, '{\"user_id\": 30, \"username\": \"gianna252\", \"hashed_password\": \"scrypt:32768:8:1$DeeMbEG9atFv6rM8$017ea236fea113b1cd58ef02e88b23dc4b3b8db5736e2fa1ac055cce6f8c76261fff9846dd1b083ecb47e7c08b1040769d8ce0c8e0208c4a62e118d8041a7156\", \"email\": \"lancegomoa@gmail.com\", \"role\": \"agent\", \"email_verified\": 1, \"is_active\": 1, \"last_login\": \"2026-06-10 07:27:08\", \"created_at\": \"2026-05-21 22:55:27\"}', '{\"user_id\": 30, \"username\": \"gianna252\", \"hashed_password\": \"scrypt:32768:8:1$DeeMbEG9atFv6rM8$017ea236fea113b1cd58ef02e88b23dc4b3b8db5736e2fa1ac055cce6f8c76261fff9846dd1b083ecb47e7c08b1040769d8ce0c8e0208c4a62e118d8041a7156\", \"email\": \"lancegomoa@gmail.com\", \"role\": \"agent\", \"email_verified\": 1, \"is_active\": 0, \"last_login\": \"2026-06-10 07:27:08\", \"created_at\": \"2026-05-21 22:55:27\"}', '192.168.1.46', '2026-06-10 00:00:08'),
(66, 6, 'PUT', 'users', 30, '{\"user_id\": 30, \"username\": \"gianna252\", \"hashed_password\": \"scrypt:32768:8:1$DeeMbEG9atFv6rM8$017ea236fea113b1cd58ef02e88b23dc4b3b8db5736e2fa1ac055cce6f8c76261fff9846dd1b083ecb47e7c08b1040769d8ce0c8e0208c4a62e118d8041a7156\", \"email\": \"lancegomoa@gmail.com\", \"role\": \"agent\", \"email_verified\": 1, \"is_active\": 0, \"last_login\": \"2026-06-10 07:27:08\", \"created_at\": \"2026-05-21 22:55:27\"}', '{\"user_id\": 30, \"username\": \"gianna252\", \"hashed_password\": \"scrypt:32768:8:1$DeeMbEG9atFv6rM8$017ea236fea113b1cd58ef02e88b23dc4b3b8db5736e2fa1ac055cce6f8c76261fff9846dd1b083ecb47e7c08b1040769d8ce0c8e0208c4a62e118d8041a7156\", \"email\": \"lancegomoa@gmail.com\", \"role\": \"agent\", \"email_verified\": 1, \"is_active\": 1, \"last_login\": \"2026-06-10 07:27:08\", \"created_at\": \"2026-05-21 22:55:27\"}', '192.168.1.46', '2026-06-10 00:00:09'),
(67, 6, 'PUT', 'users', 30, '{\"user_id\": 30, \"username\": \"gianna252\", \"hashed_password\": \"scrypt:32768:8:1$DeeMbEG9atFv6rM8$017ea236fea113b1cd58ef02e88b23dc4b3b8db5736e2fa1ac055cce6f8c76261fff9846dd1b083ecb47e7c08b1040769d8ce0c8e0208c4a62e118d8041a7156\", \"email\": \"lancegomoa@gmail.com\", \"role\": \"agent\", \"email_verified\": 1, \"is_active\": 1, \"last_login\": \"2026-06-10 07:27:08\", \"created_at\": \"2026-05-21 22:55:27\"}', '{\"user_id\": 30, \"username\": \"gianna252\", \"hashed_password\": \"scrypt:32768:8:1$DeeMbEG9atFv6rM8$017ea236fea113b1cd58ef02e88b23dc4b3b8db5736e2fa1ac055cce6f8c76261fff9846dd1b083ecb47e7c08b1040769d8ce0c8e0208c4a62e118d8041a7156\", \"email\": \"lancegomoa@gmail.com\", \"role\": \"agent\", \"email_verified\": 1, \"is_active\": 0, \"last_login\": \"2026-06-10 07:27:08\", \"created_at\": \"2026-05-21 22:55:27\"}', '192.168.1.46', '2026-06-10 00:00:10'),
(69, 49, 'PUT estimate', 'service_bookings', 1, NULL, NULL, '192.168.1.46', '2026-06-10 05:12:22'),
(70, 49, 'PUT transmit-estimate', 'service_bookings', 1, NULL, NULL, '192.168.1.46', '2026-06-10 05:12:23'),
(71, 6, 'PUT', 'users', 37, '{\"user_id\": 37, \"username\": \"cust_angela\", \"hashed_password\": \"scrypt:32768:8:1$XJXGJKB51UK4PCPx$52c93db88bb15af1326dc508d8ca0af982a82087148b5cd061da31d95e8a5f30ea150680679ea46b80a0658d0bbf8c20e446b4f78b3aed1b5d4abf322abfc2ca\", \"email\": \"angela.v@email.com\", \"role\": \"customer\", \"email_verified\": 1, \"is_active\": 0, \"last_login\": \"2026-06-10 13:14:12\", \"created_at\": \"2026-06-03 23:49:24\"}', '{\"user_id\": 37, \"username\": \"cust_angela\", \"hashed_password\": \"scrypt:32768:8:1$XJXGJKB51UK4PCPx$52c93db88bb15af1326dc508d8ca0af982a82087148b5cd061da31d95e8a5f30ea150680679ea46b80a0658d0bbf8c20e446b4f78b3aed1b5d4abf322abfc2ca\", \"email\": \"angela.v@email.com\", \"role\": \"customer\", \"email_verified\": 1, \"is_active\": 1, \"last_login\": \"2026-06-10 13:14:12\", \"created_at\": \"2026-06-03 23:49:24\"}', '192.168.1.46', '2026-06-10 05:16:49'),
(72, 6, 'PUT', 'users', 48, '{\"user_id\": 48, \"username\": \"finance_staff1\", \"hashed_password\": \"scrypt:32768:8:1$NNlwjVpq9pSqzz7A$de47ab6719bba4996237e6fcd40997883ab55af87c44ebe5b78883220412a56d7493fbd23ecc67345ac9300a12b1f75fdd7640c20927d48678079f608af40a31\", \"email\": \"finance@automatik.com\", \"role\": \"finance_staff\", \"email_verified\": 1, \"is_active\": 0, \"last_login\": \"2026-06-10 13:10:24\", \"created_at\": \"2026-06-10 12:53:07\"}', '{\"user_id\": 48, \"username\": \"finance_staff1\", \"hashed_password\": \"scrypt:32768:8:1$NNlwjVpq9pSqzz7A$de47ab6719bba4996237e6fcd40997883ab55af87c44ebe5b78883220412a56d7493fbd23ecc67345ac9300a12b1f75fdd7640c20927d48678079f608af40a31\", \"email\": \"finance@automatik.com\", \"role\": \"finance_staff\", \"email_verified\": 1, \"is_active\": 1, \"last_login\": \"2026-06-10 13:10:24\", \"created_at\": \"2026-06-10 12:53:07\"}', '192.168.1.46', '2026-06-10 05:16:49'),
(73, 6, 'PUT', 'users', 49, '{\"user_id\": 49, \"username\": \"advisor1\", \"hashed_password\": \"scrypt:32768:8:1$s9mnWfl9hKX6v0ji$bc47436a328793ce2b88a358d7b108a537d7a66d2b1a74101c0b2be81dc8ca8b69bc1b21adf1fcc4d879b7bda9fba6ad6a112d81f9a25562ba7c39cc14cac704\", \"email\": \"advisor@automatik.com\", \"role\": \"service_advisor\", \"email_verified\": 1, \"is_active\": 0, \"last_login\": \"2026-06-10 13:13:01\", \"created_at\": \"2026-06-10 12:53:07\"}', '{\"user_id\": 49, \"username\": \"advisor1\", \"hashed_password\": \"scrypt:32768:8:1$s9mnWfl9hKX6v0ji$bc47436a328793ce2b88a358d7b108a537d7a66d2b1a74101c0b2be81dc8ca8b69bc1b21adf1fcc4d879b7bda9fba6ad6a112d81f9a25562ba7c39cc14cac704\", \"email\": \"advisor@automatik.com\", \"role\": \"service_advisor\", \"email_verified\": 1, \"is_active\": 1, \"last_login\": \"2026-06-10 13:13:01\", \"created_at\": \"2026-06-10 12:53:07\"}', '192.168.1.46', '2026-06-10 05:16:49'),
(74, 6, 'PUT', 'users', 48, '{\"user_id\": 48, \"username\": \"finance_staff1\", \"hashed_password\": \"scrypt:32768:8:1$NNlwjVpq9pSqzz7A$de47ab6719bba4996237e6fcd40997883ab55af87c44ebe5b78883220412a56d7493fbd23ecc67345ac9300a12b1f75fdd7640c20927d48678079f608af40a31\", \"email\": \"finance@automatik.com\", \"role\": \"finance_staff\", \"email_verified\": 1, \"is_active\": 1, \"last_login\": \"2026-06-10 13:10:24\", \"created_at\": \"2026-06-10 12:53:07\"}', '{\"user_id\": 48, \"username\": \"finance_staff1\", \"hashed_password\": \"scrypt:32768:8:1$NNlwjVpq9pSqzz7A$de47ab6719bba4996237e6fcd40997883ab55af87c44ebe5b78883220412a56d7493fbd23ecc67345ac9300a12b1f75fdd7640c20927d48678079f608af40a31\", \"email\": \"finance@automatik.com\", \"role\": \"finance_staff\", \"email_verified\": 1, \"is_active\": 0, \"last_login\": \"2026-06-10 13:10:24\", \"created_at\": \"2026-06-10 12:53:07\"}', '192.168.1.46', '2026-06-10 05:17:16'),
(75, 48, 'PUT', 'loan_details', 2, '\"pending\"', '{\"bank_approval_status\": \"approved\"}', '192.168.1.46', '2026-06-10 05:19:06'),
(76, 6, 'PUT', 'users', 30, '{\"user_id\": 30, \"username\": \"gianna252\", \"hashed_password\": \"scrypt:32768:8:1$DeeMbEG9atFv6rM8$017ea236fea113b1cd58ef02e88b23dc4b3b8db5736e2fa1ac055cce6f8c76261fff9846dd1b083ecb47e7c08b1040769d8ce0c8e0208c4a62e118d8041a7156\", \"email\": \"lancegomoa@gmail.com\", \"role\": \"agent\", \"email_verified\": 1, \"is_active\": 1, \"last_login\": \"2026-06-10 07:27:08\", \"created_at\": \"2026-05-21 22:55:27\"}', '{\"user_id\": 30, \"username\": \"gianna252\", \"hashed_password\": \"scrypt:32768:8:1$DeeMbEG9atFv6rM8$017ea236fea113b1cd58ef02e88b23dc4b3b8db5736e2fa1ac055cce6f8c76261fff9846dd1b083ecb47e7c08b1040769d8ce0c8e0208c4a62e118d8041a7156\", \"email\": \"lancegomoa@gmail.com\", \"role\": \"agent\", \"email_verified\": 1, \"is_active\": 0, \"last_login\": \"2026-06-10 07:27:08\", \"created_at\": \"2026-05-21 22:55:27\"}', '192.168.1.46', '2026-06-10 05:21:04'),
(77, 6, 'PUT', 'users', 30, '{\"user_id\": 30, \"username\": \"gianna252\", \"hashed_password\": \"scrypt:32768:8:1$DeeMbEG9atFv6rM8$017ea236fea113b1cd58ef02e88b23dc4b3b8db5736e2fa1ac055cce6f8c76261fff9846dd1b083ecb47e7c08b1040769d8ce0c8e0208c4a62e118d8041a7156\", \"email\": \"lancegomoa@gmail.com\", \"role\": \"agent\", \"email_verified\": 1, \"is_active\": 1, \"last_login\": \"2026-06-10 13:22:36\", \"created_at\": \"2026-05-21 22:55:27\"}', '{\"user_id\": 30, \"username\": \"gianna252\", \"hashed_password\": \"scrypt:32768:8:1$DeeMbEG9atFv6rM8$017ea236fea113b1cd58ef02e88b23dc4b3b8db5736e2fa1ac055cce6f8c76261fff9846dd1b083ecb47e7c08b1040769d8ce0c8e0208c4a62e118d8041a7156\", \"email\": \"lancegomoa@gmail.com\", \"role\": \"agent\", \"email_verified\": 1, \"is_active\": 0, \"last_login\": \"2026-06-10 13:22:36\", \"created_at\": \"2026-05-21 22:55:27\"}', '192.168.1.46', '2026-06-10 05:22:57'),
(78, 6, 'PUT', 'users', 30, '{\"user_id\": 30, \"username\": \"gianna252\", \"hashed_password\": \"scrypt:32768:8:1$DeeMbEG9atFv6rM8$017ea236fea113b1cd58ef02e88b23dc4b3b8db5736e2fa1ac055cce6f8c76261fff9846dd1b083ecb47e7c08b1040769d8ce0c8e0208c4a62e118d8041a7156\", \"email\": \"lancegomoa@gmail.com\", \"role\": \"agent\", \"email_verified\": 1, \"is_active\": 0, \"last_login\": \"2026-06-10 13:22:36\", \"created_at\": \"2026-05-21 22:55:27\"}', '{\"user_id\": 30, \"username\": \"gianna252\", \"hashed_password\": \"scrypt:32768:8:1$DeeMbEG9atFv6rM8$017ea236fea113b1cd58ef02e88b23dc4b3b8db5736e2fa1ac055cce6f8c76261fff9846dd1b083ecb47e7c08b1040769d8ce0c8e0208c4a62e118d8041a7156\", \"email\": \"lancegomoa@gmail.com\", \"role\": \"agent\", \"email_verified\": 1, \"is_active\": 1, \"last_login\": \"2026-06-10 13:22:36\", \"created_at\": \"2026-05-21 22:55:27\"}', '192.168.1.46', '2026-06-10 05:24:53'),
(79, 6, 'PUT', 'sales', 7, '\"pending\"', '{\"status\": \"completed\"}', '192.168.1.46', '2026-06-10 06:05:37'),
(80, 6, 'PUT', 'users', 1, '{\"user_id\": 1, \"username\": \"admin_jose\", \"hashed_password\": \"$2b$12$mockhashadmin001\", \"email\": \"jose.admin@automatik.ph\", \"role\": \"admin\", \"email_verified\": 1, \"is_active\": 1, \"last_login\": null, \"created_at\": \"2026-04-19 16:40:18\"}', '{\"user_id\": 1, \"username\": \"admin_jose\", \"hashed_password\": \"$2b$12$mockhashadmin001\", \"email\": \"jose.admin@automatik.ph\", \"role\": \"admin\", \"email_verified\": 1, \"is_active\": 0, \"last_login\": null, \"created_at\": \"2026-04-19 16:40:18\"}', '192.168.1.46', '2026-06-10 08:23:50'),
(81, 6, 'PUT', 'users', 1, '{\"user_id\": 1, \"username\": \"admin_jose\", \"hashed_password\": \"$2b$12$mockhashadmin001\", \"email\": \"jose.admin@automatik.ph\", \"role\": \"admin\", \"email_verified\": 1, \"is_active\": 0, \"last_login\": null, \"created_at\": \"2026-04-19 16:40:18\"}', '{\"user_id\": 1, \"username\": \"admin_jose\", \"hashed_password\": \"$2b$12$mockhashadmin001\", \"email\": \"jose.admin@automatik.ph\", \"role\": \"admin\", \"email_verified\": 1, \"is_active\": 1, \"last_login\": null, \"created_at\": \"2026-04-19 16:40:18\"}', '192.168.1.46', '2026-06-10 08:23:53'),
(82, 6, 'PUT', 'inquiries', 2, '\"open\"', '{\"agent_id\": 30, \"status\": \"assigned\"}', '192.168.1.46', '2026-06-10 10:35:22'),
(83, 30, 'PUT', 'inquiries', 6, '\"open\"', '{\"agent_id\": 30, \"status\": \"assigned\"}', '192.168.1.46', '2026-06-10 13:46:04'),
(84, 30, 'PUT', 'inquiries', 4, '\"open\"', '{\"agent_id\": 30, \"status\": \"assigned\"}', '192.168.1.46', '2026-06-10 13:46:12'),
(85, 30, 'PUT', 'inquiries', 7, '\"open\"', '{\"agent_id\": 30, \"status\": \"assigned\"}', '192.168.1.46', '2026-06-10 13:58:53'),
(86, 30, 'PUT', 'inquiries', 7, '\"assigned\"', '{\"status\": \"resolved\"}', '192.168.1.46', '2026-06-11 03:18:33'),
(87, 6, 'PUT', 'inquiries', 7, '\"resolved\"', '{\"status\": \"closed\"}', '192.168.1.46', '2026-06-12 06:38:40'),
(88, 6, 'PUT', 'inquiries', 5, '\"open\"', '{\"agent_id\": 30, \"status\": \"assigned\"}', '192.168.1.46', '2026-06-12 09:07:49'),
(89, 30, 'PUT', 'inquiries', 4, '\"assigned\"', '{\"status\": \"resolved\"}', '192.168.1.46', '2026-06-12 10:20:14'),
(90, 30, 'PUT', 'inquiries', 10, '\"open\"', '{\"agent_id\": 30, \"status\": \"assigned\"}', '192.168.1.46', '2026-06-12 10:49:12'),
(91, 30, 'PUT', 'inquiries', 10, '\"assigned\"', '{\"status\": \"resolved\"}', '192.168.1.46', '2026-06-12 10:49:29'),
(92, 30, 'PUT', 'inquiries', 6, '\"assigned\"', '{\"status\": \"resolved\"}', '192.168.1.46', '2026-06-12 11:05:12'),
(93, 6, 'PUT', 'inquiries', 4, '\"resolved\"', '{\"status\": \"closed\"}', '192.168.1.46', '2026-06-12 11:06:41'),
(94, 6, 'PUT', 'inquiries', 6, '\"resolved\"', '{\"status\": \"closed\"}', '192.168.1.46', '2026-06-12 11:06:44'),
(95, 6, 'PUT', 'inquiries', 10, '\"resolved\"', '{\"status\": \"closed\"}', '192.168.1.46', '2026-06-12 11:06:46'),
(96, 6, 'PUT', 'inquiries', 25, '\"resolved\"', '{\"status\": \"closed\"}', '192.168.1.46', '2026-06-12 11:06:48'),
(97, 49, 'POST', 'service_bookings', 2, NULL, NULL, '192.168.1.46', '2026-06-13 14:58:24'),
(99, 49, 'PUT technician_notes', 'service_bookings', 2, NULL, NULL, '192.168.1.46', '2026-06-13 15:51:42'),
(102, 30, 'PUT', 'inquiries', 11, '\"open\"', '{\"agent_id\": 30, \"status\": \"assigned\"}', '192.168.1.46', '2026-06-13 20:13:44'),
(104, 49, 'PUT technician_notes', 'service_bookings', 3, NULL, NULL, '192.168.1.46', '2026-06-13 20:49:51'),
(106, 46, 'POST', 'inquiries', 26, NULL, NULL, '192.168.1.46', '2026-06-14 01:22:43'),
(107, 30, 'PUT', 'inquiries', 26, '\"open\"', '{\"agent_id\": 30, \"status\": \"assigned\"}', '192.168.1.46', '2026-06-14 01:25:01'),
(108, 30, 'PUT', 'inquiries', 2, '\"assigned\"', '{\"status\": \"resolved\"}', '192.168.1.46', '2026-06-14 01:32:15'),
(109, 46, 'POST', 'inquiries', 27, NULL, NULL, '192.168.1.46', '2026-06-14 01:55:31'),
(111, 46, 'POST', 'inquiries', 28, NULL, NULL, '192.168.1.46', '2026-06-14 02:20:39'),
(112, 46, 'POST', 'inquiries', 29, NULL, NULL, '192.168.1.46', '2026-06-14 02:21:23'),
(113, 46, 'POST', 'inquiries', 30, NULL, NULL, '192.168.1.46', '2026-06-14 02:25:11'),
(114, 46, 'POST', 'inquiries', 31, NULL, NULL, '192.168.1.46', '2026-06-14 02:25:35'),
(115, 46, 'POST', 'inquiries', 32, NULL, NULL, '192.168.1.46', '2026-06-14 02:27:31'),
(116, 6, 'DELETE', 'inquiries', 32, '{\"inquiry_id\": 32, \"user_id\": 46, \"agent_id\": null, \"vehicle_id\": 11, \"guest_name\": null, \"guest_email\": null, \"guest_number\": null, \"message\": \"asd\", \"status\": \"open\", \"created_at\": \"2026-06-14 10:27:31\", \"resolved_at\": null}', NULL, '192.168.1.46', '2026-06-14 02:32:56'),
(117, 6, 'DELETE', 'inquiries', 31, '{\"inquiry_id\": 31, \"user_id\": 46, \"agent_id\": null, \"vehicle_id\": 11, \"guest_name\": null, \"guest_email\": null, \"guest_number\": null, \"message\": \"wowerz\", \"status\": \"open\", \"created_at\": \"2026-06-14 10:25:35\", \"resolved_at\": null}', NULL, '192.168.1.46', '2026-06-14 02:32:56'),
(118, 6, 'DELETE', 'inquiries', 4, '{\"inquiry_id\": 4, \"user_id\": 6, \"agent_id\": 30, \"vehicle_id\": 3, \"guest_name\": null, \"guest_email\": null, \"guest_number\": null, \"message\": \"patingin wahahah\", \"status\": \"closed\", \"created_at\": \"2026-05-27 00:39:53\", \"resolved_at\": \"2026-06-12 18:20:14\"}', NULL, '192.168.1.46', '2026-06-14 02:32:59'),
(119, 6, 'DELETE', 'inquiries', 30, '{\"inquiry_id\": 30, \"user_id\": 46, \"agent_id\": null, \"vehicle_id\": 11, \"guest_name\": null, \"guest_email\": null, \"guest_number\": null, \"message\": \"wowerz\", \"status\": \"open\", \"created_at\": \"2026-06-14 10:25:11\", \"resolved_at\": null}', NULL, '192.168.1.46', '2026-06-14 02:33:45'),
(120, 6, 'DELETE', 'inquiries', 29, '{\"inquiry_id\": 29, \"user_id\": 46, \"agent_id\": null, \"vehicle_id\": 11, \"guest_name\": null, \"guest_email\": null, \"guest_number\": null, \"message\": \"gay\", \"status\": \"open\", \"created_at\": \"2026-06-14 10:21:23\", \"resolved_at\": null}', NULL, '192.168.1.46', '2026-06-14 02:33:48'),
(121, 6, 'DELETE', 'inquiries', 28, '{\"inquiry_id\": 28, \"user_id\": 46, \"agent_id\": null, \"vehicle_id\": 11, \"guest_name\": null, \"guest_email\": null, \"guest_number\": null, \"message\": \"bruh\", \"status\": \"open\", \"created_at\": \"2026-06-14 10:20:39\", \"resolved_at\": null}', NULL, '192.168.1.46', '2026-06-14 02:33:52'),
(122, 6, 'DELETE', 'inquiries', 27, '{\"inquiry_id\": 27, \"user_id\": 46, \"agent_id\": null, \"vehicle_id\": 11, \"guest_name\": null, \"guest_email\": null, \"guest_number\": null, \"message\": \"I would like to reserve this vehicle.\", \"status\": \"open\", \"created_at\": \"2026-06-14 09:55:31\", \"resolved_at\": null}', NULL, '192.168.1.46', '2026-06-14 02:33:55'),
(123, 46, 'POST', 'inquiries', 33, NULL, NULL, '192.168.1.46', '2026-06-14 02:40:25'),
(124, 46, 'POST', 'inquiries', 34, NULL, NULL, '192.168.1.46', '2026-06-14 02:46:02'),
(125, 46, 'POST', 'inquiries', 35, NULL, NULL, '192.168.1.46', '2026-06-14 02:49:38'),
(126, 46, 'POST', 'warranty_claims', 3, NULL, NULL, '192.168.1.46', '2026-06-14 03:20:17'),
(127, 46, 'POST', 'warranty_claims', 4, NULL, NULL, '192.168.1.46', '2026-06-14 03:23:09'),
(129, 49, 'PUT estimate', 'service_bookings', 4, NULL, NULL, '192.168.1.46', '2026-06-14 03:31:48'),
(130, 49, 'PUT transmit-estimate', 'service_bookings', 4, NULL, NULL, '192.168.1.46', '2026-06-14 03:31:48'),
(136, 49, 'PUT estimate', 'service_bookings', 6, NULL, NULL, '192.168.1.46', '2026-06-14 03:48:30'),
(137, 49, 'PUT estimate', 'service_bookings', 6, NULL, NULL, '192.168.1.46', '2026-06-14 03:48:30'),
(139, 49, 'PUT estimate', 'service_bookings', 6, NULL, NULL, '192.168.1.46', '2026-06-14 03:50:07'),
(142, 49, 'PUT estimate', 'service_bookings', 7, NULL, NULL, '192.168.1.46', '2026-06-14 03:55:53'),
(143, 49, 'PUT transmit-estimate', 'service_bookings', 7, NULL, NULL, '192.168.1.46', '2026-06-14 03:55:53'),
(144, 36, 'PUT sign-estimate', 'service_bookings', 7, NULL, NULL, '192.168.1.46', '2026-06-14 03:55:53'),
(145, 46, 'PUT acknowledge-estimate', 'service_bookings', 6, NULL, NULL, '192.168.1.46', '2026-06-14 03:57:32'),
(148, 49, 'PUT estimate', 'service_bookings', 8, NULL, NULL, '192.168.1.46', '2026-06-14 03:58:03'),
(149, 36, 'PUT acknowledge-estimate', 'service_bookings', 8, NULL, NULL, '192.168.1.46', '2026-06-14 03:58:04'),
(150, 36, 'PUT acknowledge-estimate', 'service_bookings', 8, '\"draft_estimate\"', '{\"status\": \"confirmed\"}', '192.168.1.46', '2026-06-14 04:02:36'),
(154, 49, 'PUT estimate', 'service_bookings', 6, NULL, NULL, '192.168.1.46', '2026-06-14 04:13:51'),
(155, 46, 'PUT acknowledge-estimate', 'service_bookings', 6, '\"draft_estimate\"', '{\"status\": \"confirmed\"}', '192.168.1.46', '2026-06-14 04:14:01'),
(156, 49, 'PUT technician_notes', 'service_bookings', 7, NULL, NULL, '192.168.1.46', '2026-06-14 04:14:24'),
(167, 30, 'PUT', 'inquiries', 11, '\"assigned\"', '{\"status\": \"resolved\"}', '192.168.1.46', '2026-06-14 04:40:02'),
(175, 6, 'PUT', 'system_settings', 2, 'true', '1', '192.168.1.46', '2026-06-14 07:03:21'),
(176, 6, 'PUT', 'system_settings', 2, '1', '0', '192.168.1.46', '2026-06-14 07:03:22'),
(177, 6, 'PUT', 'system_settings', 2, '0', '1', '192.168.1.46', '2026-06-14 07:03:23'),
(178, 6, 'PUT', 'system_settings', 2, '1', '0', '192.168.1.46', '2026-06-14 07:03:27'),
(179, 6, 'PUT', 'system_settings', 2, '0', '1', '192.168.1.46', '2026-06-14 07:10:16'),
(180, 6, 'PUT', 'system_settings', 2, '1', '0', '192.168.1.46', '2026-06-14 07:10:17'),
(181, 6, 'PUT', 'system_settings', 2, '0', '1', '192.168.1.46', '2026-06-14 07:12:57'),
(182, 6, 'PUT', 'system_settings', 2, '1', '0', '192.168.1.46', '2026-06-14 07:12:58'),
(185, 46, 'POST', 'inquiries', 36, NULL, NULL, '192.168.1.46', '2026-06-14 08:06:31'),
(190, 30, 'PUT', 'inquiries', 36, '\"open\"', '{\"agent_id\": 30, \"status\": \"assigned\"}', '192.168.1.46', '2026-06-14 08:07:54'),
(193, 30, 'POST', 'sales', 26, NULL, '{\"vehicle_id\": 9, \"customer_id\": 51, \"agent_id\": 30, \"payment_type\": \"full_payment\", \"selling_price\": 1800000.0, \"status\": \"pending\", \"inquiry_id\": 37}', '192.168.1.46', '2026-06-14 09:38:50'),
(194, 30, 'PUT', 'inquiries', 35, '\"open\"', '{\"agent_id\": 30, \"status\": \"assigned\"}', '192.168.1.46', '2026-06-14 09:51:22'),
(195, 30, 'PUT', 'inquiries', 33, '\"open\"', '{\"agent_id\": 30, \"status\": \"assigned\"}', '192.168.1.46', '2026-06-14 09:53:26'),
(196, 30, 'PUT', 'inquiries', 33, '\"assigned\"', '{\"status\": \"resolved\"}', '192.168.1.46', '2026-06-14 09:55:15'),
(197, NULL, 'POST', 'inquiries', 38, NULL, NULL, '192.168.1.46', '2026-06-14 15:38:49'),
(198, NULL, 'POST', 'inquiries', 39, NULL, NULL, '192.168.1.46', '2026-06-14 15:52:06'),
(199, 30, 'PUT', 'inquiries', 34, '\"open\"', '{\"agent_id\": 30, \"status\": \"assigned\"}', '192.168.1.46', '2026-06-14 16:16:55'),
(200, 30, 'PUT', 'inquiries', 35, '\"assigned\"', '{\"status\": \"resolved\"}', '192.168.1.46', '2026-06-14 16:17:00'),
(202, 6, 'PUT', 'system_settings', 2, '0', '1', '192.168.1.46', '2026-06-14 16:58:18'),
(203, 6, 'PUT', 'system_settings', 2, '1', '0', '192.168.1.46', '2026-06-14 17:53:33'),
(204, 6, 'PUT', 'system_settings', 2, '0', '1', '192.168.1.46', '2026-06-14 17:59:57'),
(205, 6, 'PUT', 'inquiries', 2, '\"resolved\"', '{\"status\": \"closed\"}', '192.168.1.46', '2026-06-14 18:51:32'),
(206, 6, 'PUT', 'inquiries', 11, '\"resolved\"', '{\"status\": \"closed\"}', '192.168.1.46', '2026-06-14 18:51:42'),
(207, 6, 'PUT', 'inquiries', 33, '\"resolved\"', '{\"status\": \"closed\"}', '192.168.1.46', '2026-06-14 18:51:44'),
(208, 30, 'POST', 'sales', 27, NULL, '{\"vehicle_id\": 17, \"customer_id\": 51, \"agent_id\": 30, \"payment_type\": \"full_payment\", \"selling_price\": 1000000.0, \"status\": \"pending\", \"inquiry_id\": 40}', '192.168.1.46', '2026-06-14 19:18:27'),
(209, 30, 'PUT', 'inquiries', 39, '\"open\"', '{\"agent_id\": 30, \"status\": \"assigned\"}', '192.168.1.46', '2026-06-14 20:21:21'),
(210, 30, 'PUT', 'inquiries', 39, '\"assigned\"', '{\"status\": \"resolved\"}', '192.168.1.46', '2026-06-14 20:21:47'),
(211, 6, 'PUT', 'users', 1, '{\"user_id\": 1, \"username\": \"admin_jose\", \"hashed_password\": \"$2b$12$mockhashadmin001\", \"email\": \"jose.admin@automatik.ph\", \"role\": \"admin\", \"email_verified\": 1, \"is_active\": 1, \"last_login\": null, \"created_at\": \"2026-04-19 16:40:18\"}', '{\"user_id\": 1, \"username\": \"admin_jose\", \"hashed_password\": \"$2b$12$mockhashadmin001\", \"email\": \"jose.admin@automatik.ph\", \"role\": \"admin\", \"email_verified\": 1, \"is_active\": 0, \"last_login\": null, \"created_at\": \"2026-04-19 16:40:18\"}', '192.168.1.46', '2026-06-14 20:35:25'),
(212, 6, 'PUT', 'users', 1, '{\"user_id\": 1, \"username\": \"admin_jose\", \"hashed_password\": \"$2b$12$mockhashadmin001\", \"email\": \"jose.admin@automatik.ph\", \"role\": \"admin\", \"email_verified\": 1, \"is_active\": 0, \"last_login\": null, \"created_at\": \"2026-04-19 16:40:18\"}', '{\"user_id\": 1, \"username\": \"admin_jose\", \"hashed_password\": \"$2b$12$mockhashadmin001\", \"email\": \"jose.admin@automatik.ph\", \"role\": \"admin\", \"email_verified\": 1, \"is_active\": 1, \"last_login\": null, \"created_at\": \"2026-04-19 16:40:18\"}', '192.168.1.46', '2026-06-14 20:35:26'),
(213, 6, 'PUT', 'users', 2, '{\"user_id\": 2, \"username\": \"agent_miguel\", \"hashed_password\": \"scrypt:32768:8:1$nqpzKGkeh2xNe4Y5$4fd26f44d4442c5a2e97d14df37a8a090be16314b768bcf9b50cea631d939ecc7e910d02559c6d2515d6a8e36aae4075b9f93babee5cac8babf793b46f2ec30c\", \"email\": \"miguel.reyes@automatik.ph\", \"role\": \"agent\", \"email_verified\": 1, \"is_active\": 1, \"last_login\": \"2026-06-10 08:52:56\", \"created_at\": \"2026-04-19 16:40:18\"}', '{\"user_id\": 2, \"username\": \"agent_miguel\", \"hashed_password\": \"scrypt:32768:8:1$nqpzKGkeh2xNe4Y5$4fd26f44d4442c5a2e97d14df37a8a090be16314b768bcf9b50cea631d939ecc7e910d02559c6d2515d6a8e36aae4075b9f93babee5cac8babf793b46f2ec30c\", \"email\": \"miguel.reyes@automatik.ph\", \"role\": \"agent\", \"email_verified\": 1, \"is_active\": 0, \"last_login\": \"2026-06-10 08:52:56\", \"created_at\": \"2026-04-19 16:40:18\"}', '192.168.1.46', '2026-06-14 20:35:32'),
(214, 6, 'PUT', 'users', 2, '{\"user_id\": 2, \"username\": \"agent_miguel\", \"hashed_password\": \"scrypt:32768:8:1$nqpzKGkeh2xNe4Y5$4fd26f44d4442c5a2e97d14df37a8a090be16314b768bcf9b50cea631d939ecc7e910d02559c6d2515d6a8e36aae4075b9f93babee5cac8babf793b46f2ec30c\", \"email\": \"miguel.reyes@automatik.ph\", \"role\": \"agent\", \"email_verified\": 1, \"is_active\": 0, \"last_login\": \"2026-06-10 08:52:56\", \"created_at\": \"2026-04-19 16:40:18\"}', '{\"user_id\": 2, \"username\": \"agent_miguel\", \"hashed_password\": \"scrypt:32768:8:1$nqpzKGkeh2xNe4Y5$4fd26f44d4442c5a2e97d14df37a8a090be16314b768bcf9b50cea631d939ecc7e910d02559c6d2515d6a8e36aae4075b9f93babee5cac8babf793b46f2ec30c\", \"email\": \"miguel.reyes@automatik.ph\", \"role\": \"agent\", \"email_verified\": 1, \"is_active\": 1, \"last_login\": \"2026-06-10 08:52:56\", \"created_at\": \"2026-04-19 16:40:18\"}', '192.168.1.46', '2026-06-14 20:35:35'),
(215, 6, 'PUT', 'sales', 27, '\"pending\"', '{\"status\": \"completed\"}', '192.168.1.46', '2026-06-14 20:44:21'),
(216, 49, 'PUT technician_notes', 'service_bookings', 7, NULL, NULL, '192.168.1.46', '2026-06-15 02:47:23');

-- --------------------------------------------------------

--
-- Table structure for table `chatbot_logs`
--

CREATE TABLE `chatbot_logs` (
  `log_id` int(11) NOT NULL,
  `session_id` varchar(100) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `inquiry_id` int(11) DEFAULT NULL,
  `user_message` text NOT NULL,
  `bot_response` text NOT NULL,
  `intent_tag` varchar(50) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `customer_details`
--

CREATE TABLE `customer_details` (
  `user_id` int(11) NOT NULL,
  `customer_number` varchar(20) NOT NULL,
  `preferred_contact_method` enum('email','sms','whatsapp') DEFAULT NULL,
  `preferred_payment_method` enum('cash','installment','bank_transfer') DEFAULT NULL,
  `notes` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `customer_details`
--

INSERT INTO `customer_details` (`user_id`, `customer_number`, `preferred_contact_method`, `preferred_payment_method`, `notes`) VALUES
(4, 'CUST-2025-001', 'email', 'installment', NULL),
(5, 'CUST-2025-002', 'sms', 'cash', NULL),
(31, 'CUST-2026-31', NULL, NULL, NULL),
(34, 'CUST-2025-003', 'email', 'cash', NULL),
(35, 'CUST-2025-004', 'sms', 'installment', NULL),
(36, 'CUST-2025-005', 'email', 'cash', NULL),
(37, 'CUST-2025-006', 'whatsapp', 'installment', NULL),
(46, 'CUST-2026-46', 'email', NULL, NULL),
(51, 'CUST-2026-51', NULL, NULL, NULL),
(54, 'CUST-54', NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `documents`
--

CREATE TABLE `documents` (
  `document_id` int(11) NOT NULL,
  `sale_id` int(11) NOT NULL,
  `document_type` enum('OR','CR','warranty_cert','amortization_schedule','sales_contract','other') NOT NULL,
  `file_url` varchar(500) NOT NULL,
  `is_accessible` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `documents`
--

INSERT INTO `documents` (`document_id`, `sale_id`, `document_type`, `file_url`, `is_accessible`, `created_at`) VALUES
(2, 1, 'CR', '/static/uploads/documents/1781424021_Automatik_DB_Impact_Summary.pdf', 1, '2026-04-19 08:40:18'),
(3, 2, 'amortization_schedule', 'https://docs.automatik.ph/amo/SCHED-2025-001.pdf', 1, '2026-04-19 08:40:18'),
(4, 1, 'OR', 'http://example.com/or.pdf', 1, '2026-06-04 05:59:15'),
(9, 25, 'OR', 'https://docs.automatik.ph/or/OR-20260606-0020.pdf', 1, '2026-06-05 17:05:32'),
(10, 2, 'sales_contract', 'https://docs.automatik.ph/contract/SC-2025-002.pdf', 1, '2026-06-12 06:32:21'),
(11, 2, 'OR', 'https://docs.automatik.ph/or/OR-2025-002.pdf', 1, '2026-06-12 06:32:21'),
(12, 3, 'sales_contract', 'https://docs.automatik.ph/contract/SC-2025-003.pdf', 1, '2026-06-12 06:32:21'),
(13, 3, 'warranty_cert', 'https://docs.automatik.ph/warranty/WC-2025-003.pdf', 1, '2026-06-12 06:32:21'),
(14, 7, 'amortization_schedule', 'https://docs.automatik.ph/amo/SCHED-2025-007.pdf', 1, '2026-06-12 06:32:21'),
(15, 7, 'CR', 'https://docs.automatik.ph/cr/CR-2025-007.pdf', 1, '2026-06-12 06:32:21'),
(16, 10, 'sales_contract', 'https://docs.automatik.ph/contract/SC-2025-010.pdf', 1, '2026-06-12 06:32:21'),
(17, 10, 'OR', 'https://docs.automatik.ph/or/OR-2025-010.pdf', 1, '2026-06-12 06:32:21'),
(18, 24, 'sales_contract', 'https://docs.automatik.ph/contract/SC-2026-024.pdf', 1, '2026-06-12 06:33:12'),
(19, 24, 'OR', 'https://docs.automatik.ph/or/OR-2026-024.pdf', 1, '2026-06-12 06:33:12'),
(20, 24, 'CR', 'https://docs.automatik.ph/cr/CR-2026-024.pdf', 1, '2026-06-12 06:33:12'),
(21, 24, 'amortization_schedule', 'https://docs.automatik.ph/amo/SCHED-2026-024.pdf', 1, '2026-06-12 06:33:12'),
(22, 24, 'warranty_cert', 'https://docs.automatik.ph/warranty/WC-2026-024.pdf', 1, '2026-06-12 06:33:12'),
(23, 24, 'sales_contract', '/static/uploads/documents/1781424098_AutoMatik_UI_Requirements.pdf', 1, '2026-06-14 08:01:40');

-- --------------------------------------------------------

--
-- Table structure for table `inquiries`
--

CREATE TABLE `inquiries` (
  `inquiry_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `agent_id` int(11) DEFAULT NULL,
  `vehicle_id` int(11) NOT NULL,
  `guest_name` varchar(100) DEFAULT NULL,
  `guest_email` varchar(100) DEFAULT NULL,
  `guest_number` varchar(20) DEFAULT NULL,
  `message` text NOT NULL,
  `status` enum('open','assigned','resolved','closed') NOT NULL DEFAULT 'open',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `resolved_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Dumping data for table `inquiries`
--

INSERT INTO `inquiries` (`inquiry_id`, `user_id`, `agent_id`, `vehicle_id`, `guest_name`, `guest_email`, `guest_number`, `message`, `status`, `created_at`, `resolved_at`) VALUES
(1, 4, 2, 1, NULL, NULL, NULL, 'I am interested in the Fortuner GR. What is the best deal available?', 'assigned', '2026-04-19 08:40:18', NULL),
(2, NULL, 30, 3, 'Juan Buenaventura', 'juan.b@email.com', NULL, 'How much is the downpayment for CR-V RS?', 'closed', '2026-04-19 08:40:18', '2026-06-14 01:32:15'),
(3, 6, 28, 3, NULL, NULL, NULL, 'patingin wahahah', 'assigned', '2026-05-26 16:38:38', NULL),
(5, NULL, 30, 3, 'lance kit gom-os', 'lancegomoa@gmail.com', NULL, 'Hi can I test drive this? ', 'assigned', '2026-05-28 21:00:43', NULL),
(6, NULL, 30, 3, 'lance kit gom-os', 'lancegomoa@gmail.com', NULL, 'Hi can I test drive this? ', 'closed', '2026-05-28 21:02:23', '2026-06-12 11:05:12'),
(7, NULL, 30, 3, 'lance kit gom-os', 'lancegomoa@gmail.com', NULL, 'Hi can I test drive this? ', 'closed', '2026-05-28 21:05:20', '2026-06-11 03:18:33'),
(8, NULL, NULL, 3, 'lance kit gom-os', 'lancegomoa@gmail.com', NULL, 'Hi can I test drive this? ', 'open', '2026-05-28 21:07:27', NULL),
(9, NULL, NULL, 3, 'lance kit gom-os', 'lancegomoa@gmail.com', NULL, 'Hi can I test drive this? ', 'open', '2026-05-28 21:09:34', NULL),
(10, 34, 30, 2, NULL, NULL, NULL, 'Good day! I am interested in the Vios XLE CVT for my daily commute. Do you offer free LTO registration and comprehensive insurance? Please advise on the best deal available.', 'closed', '2026-06-03 15:49:24', '2026-06-12 10:49:29'),
(11, 35, 30, 5, NULL, NULL, NULL, 'Hi! I currently own a 2019 sedan and am looking to trade it in for the Civic RS Turbo. Do you accept trade-ins? What is the total cash-out needed?', 'closed', '2026-06-03 15:49:24', '2026-06-14 04:40:02'),
(25, 46, 30, 1, 'Tanjiro Kamado', 'tanjirokamado22222@gmail.com', NULL, 'Testing all notifications', 'closed', '2026-06-05 10:13:51', '2026-06-05 10:14:05'),
(26, 46, 30, 5, NULL, NULL, NULL, 'I would like to reserve this vehicle.', 'assigned', '2026-06-14 01:22:43', NULL),
(33, 46, 30, 9, NULL, NULL, NULL, 'is this really it?', 'closed', '2026-06-14 02:40:25', '2026-06-14 09:55:15'),
(34, 46, 30, 9, NULL, NULL, NULL, 'test', 'assigned', '2026-06-14 02:46:02', NULL),
(35, 46, 30, 9, NULL, NULL, NULL, 'is the specs available?', 'resolved', '2026-06-14 02:49:38', '2026-06-14 16:17:00'),
(36, 46, 30, 11, NULL, NULL, NULL, 'I would like to reserve this vehicle.', 'assigned', '2026-06-14 08:06:31', NULL),
(37, 51, 30, 9, 'Gianna Izabelle Cantillo', 'lancekit223@gmail.com', '09776913684', 'sale', 'resolved', '2026-06-14 09:38:27', '2026-06-14 09:38:50'),
(38, NULL, NULL, 12, 'Lance Kit Gom-os', 'lancegomoa@gmail.com', '09776913684', 'I would like to reserve this vehicle.', 'open', '2026-06-14 15:38:49', NULL),
(39, NULL, 30, 9, 'Lance Kit Gom-os', 'lancegomoa@gmail.com', NULL, 'I would like to reserve this vehicle.', 'resolved', '2026-06-14 15:52:06', '2026-06-14 20:21:47'),
(40, 51, 30, 17, 'Kit kit', 'lancekit223@gmail.com', NULL, 'for sale conversion', 'resolved', '2026-06-14 19:18:02', '2026-06-14 19:18:27');

-- --------------------------------------------------------

--
-- Table structure for table `insurance_records`
--

CREATE TABLE `insurance_records` (
  `insurance_id` int(11) NOT NULL,
  `vehicle_id` int(11) NOT NULL,
  `sale_id` int(11) NOT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `provider_name` varchar(150) NOT NULL,
  `policy_number` varchar(100) NOT NULL,
  `coverage_type` varchar(100) DEFAULT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `status` enum('active','expired','cancelled') NOT NULL DEFAULT 'active'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `insurance_records`
--

INSERT INTO `insurance_records` (`insurance_id`, `vehicle_id`, `sale_id`, `customer_id`, `provider_name`, `policy_number`, `coverage_type`, `start_date`, `end_date`, `status`) VALUES
(1, 4, 1, 5, 'automatik', 'MAL-2025-VH-001', 'Comprehensive', '2025-03-10', '2026-03-10', 'active'),
(2, 1, 2, 4, 'automatik', 'PIO-2025-VH-002', 'CTPL + Comprehensive', '2025-04-01', '2026-04-01', 'active'),
(3, 1, 19, 28, 'automatik', 'PRU-2026-1234', 'Comprehensive', '2026-06-05', '2027-06-05', 'active'),
(4, 1, 24, 46, 'automatik', 'PRU-001', 'Comprehensive', '2026-06-05', '2027-06-05', 'active');

-- --------------------------------------------------------

--
-- Table structure for table `loan_details`
--

CREATE TABLE `loan_details` (
  `loan_id` int(11) NOT NULL,
  `sale_id` int(11) NOT NULL,
  `down_payment` decimal(12,2) NOT NULL,
  `loan_amount` decimal(12,2) NOT NULL,
  `interest_rate` decimal(5,2) NOT NULL,
  `term_months` int(11) NOT NULL,
  `monthly_amortization` decimal(12,2) NOT NULL,
  `bank_name` varchar(100) NOT NULL DEFAULT 'automatik_financing',
  `bank_approval_status` enum('pending','approved','rejected') NOT NULL DEFAULT 'pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `loan_details`
--

INSERT INTO `loan_details` (`loan_id`, `sale_id`, `down_payment`, `loan_amount`, `interest_rate`, `term_months`, `monthly_amortization`, `bank_name`, `bank_approval_status`, `created_at`) VALUES
(1, 2, 478000.00, 1912000.00, 7.00, 12, 191794.80, 'automatik_financing', 'approved', '2026-04-19 08:40:18'),
(2, 1, 20000.00, 100000.00, 6.50, 12, 8629.64, 'automatik_financing', 'approved', '2026-06-04 05:59:15'),
(13, 24, 478000.00, 1912000.00, 6.50, 60, 37410.18, 'automatik_financing', 'approved', '2026-06-05 10:14:05');

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE `notifications` (
  `notification_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `title` varchar(200) NOT NULL,
  `message` text NOT NULL,
  `channel` enum('in_app','email','sms') NOT NULL DEFAULT 'in_app',
  `ref_type` varchar(50) DEFAULT NULL,
  `ref_id` int(11) DEFAULT NULL,
  `is_read` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `notifications`
--

INSERT INTO `notifications` (`notification_id`, `user_id`, `title`, `message`, `channel`, `ref_type`, `ref_id`, `is_read`, `created_at`) VALUES
(1, 4, 'Amortization Due', 'Your payment of PHP 37,373.45 is due on July 15, 2025.', 'email', 'amortization_schedule', 3, 0, '2026-04-19 08:40:18'),
(2, 2, 'New Inquiry Assigned', 'A new inquiry has been assigned to you from Pedro Garcia.', 'in_app', 'inquiries', 1, 1, '2026-04-19 08:40:18'),
(33, 4, 'Payment Schedule Updated', 'Your payment schedule for month 1 has been marked as paid.', 'in_app', 'amortization_schedule', 1, 0, '2026-06-04 05:59:15'),
(34, 4, 'Payment Schedule Updated', 'Your payment schedule for month 1 has been marked as paid.', 'in_app', 'amortization_schedule', 1, 0, '2026-06-04 06:00:05'),
(35, 4, 'Payment Schedule Updated', 'Your payment schedule for month 1 has been marked as paid.', 'in_app', 'amortization_schedule', 1, 0, '2026-06-04 06:00:51'),
(36, 4, 'Payment Schedule Updated', 'Your payment schedule for month 1 has been marked as paid.', 'in_app', 'amortization_schedule', 1, 0, '2026-06-04 06:23:06'),
(37, 4, 'Payment Schedule Updated', 'Your payment schedule for month 1 has been marked as paid.', 'in_app', 'amortization_schedule', 1, 0, '2026-06-04 06:23:27'),
(38, 5, 'Sale Created', 'Sale #7 has been created for Honda CR-V RS Turbo.', 'in_app', 'sales', 7, 0, '2026-06-05 06:31:22'),
(39, 5, 'Sale Created', 'Sale #9 has been created for Honda CR-V RS Turbo.', 'in_app', 'sales', 9, 0, '2026-06-05 06:32:16'),
(40, 5, 'Payment Received', 'A payment of 1800000.0 has been recorded for sale #9.', 'in_app', 'payments', 4, 0, '2026-06-05 06:42:55'),
(41, 5, 'Payment Received', 'A payment of 500000.0 has been recorded for sale #1.', 'in_app', 'payments', 5, 0, '2026-06-05 06:42:59'),
(42, 5, 'Payment Received', 'A payment of 1800000.0 has been recorded for sale #9.', 'in_app', 'payments', 11, 0, '2026-06-05 07:40:02'),
(43, 34, 'Payment Received', 'A payment of 18000.0 has been recorded for sale #10.', 'in_app', 'payments', 12, 0, '2026-06-05 07:41:19'),
(45, 39, 'Sale Created', 'Sale #13 has been created for Toyota Fortuner GR Sport.', 'in_app', 'sales', 13, 0, '2026-06-05 08:57:05'),
(46, 39, 'Loan Status Updated', 'Your loan for sale #13 has been approved.', 'in_app', 'loan_details', 3, 0, '2026-06-05 09:03:23'),
(47, 39, 'Payment Received', 'A payment of 37410.48 has been recorded for sale #13.', 'in_app', 'payments', 13, 0, '2026-06-05 09:03:36'),
(49, 40, 'Sale Created', 'Sale #14 has been created for Toyota Fortuner GR Sport.', 'in_app', 'sales', 14, 0, '2026-06-05 09:14:44'),
(50, 40, 'Loan Status Updated', 'Your loan for sale #14 has been approved.', 'in_app', 'loan_details', 4, 0, '2026-06-05 09:14:44'),
(51, 40, 'Payment Received', 'A payment of 37410.48 has been recorded for sale #14.', 'in_app', 'payments', 14, 0, '2026-06-05 09:14:48'),
(56, 30, 'New Inquiry Assigned', 'Inquiry #16 has been assigned to you. Please follow up with the customer.', 'in_app', 'inquiries', 16, 0, '2026-06-05 09:25:40'),
(60, 30, 'New Inquiry Assigned', 'Inquiry #17 has been assigned to you. Please follow up with the customer.', 'in_app', 'inquiries', 17, 0, '2026-06-05 09:45:12'),
(65, 30, 'New Inquiry Assigned', 'Inquiry #19 has been assigned to you. Please follow up with the customer.', 'in_app', 'inquiries', 19, 0, '2026-06-05 09:54:18'),
(69, 30, 'New Inquiry Assigned', 'Inquiry #20 has been assigned to you. Please follow up with the customer.', 'in_app', 'inquiries', 20, 0, '2026-06-05 09:59:06'),
(71, 30, 'New Inquiry Assigned', 'Inquiry #21 has been assigned to you. Please follow up with the customer.', 'in_app', 'inquiries', 21, 1, '2026-06-05 10:06:39'),
(74, 30, 'New Inquiry Assigned', 'Inquiry #22 has been assigned to you. Please follow up with the customer.', 'in_app', 'inquiries', 22, 1, '2026-06-05 10:08:11'),
(76, 30, 'New Inquiry Assigned', 'Inquiry #23 has been assigned to you. Please follow up with the customer.', 'in_app', 'inquiries', 23, 1, '2026-06-05 10:11:08'),
(79, 30, 'New Inquiry Assigned', 'Inquiry #24 has been assigned to you. Please follow up with the customer.', 'in_app', 'inquiries', 24, 1, '2026-06-05 10:13:09'),
(80, 30, 'New Inquiry Assigned', 'Inquiry #25 has been assigned to you. Please follow up with the customer.', 'in_app', 'inquiries', 25, 1, '2026-06-05 10:13:58'),
(81, 46, 'Account Created', 'Your AutoMatik account (CUST-tanjirokamad-1894) has been created. Welcome!', 'in_app', 'users', 46, 1, '2026-06-05 10:14:08'),
(82, 46, 'Sale Created', 'Sale #24 has been created for Toyota Fortuner GR Sport.', 'in_app', 'sales', 24, 1, '2026-06-05 10:14:11'),
(83, 46, 'Loan Status Updated', 'Your loan for sale #24 has been approved.', 'in_app', 'loan_details', 13, 1, '2026-06-05 10:14:18'),
(84, 46, 'Insurance Added', 'Insurance policy PRU-001 added to sale #24.', 'in_app', 'insurance_records', 4, 1, '2026-06-05 10:14:21'),
(85, 46, 'Payment Received', 'A payment of 37410.48 has been recorded for sale #24.', 'in_app', 'payments', 19, 1, '2026-06-05 10:14:21'),
(86, 46, 'Sale Status Updated', 'Sale #24 status changed to \'completed\'.', 'in_app', 'sales', 24, 1, '2026-06-05 10:14:24'),
(87, 4, 'Estimate Ready for Signature', 'Your service estimate is ready. Please review and sign digitally.', 'in_app', 'service_bookings', 1, 0, '2026-06-10 05:12:23'),
(88, 5, 'Loan Status Updated', 'Your loan for sale #1 has been approved.', 'in_app', 'loan_details', 2, 0, '2026-06-10 05:19:06'),
(89, 5, 'Sale Status Updated', 'Sale #7 status changed to \'completed\'.', 'in_app', 'sales', 7, 0, '2026-06-10 06:05:37'),
(90, 46, 'Amortization Updated', 'Amortization period #2 marked as paid.', 'in_app', 'amortization_schedule', 577, 1, '2026-06-10 06:21:32'),
(91, 30, 'New Inquiry Assigned', 'Inquiry #2 has been assigned to you. Please follow up with the customer.', 'in_app', 'inquiries', 2, 1, '2026-06-10 10:35:22'),
(92, 1, 'Inquiry Self-Assigned', 'Agent gianna252 has self-assigned inquiry #6.', 'in_app', 'inquiries', 6, 0, '2026-06-10 13:46:04'),
(93, 6, 'Inquiry Self-Assigned', 'Agent gianna252 has self-assigned inquiry #6.', 'in_app', 'inquiries', 6, 1, '2026-06-10 13:46:04'),
(94, 1, 'Inquiry Self-Assigned', 'Agent gianna252 has self-assigned inquiry #4.', 'in_app', 'inquiries', 4, 0, '2026-06-10 13:46:12'),
(95, 6, 'Inquiry Self-Assigned', 'Agent gianna252 has self-assigned inquiry #4.', 'in_app', 'inquiries', 4, 1, '2026-06-10 13:46:12'),
(96, 6, 'Inquiry Assigned', 'Your inquiry #4 has been assigned to gianna252. They will contact you soon.', 'in_app', 'inquiries', 4, 1, '2026-06-10 13:46:12'),
(97, 1, 'Inquiry Self-Assigned', 'Agent gianna252 has self-assigned inquiry #7.', 'in_app', 'inquiries', 7, 0, '2026-06-10 13:58:53'),
(98, 6, 'Inquiry Self-Assigned', 'Agent gianna252 has self-assigned inquiry #7.', 'in_app', 'inquiries', 7, 1, '2026-06-10 13:58:53'),
(99, 30, 'New Inquiry Assigned', 'Inquiry #5 has been assigned to you. Please follow up with the customer.', 'in_app', 'inquiries', 5, 0, '2026-06-12 09:07:49'),
(100, 6, 'Inquiry Resolved', 'Your inquiry #4 has been resolved by gianna252. Thank you!', 'in_app', 'inquiries', 4, 1, '2026-06-12 10:20:14'),
(101, 1, 'Inquiry Resolved', 'Inquiry #4 has been resolved by gianna252.', 'in_app', 'inquiries', 4, 0, '2026-06-12 10:20:20'),
(102, 6, 'Inquiry Resolved', 'Inquiry #4 has been resolved by gianna252.', 'in_app', 'inquiries', 4, 1, '2026-06-12 10:20:20'),
(103, 1, 'Inquiry Self-Assigned', 'Agent gianna252 has self-assigned inquiry #10.', 'in_app', 'inquiries', 10, 0, '2026-06-12 10:49:12'),
(104, 6, 'Inquiry Self-Assigned', 'Agent gianna252 has self-assigned inquiry #10.', 'in_app', 'inquiries', 10, 1, '2026-06-12 10:49:12'),
(105, 34, 'Inquiry Assigned', 'Your inquiry #10 has been assigned to gianna252. They will contact you soon.', 'in_app', 'inquiries', 10, 0, '2026-06-12 10:49:12'),
(106, 34, 'Inquiry Resolved', 'Your inquiry #10 has been resolved by gianna252. Thank you!', 'in_app', 'inquiries', 10, 0, '2026-06-12 10:49:29'),
(107, 1, 'Inquiry Resolved', 'Inquiry #10 has been resolved by gianna252.', 'in_app', 'inquiries', 10, 0, '2026-06-12 10:49:35'),
(108, 6, 'Inquiry Resolved', 'Inquiry #10 has been resolved by gianna252.', 'in_app', 'inquiries', 10, 1, '2026-06-12 10:49:35'),
(109, 6, 'Inquiry Closed', 'Your inquiry has been closed. If you need further assistance, please submit a new inquiry.', 'in_app', 'inquiries', 4, 1, '2026-06-12 11:06:41'),
(110, 30, 'Inquiry Closed', 'Inquiry #4 has been closed by admin.', 'in_app', 'inquiries', 4, 0, '2026-06-12 11:06:41'),
(111, 30, 'Inquiry Closed', 'Inquiry #6 has been closed by admin.', 'in_app', 'inquiries', 6, 0, '2026-06-12 11:06:44'),
(112, 34, 'Inquiry Closed', 'Your inquiry has been closed. If you need further assistance, please submit a new inquiry.', 'in_app', 'inquiries', 10, 0, '2026-06-12 11:06:46'),
(113, 30, 'Inquiry Closed', 'Inquiry #10 has been closed by admin.', 'in_app', 'inquiries', 10, 0, '2026-06-12 11:06:46'),
(114, 46, 'Inquiry Closed', 'Your inquiry has been closed. If you need further assistance, please submit a new inquiry.', 'in_app', 'inquiries', 25, 1, '2026-06-12 11:06:48'),
(115, 30, 'Inquiry Closed', 'Inquiry #25 has been closed by admin.', 'in_app', 'inquiries', 25, 0, '2026-06-12 11:06:48'),
(116, 36, 'Service Completed', 'Your vehicle service has been completed. Thank you!', 'in_app', 'service_bookings', 2, 0, '2026-06-13 15:51:12'),
(117, 36, 'Warranty Resolved', 'Your warranty claim has been resolved.', 'in_app', 'warranty_claims', 2, 0, '2026-06-13 16:33:02'),
(118, 1, 'Inquiry Self-Assigned', 'Agent gianna252 has self-assigned inquiry #11.', 'in_app', 'inquiries', 11, 0, '2026-06-13 20:13:44'),
(119, 6, 'Inquiry Self-Assigned', 'Agent gianna252 has self-assigned inquiry #11.', 'in_app', 'inquiries', 11, 1, '2026-06-13 20:13:44'),
(120, 35, 'Inquiry Assigned', 'Your inquiry #11 has been assigned to gianna252. They will contact you soon.', 'in_app', 'inquiries', 11, 0, '2026-06-13 20:13:44'),
(121, 36, 'Booking Confirmed', 'Your service booking has been confirmed.', 'in_app', 'service_bookings', 3, 0, '2026-06-13 20:49:51'),
(122, 2, 'Vehicle Reserved', 'Customer reserved Honda Civic RS Turbo (#5).', 'in_app', 'inquiries', 26, 0, '2026-06-14 01:22:43'),
(123, 3, 'Vehicle Reserved', 'Customer reserved Honda Civic RS Turbo (#5).', 'in_app', 'inquiries', 26, 0, '2026-06-14 01:22:43'),
(124, 29, 'Vehicle Reserved', 'Customer reserved Honda Civic RS Turbo (#5).', 'in_app', 'inquiries', 26, 0, '2026-06-14 01:22:43'),
(125, 30, 'Vehicle Reserved', 'Customer reserved Honda Civic RS Turbo (#5).', 'in_app', 'inquiries', 26, 0, '2026-06-14 01:22:43'),
(126, 33, 'Vehicle Reserved', 'Customer reserved Honda Civic RS Turbo (#5).', 'in_app', 'inquiries', 26, 0, '2026-06-14 01:22:43'),
(127, 50, 'Vehicle Reserved', 'Customer reserved Honda Civic RS Turbo (#5).', 'in_app', 'inquiries', 26, 0, '2026-06-14 01:22:43'),
(128, 46, 'Reservation Confirmed', 'You have reserved the Honda Civic RS Turbo. An agent will follow up.', 'in_app', 'inquiries', 26, 1, '2026-06-14 01:22:43'),
(129, 1, 'Inquiry Self-Assigned', 'Agent gianna252 has self-assigned inquiry #26.', 'in_app', 'inquiries', 26, 0, '2026-06-14 01:25:01'),
(130, 6, 'Inquiry Self-Assigned', 'Agent gianna252 has self-assigned inquiry #26.', 'in_app', 'inquiries', 26, 1, '2026-06-14 01:25:01'),
(131, 46, 'Inquiry Assigned', 'Your inquiry #26 has been assigned to gianna252. They will contact you soon.', 'in_app', 'inquiries', 26, 1, '2026-06-14 01:25:01'),
(132, 2, 'Vehicle Reserved', 'Customer reserved BYD SEALION (#11).', 'in_app', 'inquiries', 27, 0, '2026-06-14 01:55:31'),
(133, 3, 'Vehicle Reserved', 'Customer reserved BYD SEALION (#11).', 'in_app', 'inquiries', 27, 0, '2026-06-14 01:55:31'),
(134, 29, 'Vehicle Reserved', 'Customer reserved BYD SEALION (#11).', 'in_app', 'inquiries', 27, 0, '2026-06-14 01:55:31'),
(135, 30, 'Vehicle Reserved', 'Customer reserved BYD SEALION (#11).', 'in_app', 'inquiries', 27, 1, '2026-06-14 01:55:31'),
(136, 33, 'Vehicle Reserved', 'Customer reserved BYD SEALION (#11).', 'in_app', 'inquiries', 27, 0, '2026-06-14 01:55:31'),
(137, 50, 'Vehicle Reserved', 'Customer reserved BYD SEALION (#11).', 'in_app', 'inquiries', 27, 0, '2026-06-14 01:55:31'),
(138, 46, 'Reservation Confirmed', 'You have reserved the BYD SEALION. An agent will follow up.', 'in_app', 'inquiries', 27, 1, '2026-06-14 01:55:31'),
(139, 2, 'New Booking', 'Test Drive booking #4 created.', 'in_app', 'service_bookings', 4, 0, '2026-06-14 02:19:44'),
(140, 3, 'New Booking', 'Test Drive booking #4 created.', 'in_app', 'service_bookings', 4, 0, '2026-06-14 02:19:44'),
(141, 29, 'New Booking', 'Test Drive booking #4 created.', 'in_app', 'service_bookings', 4, 0, '2026-06-14 02:19:44'),
(142, 30, 'New Booking', 'Test Drive booking #4 created.', 'in_app', 'service_bookings', 4, 1, '2026-06-14 02:19:44'),
(143, 33, 'New Booking', 'Test Drive booking #4 created.', 'in_app', 'service_bookings', 4, 0, '2026-06-14 02:19:44'),
(144, 50, 'New Booking', 'Test Drive booking #4 created.', 'in_app', 'service_bookings', 4, 0, '2026-06-14 02:19:44'),
(145, 1, 'New Booking', 'Test Drive booking #4 created.', 'in_app', 'service_bookings', 4, 0, '2026-06-14 02:19:44'),
(146, 6, 'New Booking', 'Test Drive booking #4 created.', 'in_app', 'service_bookings', 4, 1, '2026-06-14 02:19:44'),
(147, 46, 'Inquiry Submitted', 'Your inquiry has been received. An agent will follow up shortly.', 'in_app', 'inquiries', 28, 1, '2026-06-14 02:20:39'),
(148, 46, 'Inquiry Submitted', 'Your inquiry has been received. An agent will follow up shortly.', 'in_app', 'inquiries', 29, 1, '2026-06-14 02:21:23'),
(149, 46, 'Inquiry Submitted', 'Your inquiry has been received. An agent will follow up shortly.', 'in_app', 'inquiries', 30, 1, '2026-06-14 02:25:11'),
(150, 46, 'Inquiry Submitted', 'Your inquiry has been received. An agent will follow up shortly.', 'in_app', 'inquiries', 31, 1, '2026-06-14 02:25:35'),
(151, 46, 'Inquiry Submitted', 'Your inquiry has been received. An agent will follow up shortly.', 'in_app', 'inquiries', 32, 0, '2026-06-14 02:27:31'),
(152, 46, 'Inquiry Deleted', 'Your inquiry #32 has been removed by an admin.', 'in_app', 'inquiries', 32, 1, '2026-06-14 02:32:56'),
(153, 46, 'Inquiry Deleted', 'Your inquiry #31 has been removed by an admin.', 'in_app', 'inquiries', 31, 1, '2026-06-14 02:32:56'),
(154, 6, 'Inquiry Deleted', 'Your inquiry #4 has been removed by an admin.', 'in_app', 'inquiries', 4, 1, '2026-06-14 02:32:59'),
(155, 46, 'Inquiry Deleted', 'Your inquiry #30 has been removed by an admin.', 'in_app', 'inquiries', 30, 1, '2026-06-14 02:33:45'),
(156, 46, 'Inquiry Deleted', 'Your inquiry #29 has been removed by an admin.', 'in_app', 'inquiries', 29, 1, '2026-06-14 02:33:48'),
(157, 46, 'Inquiry Deleted', 'Your inquiry #28 has been removed by an admin.', 'in_app', 'inquiries', 28, 1, '2026-06-14 02:33:52'),
(158, 46, 'Inquiry Deleted', 'Your inquiry #27 has been removed by an admin.', 'in_app', 'inquiries', 27, 1, '2026-06-14 02:33:55'),
(159, 46, 'Inquiry Submitted', 'Your inquiry has been received. An agent will follow up shortly.', 'in_app', 'inquiries', 33, 1, '2026-06-14 02:40:25'),
(160, 46, 'Inquiry Submitted', 'Your inquiry has been received. An agent will follow up shortly.', 'in_app', 'inquiries', 34, 1, '2026-06-14 02:46:02'),
(161, 46, 'Inquiry Submitted', 'Your inquiry has been received. An agent will follow up shortly.', 'in_app', 'inquiries', 35, 1, '2026-06-14 02:49:38'),
(162, 46, 'Payment Submitted', 'Your payment of 37410.48 for schedule #578 has been submitted for review.', 'in_app', 'payments', 22, 1, '2026-06-14 03:05:34'),
(163, 48, 'Payment Pending Review', 'Customer #46 submitted a payment of 37410.48 for schedule #578.', 'in_app', 'payments', 22, 1, '2026-06-14 03:05:34'),
(164, 46, 'Payment Approved', 'Your payment of 37410.48 has been approved.', 'in_app', 'payments', 22, 1, '2026-06-14 03:12:45'),
(165, 46, 'Warranty Claim Submitted', 'Your warranty claim has been received and is under review.', 'in_app', 'warranty_claims', 3, 1, '2026-06-14 03:20:17'),
(166, 1, 'New Warranty Claim', 'Customer #46 submitted a repair claim for Toyota Fortuner GR Sport.', 'in_app', 'warranty_claims', 3, 0, '2026-06-14 03:20:17'),
(167, 6, 'New Warranty Claim', 'Customer #46 submitted a repair claim for Toyota Fortuner GR Sport.', 'in_app', 'warranty_claims', 3, 0, '2026-06-14 03:20:17'),
(168, 2, 'New Warranty Claim', 'Customer #46 submitted a repair claim for Toyota Fortuner GR Sport.', 'in_app', 'warranty_claims', 3, 0, '2026-06-14 03:20:17'),
(169, 3, 'New Warranty Claim', 'Customer #46 submitted a repair claim for Toyota Fortuner GR Sport.', 'in_app', 'warranty_claims', 3, 0, '2026-06-14 03:20:17'),
(170, 29, 'New Warranty Claim', 'Customer #46 submitted a repair claim for Toyota Fortuner GR Sport.', 'in_app', 'warranty_claims', 3, 0, '2026-06-14 03:20:17'),
(171, 30, 'New Warranty Claim', 'Customer #46 submitted a repair claim for Toyota Fortuner GR Sport.', 'in_app', 'warranty_claims', 3, 0, '2026-06-14 03:20:17'),
(172, 33, 'New Warranty Claim', 'Customer #46 submitted a repair claim for Toyota Fortuner GR Sport.', 'in_app', 'warranty_claims', 3, 0, '2026-06-14 03:20:17'),
(173, 50, 'New Warranty Claim', 'Customer #46 submitted a repair claim for Toyota Fortuner GR Sport.', 'in_app', 'warranty_claims', 3, 0, '2026-06-14 03:20:17'),
(174, 46, 'Warranty Claim Submitted', 'Your warranty claim has been received and is under review.', 'in_app', 'warranty_claims', 4, 1, '2026-06-14 03:23:09'),
(175, 1, 'New Warranty Claim', 'Customer #46 submitted a repair claim for Toyota Fortuner GR Sport.', 'in_app', 'warranty_claims', 4, 0, '2026-06-14 03:23:09'),
(176, 6, 'New Warranty Claim', 'Customer #46 submitted a repair claim for Toyota Fortuner GR Sport.', 'in_app', 'warranty_claims', 4, 1, '2026-06-14 03:23:09'),
(177, 2, 'New Warranty Claim', 'Customer #46 submitted a repair claim for Toyota Fortuner GR Sport.', 'in_app', 'warranty_claims', 4, 0, '2026-06-14 03:23:09'),
(178, 3, 'New Warranty Claim', 'Customer #46 submitted a repair claim for Toyota Fortuner GR Sport.', 'in_app', 'warranty_claims', 4, 0, '2026-06-14 03:23:09'),
(179, 29, 'New Warranty Claim', 'Customer #46 submitted a repair claim for Toyota Fortuner GR Sport.', 'in_app', 'warranty_claims', 4, 0, '2026-06-14 03:23:09'),
(180, 30, 'New Warranty Claim', 'Customer #46 submitted a repair claim for Toyota Fortuner GR Sport.', 'in_app', 'warranty_claims', 4, 0, '2026-06-14 03:23:09'),
(181, 33, 'New Warranty Claim', 'Customer #46 submitted a repair claim for Toyota Fortuner GR Sport.', 'in_app', 'warranty_claims', 4, 0, '2026-06-14 03:23:09'),
(182, 50, 'New Warranty Claim', 'Customer #46 submitted a repair claim for Toyota Fortuner GR Sport.', 'in_app', 'warranty_claims', 4, 0, '2026-06-14 03:23:09'),
(183, 46, 'Estimate Ready for Signature', 'Your service estimate is ready. Please review and sign digitally.', 'in_app', 'service_bookings', 4, 1, '2026-06-14 03:31:48'),
(184, 2, 'New Booking', 'Maintenance booking #5 created.', 'in_app', 'service_bookings', 5, 0, '2026-06-14 03:39:06'),
(185, 3, 'New Booking', 'Maintenance booking #5 created.', 'in_app', 'service_bookings', 5, 0, '2026-06-14 03:39:06'),
(186, 29, 'New Booking', 'Maintenance booking #5 created.', 'in_app', 'service_bookings', 5, 0, '2026-06-14 03:39:06'),
(187, 30, 'New Booking', 'Maintenance booking #5 created.', 'in_app', 'service_bookings', 5, 0, '2026-06-14 03:39:06'),
(188, 33, 'New Booking', 'Maintenance booking #5 created.', 'in_app', 'service_bookings', 5, 0, '2026-06-14 03:39:06'),
(189, 50, 'New Booking', 'Maintenance booking #5 created.', 'in_app', 'service_bookings', 5, 0, '2026-06-14 03:39:06'),
(190, 1, 'New Booking', 'Maintenance booking #5 created.', 'in_app', 'service_bookings', 5, 0, '2026-06-14 03:39:06'),
(191, 6, 'New Booking', 'Maintenance booking #5 created.', 'in_app', 'service_bookings', 5, 1, '2026-06-14 03:39:06'),
(192, 2, 'New Booking', 'Repair booking #6 created.', 'in_app', 'service_bookings', 6, 0, '2026-06-14 03:40:01'),
(193, 3, 'New Booking', 'Repair booking #6 created.', 'in_app', 'service_bookings', 6, 0, '2026-06-14 03:40:01'),
(194, 29, 'New Booking', 'Repair booking #6 created.', 'in_app', 'service_bookings', 6, 0, '2026-06-14 03:40:01'),
(195, 30, 'New Booking', 'Repair booking #6 created.', 'in_app', 'service_bookings', 6, 1, '2026-06-14 03:40:01'),
(196, 33, 'New Booking', 'Repair booking #6 created.', 'in_app', 'service_bookings', 6, 0, '2026-06-14 03:40:01'),
(197, 50, 'New Booking', 'Repair booking #6 created.', 'in_app', 'service_bookings', 6, 0, '2026-06-14 03:40:01'),
(198, 1, 'New Booking', 'Repair booking #6 created.', 'in_app', 'service_bookings', 6, 0, '2026-06-14 03:40:01'),
(199, 6, 'New Booking', 'Repair booking #6 created.', 'in_app', 'service_bookings', 6, 1, '2026-06-14 03:40:01'),
(200, 36, 'Booking Confirmed', 'Your service booking has been confirmed.', 'in_app', 'service_bookings', 5, 0, '2026-06-14 03:40:27'),
(201, 46, 'Draft Estimate Ready', 'A draft estimate for booking #6 has been prepared by our service team. Please check your portal for details.', 'in_app', 'service_bookings', 6, 1, '2026-06-14 03:48:30'),
(202, 46, 'Draft Estimate Ready', 'A draft estimate for booking #6 has been prepared by our service team. Please check your portal for details.', 'in_app', 'service_bookings', 6, 1, '2026-06-14 03:50:07'),
(203, 2, 'New Booking', 'Repair booking #7 created.', 'in_app', 'service_bookings', 7, 0, '2026-06-14 03:55:53'),
(204, 3, 'New Booking', 'Repair booking #7 created.', 'in_app', 'service_bookings', 7, 0, '2026-06-14 03:55:53'),
(205, 29, 'New Booking', 'Repair booking #7 created.', 'in_app', 'service_bookings', 7, 0, '2026-06-14 03:55:53'),
(206, 30, 'New Booking', 'Repair booking #7 created.', 'in_app', 'service_bookings', 7, 1, '2026-06-14 03:55:53'),
(207, 33, 'New Booking', 'Repair booking #7 created.', 'in_app', 'service_bookings', 7, 0, '2026-06-14 03:55:53'),
(208, 50, 'New Booking', 'Repair booking #7 created.', 'in_app', 'service_bookings', 7, 0, '2026-06-14 03:55:53'),
(209, 1, 'New Booking', 'Repair booking #7 created.', 'in_app', 'service_bookings', 7, 0, '2026-06-14 03:55:53'),
(210, 6, 'New Booking', 'Repair booking #7 created.', 'in_app', 'service_bookings', 7, 1, '2026-06-14 03:55:53'),
(211, 36, 'Estimate Ready for Signature', 'Your service estimate is ready. Please review and sign digitally.', 'in_app', 'service_bookings', 7, 0, '2026-06-14 03:55:53'),
(212, 49, 'Customer Acknowledged Estimate', 'The customer has acknowledged the estimate for booking #6 and confirmed they want to proceed with the repair.', 'in_app', 'service_bookings', 6, 1, '2026-06-14 03:57:32'),
(213, 2, 'New Booking', 'Repair booking #8 created.', 'in_app', 'service_bookings', 8, 0, '2026-06-14 03:58:03'),
(214, 3, 'New Booking', 'Repair booking #8 created.', 'in_app', 'service_bookings', 8, 0, '2026-06-14 03:58:03'),
(215, 29, 'New Booking', 'Repair booking #8 created.', 'in_app', 'service_bookings', 8, 0, '2026-06-14 03:58:03'),
(216, 30, 'New Booking', 'Repair booking #8 created.', 'in_app', 'service_bookings', 8, 1, '2026-06-14 03:58:03'),
(217, 33, 'New Booking', 'Repair booking #8 created.', 'in_app', 'service_bookings', 8, 0, '2026-06-14 03:58:03'),
(218, 50, 'New Booking', 'Repair booking #8 created.', 'in_app', 'service_bookings', 8, 0, '2026-06-14 03:58:03'),
(219, 1, 'New Booking', 'Repair booking #8 created.', 'in_app', 'service_bookings', 8, 0, '2026-06-14 03:58:03'),
(220, 6, 'New Booking', 'Repair booking #8 created.', 'in_app', 'service_bookings', 8, 1, '2026-06-14 03:58:03'),
(221, 49, 'Customer Acknowledged Estimate', 'The customer has acknowledged the estimate for booking #8 and confirmed they want to proceed with the repair.', 'in_app', 'service_bookings', 8, 1, '2026-06-14 03:58:04'),
(222, 36, 'Repair Confirmed', 'Your repair for Toyota Fortuner GR Sport on Sun, Jun 14 at 11:58 AM has been confirmed! Total estimate: ₱3,808.00. Please bring your vehicle on time. You can view the full estimate details in your portal.', 'in_app', 'service_bookings', 8, 0, '2026-06-14 04:02:36'),
(223, 49, 'Customer Confirmed Repair', 'The customer has acknowledged the estimate for booking #8 (Toyota Fortuner GR Sport) and confirmed they will proceed. Status is now \'confirmed\'.', 'in_app', 'service_bookings', 8, 1, '2026-06-14 04:02:36'),
(224, 2, 'New Booking', 'Maintenance booking #9 created.', 'in_app', 'service_bookings', 9, 0, '2026-06-14 04:02:49'),
(225, 3, 'New Booking', 'Maintenance booking #9 created.', 'in_app', 'service_bookings', 9, 0, '2026-06-14 04:02:49'),
(226, 29, 'New Booking', 'Maintenance booking #9 created.', 'in_app', 'service_bookings', 9, 0, '2026-06-14 04:02:49'),
(227, 30, 'New Booking', 'Maintenance booking #9 created.', 'in_app', 'service_bookings', 9, 1, '2026-06-14 04:02:49'),
(228, 33, 'New Booking', 'Maintenance booking #9 created.', 'in_app', 'service_bookings', 9, 0, '2026-06-14 04:02:49'),
(229, 50, 'New Booking', 'Maintenance booking #9 created.', 'in_app', 'service_bookings', 9, 0, '2026-06-14 04:02:49'),
(230, 1, 'New Booking', 'Maintenance booking #9 created.', 'in_app', 'service_bookings', 9, 0, '2026-06-14 04:02:49'),
(231, 6, 'New Booking', 'Maintenance booking #9 created.', 'in_app', 'service_bookings', 9, 1, '2026-06-14 04:02:49'),
(232, 2, 'New Booking', 'Maintenance booking #10 created.', 'in_app', 'service_bookings', 10, 0, '2026-06-14 04:05:14'),
(233, 3, 'New Booking', 'Maintenance booking #10 created.', 'in_app', 'service_bookings', 10, 0, '2026-06-14 04:05:14'),
(234, 29, 'New Booking', 'Maintenance booking #10 created.', 'in_app', 'service_bookings', 10, 0, '2026-06-14 04:05:14'),
(235, 30, 'New Booking', 'Maintenance booking #10 created.', 'in_app', 'service_bookings', 10, 1, '2026-06-14 04:05:14'),
(236, 33, 'New Booking', 'Maintenance booking #10 created.', 'in_app', 'service_bookings', 10, 0, '2026-06-14 04:05:14'),
(237, 50, 'New Booking', 'Maintenance booking #10 created.', 'in_app', 'service_bookings', 10, 0, '2026-06-14 04:05:14'),
(238, 1, 'New Booking', 'Maintenance booking #10 created.', 'in_app', 'service_bookings', 10, 0, '2026-06-14 04:05:14'),
(239, 6, 'New Booking', 'Maintenance booking #10 created.', 'in_app', 'service_bookings', 10, 1, '2026-06-14 04:05:14'),
(240, 36, 'Booking Confirmed', 'Your maintenance booking for Toyota Fortuner GR Sport on Sunday, June 14 at 12:05 PM has been received. We\'ll notify you once the estimate is ready.', 'in_app', 'service_bookings', 10, 0, '2026-06-14 04:05:14'),
(241, 46, 'Draft Estimate Ready', 'A draft estimate for booking #6 has been prepared by our service team. Please check your portal for details.', 'in_app', 'service_bookings', 6, 1, '2026-06-14 04:13:51'),
(242, 46, 'Repair Confirmed', 'Your repair for Toyota Fortuner GR Sport on Sun, Jun 14 at 11:40 AM has been confirmed! Total estimate: ₱3,808.00. Please bring your vehicle on time. You can view the full estimate details in your portal.', 'in_app', 'service_bookings', 6, 1, '2026-06-14 04:14:01'),
(243, 49, 'Customer Confirmed Repair', 'The customer has acknowledged the estimate for booking #6 (Toyota Fortuner GR Sport) and confirmed they will proceed. Status is now \'confirmed\'.', 'in_app', 'service_bookings', 6, 1, '2026-06-14 04:14:01'),
(244, 36, 'Booking Confirmed', 'Your service booking has been confirmed.', 'in_app', 'service_bookings', 10, 0, '2026-06-14 04:14:50'),
(245, 2, 'New Booking', 'Maintenance booking #11 created.', 'in_app', 'service_bookings', 11, 0, '2026-06-14 04:17:40'),
(246, 3, 'New Booking', 'Maintenance booking #11 created.', 'in_app', 'service_bookings', 11, 0, '2026-06-14 04:17:40'),
(247, 29, 'New Booking', 'Maintenance booking #11 created.', 'in_app', 'service_bookings', 11, 0, '2026-06-14 04:17:40'),
(248, 30, 'New Booking', 'Maintenance booking #11 created.', 'in_app', 'service_bookings', 11, 1, '2026-06-14 04:17:40'),
(249, 33, 'New Booking', 'Maintenance booking #11 created.', 'in_app', 'service_bookings', 11, 0, '2026-06-14 04:17:40'),
(250, 50, 'New Booking', 'Maintenance booking #11 created.', 'in_app', 'service_bookings', 11, 0, '2026-06-14 04:17:40'),
(251, 1, 'New Booking', 'Maintenance booking #11 created.', 'in_app', 'service_bookings', 11, 0, '2026-06-14 04:17:40'),
(252, 6, 'New Booking', 'Maintenance booking #11 created.', 'in_app', 'service_bookings', 11, 1, '2026-06-14 04:17:40'),
(253, 36, 'Booking Confirmed', 'Your maintenance booking for Toyota Fortuner GR Sport on Sunday, June 14 at 12:17 PM has been received. We\'ll notify you once the estimate is ready.', 'in_app', 'service_bookings', 11, 0, '2026-06-14 04:17:40'),
(254, 36, 'Booking Confirmed', 'Your service booking has been confirmed.', 'in_app', 'service_bookings', 11, 0, '2026-06-14 04:17:41'),
(255, 46, 'Warranty Approved', 'Your warranty claim #4 has been approved! You may now bring your vehicle to our dealership for service. Please book a service appointment through your portal.', 'in_app', 'warranty_claims', 4, 1, '2026-06-14 04:32:39'),
(256, 35, 'Inquiry Resolved', 'Your inquiry #11 has been resolved. Thank you!', 'in_app', 'inquiries', 11, 0, '2026-06-14 04:40:02'),
(257, 2, 'New Booking', 'Test Drive booking #12 created.', 'in_app', 'service_bookings', 12, 0, '2026-06-14 05:11:48'),
(258, 3, 'New Booking', 'Test Drive booking #12 created.', 'in_app', 'service_bookings', 12, 0, '2026-06-14 05:11:48'),
(259, 29, 'New Booking', 'Test Drive booking #12 created.', 'in_app', 'service_bookings', 12, 0, '2026-06-14 05:11:48'),
(260, 30, 'New Booking', 'Test Drive booking #12 created.', 'in_app', 'service_bookings', 12, 1, '2026-06-14 05:11:48'),
(261, 33, 'New Booking', 'Test Drive booking #12 created.', 'in_app', 'service_bookings', 12, 0, '2026-06-14 05:11:48'),
(262, 50, 'New Booking', 'Test Drive booking #12 created.', 'in_app', 'service_bookings', 12, 0, '2026-06-14 05:11:48'),
(263, 1, 'New Booking', 'Test Drive booking #12 created.', 'in_app', 'service_bookings', 12, 0, '2026-06-14 05:11:48'),
(264, 6, 'New Booking', 'Test Drive booking #12 created.', 'in_app', 'service_bookings', 12, 1, '2026-06-14 05:11:48'),
(265, 46, 'Booking Confirmed', 'Your test drive booking for BYD SEALION on Monday, June 15 at 10:00 AM has been received. We\'ll notify you once the estimate is ready.', 'in_app', 'service_bookings', 12, 1, '2026-06-14 05:11:48'),
(266, 46, 'Booking Confirmed', 'Your service booking has been confirmed.', 'in_app', 'service_bookings', 12, 1, '2026-06-14 05:12:05'),
(267, 46, 'Warranty Resolved', 'Your warranty claim has been resolved.', 'in_app', 'warranty_claims', 4, 1, '2026-06-14 07:00:05'),
(268, 5, 'Warranty Resolved', 'Your warranty claim has been resolved.', 'in_app', 'warranty_claims', 1, 0, '2026-06-14 07:00:06'),
(269, 31, 'Payment Received', 'A payment of 5000.0 has been recorded for sale #25.', 'in_app', 'payments', 23, 0, '2026-06-14 07:33:03'),
(270, 2, 'New Booking', 'Test Drive booking #13 created.', 'in_app', 'service_bookings', 13, 0, '2026-06-14 08:03:33'),
(271, 3, 'New Booking', 'Test Drive booking #13 created.', 'in_app', 'service_bookings', 13, 0, '2026-06-14 08:03:33'),
(272, 29, 'New Booking', 'Test Drive booking #13 created.', 'in_app', 'service_bookings', 13, 0, '2026-06-14 08:03:33'),
(273, 30, 'New Booking', 'Test Drive booking #13 created.', 'in_app', 'service_bookings', 13, 1, '2026-06-14 08:03:33'),
(274, 33, 'New Booking', 'Test Drive booking #13 created.', 'in_app', 'service_bookings', 13, 0, '2026-06-14 08:03:33'),
(275, 50, 'New Booking', 'Test Drive booking #13 created.', 'in_app', 'service_bookings', 13, 0, '2026-06-14 08:03:33'),
(276, 1, 'New Booking', 'Test Drive booking #13 created.', 'in_app', 'service_bookings', 13, 0, '2026-06-14 08:03:33'),
(277, 6, 'New Booking', 'Test Drive booking #13 created.', 'in_app', 'service_bookings', 13, 1, '2026-06-14 08:03:33'),
(278, 46, 'Booking Confirmed', 'Your test drive booking for BYD SEALION on Wednesday, June 17 at 10:00 AM has been received. We\'ll notify you once the estimate is ready.', 'in_app', 'service_bookings', 13, 1, '2026-06-14 08:03:33'),
(279, 2, 'New Booking', 'Test Drive booking #14 created.', 'in_app', 'service_bookings', 14, 0, '2026-06-14 08:05:58'),
(280, 3, 'New Booking', 'Test Drive booking #14 created.', 'in_app', 'service_bookings', 14, 0, '2026-06-14 08:05:58'),
(281, 29, 'New Booking', 'Test Drive booking #14 created.', 'in_app', 'service_bookings', 14, 0, '2026-06-14 08:05:58'),
(282, 30, 'New Booking', 'Test Drive booking #14 created.', 'in_app', 'service_bookings', 14, 1, '2026-06-14 08:05:58'),
(283, 33, 'New Booking', 'Test Drive booking #14 created.', 'in_app', 'service_bookings', 14, 0, '2026-06-14 08:05:58'),
(284, 50, 'New Booking', 'Test Drive booking #14 created.', 'in_app', 'service_bookings', 14, 0, '2026-06-14 08:05:58'),
(285, 1, 'New Booking', 'Test Drive booking #14 created.', 'in_app', 'service_bookings', 14, 0, '2026-06-14 08:05:58'),
(286, 6, 'New Booking', 'Test Drive booking #14 created.', 'in_app', 'service_bookings', 14, 1, '2026-06-14 08:05:58'),
(287, 2, 'Vehicle Reserved', 'Customer reserved BYD SEALION (#11).', 'in_app', 'inquiries', 36, 0, '2026-06-14 08:06:31'),
(288, 3, 'Vehicle Reserved', 'Customer reserved BYD SEALION (#11).', 'in_app', 'inquiries', 36, 0, '2026-06-14 08:06:31'),
(289, 29, 'Vehicle Reserved', 'Customer reserved BYD SEALION (#11).', 'in_app', 'inquiries', 36, 0, '2026-06-14 08:06:31'),
(290, 30, 'Vehicle Reserved', 'Customer reserved BYD SEALION (#11).', 'in_app', 'inquiries', 36, 1, '2026-06-14 08:06:31'),
(291, 33, 'Vehicle Reserved', 'Customer reserved BYD SEALION (#11).', 'in_app', 'inquiries', 36, 0, '2026-06-14 08:06:31'),
(292, 50, 'Vehicle Reserved', 'Customer reserved BYD SEALION (#11).', 'in_app', 'inquiries', 36, 0, '2026-06-14 08:06:31'),
(293, 46, 'Reservation Confirmed', 'You have reserved the BYD SEALION. An agent will follow up.', 'in_app', 'inquiries', 36, 0, '2026-06-14 08:06:31'),
(294, 46, 'Booking Confirmed', 'Your service booking has been confirmed.', 'in_app', 'service_bookings', 13, 0, '2026-06-14 08:07:43'),
(295, 46, 'Booking Confirmed', 'Your service booking has been confirmed.', 'in_app', 'service_bookings', 14, 0, '2026-06-14 08:07:44'),
(296, 1, 'Inquiry Self-Assigned', 'Agent gianna252 has self-assigned inquiry #36.', 'in_app', 'inquiries', 36, 0, '2026-06-14 08:07:54'),
(297, 6, 'Inquiry Self-Assigned', 'Agent gianna252 has self-assigned inquiry #36.', 'in_app', 'inquiries', 36, 1, '2026-06-14 08:07:54'),
(298, 46, 'Inquiry Assigned', 'Your inquiry #36 has been assigned to gianna252. They will contact you soon.', 'in_app', 'inquiries', 36, 0, '2026-06-14 08:07:54'),
(299, 46, 'Payment Received', 'A payment of 37000.0 has been recorded for sale #24.', 'in_app', 'payments', 25, 1, '2026-06-14 08:35:24'),
(300, 46, 'Warranty Approved', 'Your warranty claim #3 has been approved! You may now bring your vehicle to our dealership for service. Please book a service appointment through your portal.', 'in_app', 'warranty_claims', 3, 1, '2026-06-14 08:36:18'),
(301, 46, 'Warranty Resolved', 'Your warranty claim has been resolved.', 'in_app', 'warranty_claims', 3, 1, '2026-06-14 08:36:34'),
(302, 48, 'New Sale for Review', 'gianna252 created Sale #26 for Honda SADASD — ₱1,800,000.00 (full_payment). Pending processing.', 'in_app', 'sales', 26, 1, '2026-06-14 09:38:50'),
(303, 51, 'Account Created', 'Your AutoMatik account (CUST-giannaizabel-3886) has been created. Welcome!', 'in_app', 'users', 51, 0, '2026-06-14 09:38:56'),
(304, 51, 'Sale Created', 'Sale #26 has been created for Honda SADASD.', 'in_app', 'sales', 26, 0, '2026-06-14 09:39:03'),
(305, 1, 'Inquiry Self-Assigned', 'Agent gianna252 has self-assigned inquiry #35.', 'in_app', 'inquiries', 35, 0, '2026-06-14 09:51:22'),
(306, 6, 'Inquiry Self-Assigned', 'Agent gianna252 has self-assigned inquiry #35.', 'in_app', 'inquiries', 35, 1, '2026-06-14 09:51:22'),
(307, 46, 'Inquiry Assigned', 'Your inquiry #35 has been assigned to gianna252. They will contact you soon.', 'in_app', 'inquiries', 35, 1, '2026-06-14 09:51:22'),
(308, 1, 'Inquiry Self-Assigned', 'Agent gianna252 has self-assigned inquiry #33.', 'in_app', 'inquiries', 33, 0, '2026-06-14 09:53:26'),
(309, 6, 'Inquiry Self-Assigned', 'Agent gianna252 has self-assigned inquiry #33.', 'in_app', 'inquiries', 33, 1, '2026-06-14 09:53:26'),
(310, 46, 'Inquiry Assigned', 'Your inquiry #33 has been assigned to gianna252. They will contact you soon.', 'in_app', 'inquiries', 33, 1, '2026-06-14 09:53:26'),
(311, 46, 'Inquiry Resolved', 'Your inquiry #33 has been resolved by gianna252. Thank you!', 'in_app', 'inquiries', 33, 1, '2026-06-14 09:55:15'),
(312, 1, 'Inquiry Resolved', 'Inquiry #33 has been resolved by gianna252.', 'in_app', 'inquiries', 33, 0, '2026-06-14 09:55:17'),
(313, 6, 'Inquiry Resolved', 'Inquiry #33 has been resolved by gianna252.', 'in_app', 'inquiries', 33, 1, '2026-06-14 09:55:17'),
(314, 46, 'Payment Submitted', 'Your payment of 37410.48 for schedule #579 has been submitted for review.', 'in_app', 'payments', 26, 1, '2026-06-14 09:57:26'),
(315, 48, 'Payment Pending Review', 'Customer #46 submitted a payment of 37410.48 for schedule #579.', 'in_app', 'payments', 26, 1, '2026-06-14 09:57:26'),
(316, 46, 'Payment Approved', 'Your payment of 37410.48 has been approved.', 'in_app', 'payments', 26, 1, '2026-06-14 09:58:42'),
(317, 5, 'Amortization Updated', 'Amortization period #1 marked as paid.', 'in_app', 'amortization_schedule', 24, 0, '2026-06-14 10:05:44'),
(318, 2, 'Vehicle Reserved (Guest)', 'Guest Lance Kit Gom-os reserved Toyota Vios 1.3 XLE M/T (#12).', 'in_app', 'inquiries', 38, 0, '2026-06-14 15:38:49'),
(319, 3, 'Vehicle Reserved (Guest)', 'Guest Lance Kit Gom-os reserved Toyota Vios 1.3 XLE M/T (#12).', 'in_app', 'inquiries', 38, 0, '2026-06-14 15:38:49'),
(320, 29, 'Vehicle Reserved (Guest)', 'Guest Lance Kit Gom-os reserved Toyota Vios 1.3 XLE M/T (#12).', 'in_app', 'inquiries', 38, 0, '2026-06-14 15:38:49'),
(321, 30, 'Vehicle Reserved (Guest)', 'Guest Lance Kit Gom-os reserved Toyota Vios 1.3 XLE M/T (#12).', 'in_app', 'inquiries', 38, 1, '2026-06-14 15:38:49'),
(322, 33, 'Vehicle Reserved (Guest)', 'Guest Lance Kit Gom-os reserved Toyota Vios 1.3 XLE M/T (#12).', 'in_app', 'inquiries', 38, 0, '2026-06-14 15:38:49'),
(323, 50, 'Vehicle Reserved (Guest)', 'Guest Lance Kit Gom-os reserved Toyota Vios 1.3 XLE M/T (#12).', 'in_app', 'inquiries', 38, 0, '2026-06-14 15:38:49'),
(324, 2, 'Vehicle Reserved (Guest)', 'Guest Lance Kit Gom-os reserved Honda SADASD (#9).', 'in_app', 'inquiries', 39, 0, '2026-06-14 15:52:06'),
(325, 3, 'Vehicle Reserved (Guest)', 'Guest Lance Kit Gom-os reserved Honda SADASD (#9).', 'in_app', 'inquiries', 39, 0, '2026-06-14 15:52:06'),
(326, 29, 'Vehicle Reserved (Guest)', 'Guest Lance Kit Gom-os reserved Honda SADASD (#9).', 'in_app', 'inquiries', 39, 0, '2026-06-14 15:52:06'),
(327, 30, 'Vehicle Reserved (Guest)', 'Guest Lance Kit Gom-os reserved Honda SADASD (#9).', 'in_app', 'inquiries', 39, 1, '2026-06-14 15:52:06'),
(328, 33, 'Vehicle Reserved (Guest)', 'Guest Lance Kit Gom-os reserved Honda SADASD (#9).', 'in_app', 'inquiries', 39, 0, '2026-06-14 15:52:06'),
(329, 50, 'Vehicle Reserved (Guest)', 'Guest Lance Kit Gom-os reserved Honda SADASD (#9).', 'in_app', 'inquiries', 39, 0, '2026-06-14 15:52:06'),
(330, 1, 'Inquiry Self-Assigned', 'Agent gianna252 has self-assigned inquiry #34.', 'in_app', 'inquiries', 34, 0, '2026-06-14 16:16:55'),
(331, 6, 'Inquiry Self-Assigned', 'Agent gianna252 has self-assigned inquiry #34.', 'in_app', 'inquiries', 34, 1, '2026-06-14 16:16:55'),
(332, 46, 'Inquiry Assigned', 'Your inquiry #34 has been assigned to gianna252. They will contact you soon.', 'in_app', 'inquiries', 34, 1, '2026-06-14 16:16:55'),
(333, 46, 'Inquiry Resolved', 'Your inquiry #35 has been resolved by gianna252. Thank you!', 'in_app', 'inquiries', 35, 1, '2026-06-14 16:17:00'),
(334, 1, 'Inquiry Resolved', 'Inquiry #35 has been resolved by gianna252.', 'in_app', 'inquiries', 35, 0, '2026-06-14 16:17:01'),
(335, 6, 'Inquiry Resolved', 'Inquiry #35 has been resolved by gianna252.', 'in_app', 'inquiries', 35, 1, '2026-06-14 16:17:01'),
(336, 46, 'Payment Submitted', 'Your payment of 37410.48 for schedule #580 has been submitted for review.', 'in_app', 'payments', 28, 1, '2026-06-14 16:18:10'),
(337, 48, 'Payment Pending Review', 'Customer #46 submitted a payment of 37410.48 for schedule #580.', 'in_app', 'payments', 28, 1, '2026-06-14 16:18:10'),
(338, 1, 'New Guest Booking', 'Guest Gianna Izabelle Cantillo booked a test drive (#15).', 'in_app', 'service_bookings', 15, 0, '2026-06-14 16:26:26'),
(339, 6, 'New Guest Booking', 'Guest Gianna Izabelle Cantillo booked a test drive (#15).', 'in_app', 'service_bookings', 15, 1, '2026-06-14 16:26:26'),
(340, 30, 'Inquiry Closed', 'Inquiry #2 has been closed by admin.', 'in_app', 'inquiries', 2, 1, '2026-06-14 18:51:32'),
(341, 35, 'Inquiry Closed', 'Your inquiry has been closed. If you need further assistance, please submit a new inquiry.', 'in_app', 'inquiries', 11, 0, '2026-06-14 18:51:42'),
(342, 30, 'Inquiry Closed', 'Inquiry #11 has been closed by admin.', 'in_app', 'inquiries', 11, 1, '2026-06-14 18:51:42'),
(343, 46, 'Inquiry Closed', 'Your inquiry has been closed. If you need further assistance, please submit a new inquiry.', 'in_app', 'inquiries', 33, 1, '2026-06-14 18:51:44'),
(344, 30, 'Inquiry Closed', 'Inquiry #33 has been closed by admin.', 'in_app', 'inquiries', 33, 1, '2026-06-14 18:51:44'),
(345, 48, 'New Sale for Review', 'gianna252 created Sale #27 for Mitsubishi Xpander GLS A/T	 — ₱1,000,000.00 (full_payment). Pending processing.', 'in_app', 'sales', 27, 0, '2026-06-14 19:18:27'),
(346, 51, 'Sale Created', 'Sale #27 has been created for Mitsubishi Xpander GLS A/T	.', 'in_app', 'sales', 27, 0, '2026-06-14 19:18:27'),
(347, 46, 'Payment Rejected', 'Your payment of 37410.48 was rejected. no proof', 'in_app', 'payments', 28, 0, '2026-06-14 19:48:20'),
(348, 46, 'Payment Rejected', 'Your payment of 37000.00 was rejected. no proof', 'in_app', 'payments', 25, 0, '2026-06-14 19:48:37'),
(349, 46, 'Payment Approved', 'Your payment of 37410.48 has been approved.', 'in_app', 'payments', 19, 0, '2026-06-14 20:05:52'),
(350, 31, 'Payment Approved', 'Your payment of 5000.00 has been approved.', 'in_app', 'payments', 23, 0, '2026-06-14 20:06:25'),
(351, 46, 'Payment Received', 'A payment of 67.0 has been recorded for sale #24.', 'in_app', 'payments', 29, 0, '2026-06-14 20:13:47'),
(352, 46, 'Payment Rejected', 'Your payment of 67.00 was rejected. bruh', 'in_app', 'payments', 29, 0, '2026-06-14 20:14:00'),
(353, 1, 'Inquiry Self-Assigned', 'Agent gianna252 has self-assigned inquiry #39.', 'in_app', 'inquiries', 39, 0, '2026-06-14 20:21:21'),
(354, 6, 'Inquiry Self-Assigned', 'Agent gianna252 has self-assigned inquiry #39.', 'in_app', 'inquiries', 39, 1, '2026-06-14 20:21:21'),
(355, 51, 'Payment Received', 'A payment of 9000000.0 has been recorded for sale #27.', 'in_app', 'payments', 30, 0, '2026-06-14 20:39:10'),
(356, 51, 'Payment Received', 'A payment of 9999999.0 has been recorded for sale #27.', 'in_app', 'payments', 31, 0, '2026-06-14 20:39:16'),
(357, 51, 'Payment Received', 'A payment of 20000000.0 has been recorded for sale #26.', 'in_app', 'payments', 32, 0, '2026-06-14 20:43:21'),
(358, 51, 'Payment Received', 'A payment of 1000000.0 has been recorded for sale #27.', 'in_app', 'payments', 33, 0, '2026-06-14 20:44:11'),
(359, 51, 'Sale Status Updated', 'Sale #27 status changed to \'completed\'.', 'in_app', 'sales', 27, 0, '2026-06-14 20:44:21'),
(360, 51, 'Payment Approved', 'Your payment of 1000000.00 has been approved.', 'in_app', 'payments', 33, 0, '2026-06-15 03:09:20');

-- --------------------------------------------------------

--
-- Table structure for table `payments`
--

CREATE TABLE `payments` (
  `payment_id` int(11) NOT NULL,
  `sale_id` int(11) DEFAULT NULL,
  `schedule_id` int(11) DEFAULT NULL,
  `amount_paid` decimal(12,2) NOT NULL,
  `payment_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `payment_method` enum('cash','bank_transfer','check','online') NOT NULL,
  `reference` varchar(100) DEFAULT NULL,
  `payment_allocation` enum('service_fee','maintenance','repair','amortization','full_cash','downpayment','reservation_fee') NOT NULL,
  `proof_of_payment` varchar(255) DEFAULT NULL,
  `recorded_by` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `review_status` varchar(50) DEFAULT 'pending_verification',
  `notes` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `payments`
--

INSERT INTO `payments` (`payment_id`, `sale_id`, `schedule_id`, `amount_paid`, `payment_date`, `payment_method`, `reference`, `payment_allocation`, `proof_of_payment`, `recorded_by`, `created_at`, `review_status`, `notes`) VALUES
(1, 1, NULL, 1648000.00, '2026-04-19 08:40:18', 'bank_transfer', 'BDO-TXN-20250310-001', 'service_fee', NULL, 1, '2026-04-19 08:40:18', 'pending_verification', NULL),
(2, 2, 1, 37373.45, '2026-04-19 08:40:18', 'online', 'BDO-AMO-20250515-001', 'service_fee', NULL, 1, '2026-04-19 08:40:18', 'pending_verification', NULL),
(3, 2, 2, 37373.45, '2026-04-19 08:40:18', 'online', 'BDO-AMO-20250615-001', 'service_fee', NULL, 1, '2026-04-19 08:40:18', 'pending_verification', NULL),
(5, 1, NULL, 500000.00, '2026-06-05 06:42:59', 'cash', NULL, 'service_fee', NULL, 6, '2026-06-05 06:42:59', 'pending_verification', NULL),
(19, 24, 576, 37410.48, '2026-06-05 10:14:21', 'cash', 'OR-001', 'service_fee', '/static/uploads/payments/1781243952_19.jpg', 6, '2026-06-05 10:14:21', 'verified', ''),
(20, 25, NULL, 798000.00, '2026-06-05 17:05:32', 'cash', NULL, 'service_fee', NULL, 33, '2026-06-05 17:05:32', 'pending_verification', NULL),
(21, NULL, NULL, 5000.00, '2026-06-14 01:55:46', 'online', NULL, 'reservation_fee', NULL, 46, '2026-06-14 01:55:46', 'pending_verification', NULL),
(22, 24, 578, 37410.48, '2026-06-14 03:05:34', 'bank_transfer', NULL, 'amortization', '/static/uploads/payments/1781406334_578.jpg', 46, '2026-06-14 03:05:34', 'verified', ''),
(23, 25, NULL, 5000.00, '2026-06-14 07:33:03', 'cash', NULL, 'service_fee', NULL, 6, '2026-06-14 07:33:03', 'verified', ''),
(24, NULL, NULL, 5000.00, '2026-06-14 08:07:01', 'online', NULL, 'reservation_fee', NULL, 46, '2026-06-14 08:07:01', 'pending_verification', NULL),
(25, 24, NULL, 37000.00, '2026-06-14 08:35:24', 'online', NULL, 'service_fee', NULL, 6, '2026-06-14 08:35:24', 'rejected', 'no proof'),
(26, 24, 579, 37410.48, '2026-06-14 09:57:26', 'bank_transfer', NULL, 'amortization', '/static/uploads/payments/1781431046_579.jpg', 46, '2026-06-14 09:57:26', 'verified', ''),
(27, NULL, NULL, 5000.00, '2026-06-14 15:52:08', 'online', NULL, 'reservation_fee', NULL, 1, '2026-06-14 15:52:08', 'pending_verification', NULL),
(28, 24, 580, 37410.48, '2026-06-14 16:18:10', 'bank_transfer', NULL, 'amortization', '/static/uploads/payments/1781453890_580.jpg', 46, '2026-06-14 16:18:10', 'rejected', 'no proof'),
(29, 24, NULL, 67.00, '2026-06-14 20:13:47', 'cash', NULL, 'service_fee', NULL, 48, '2026-06-14 20:13:47', 'rejected', 'bruh'),
(30, 27, NULL, 9000000.00, '2026-06-14 20:39:10', 'cash', NULL, 'full_cash', '/static/uploads/payments/1781469550_30.pdf', 6, '2026-06-14 20:39:10', 'pending_verification', NULL),
(31, 27, NULL, 9999999.00, '2026-06-14 20:39:16', 'cash', NULL, 'full_cash', NULL, 6, '2026-06-14 20:39:16', 'pending_verification', NULL),
(32, 26, NULL, 20000000.00, '2026-06-14 20:43:21', 'cash', NULL, 'full_cash', '/static/uploads/payments/1781469801_32.pdf', 6, '2026-06-14 20:43:21', 'pending_verification', NULL),
(33, 27, NULL, 1000000.00, '2026-06-14 20:44:11', 'cash', NULL, 'full_cash', NULL, 6, '2026-06-14 20:44:11', 'verified', '');

-- --------------------------------------------------------

--
-- Table structure for table `sales`
--

CREATE TABLE `sales` (
  `sale_id` int(11) NOT NULL,
  `vehicle_id` int(11) NOT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `agent_id` int(11) NOT NULL,
  `inquiry_id` int(11) DEFAULT NULL,
  `selling_price` decimal(12,2) NOT NULL,
  `payment_type` enum('full_payment','installment') NOT NULL,
  `sale_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `status` enum('pending','active','completed','cancelled') NOT NULL DEFAULT 'pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `sales`
--

INSERT INTO `sales` (`sale_id`, `vehicle_id`, `customer_id`, `agent_id`, `inquiry_id`, `selling_price`, `payment_type`, `sale_date`, `status`, `created_at`) VALUES
(1, 4, 5, 3, NULL, 1648000.00, 'full_payment', '2026-04-19 08:40:18', 'completed', '2026-04-19 08:40:18'),
(2, 1, 4, 2, 1, 2390000.00, 'installment', '2026-04-19 08:40:18', 'active', '2026-04-19 08:40:18'),
(3, 1, 36, 2, NULL, 2390000.00, 'installment', '2026-06-03 15:49:24', 'active', '2026-06-03 15:49:24'),
(7, 3, 5, 3, NULL, 1800000.00, 'full_payment', '2026-06-05 06:31:22', 'completed', '2026-06-05 06:31:22'),
(9, 3, 5, 3, NULL, 1800000.00, 'full_payment', '2026-06-05 06:32:16', 'pending', '2026-06-05 06:32:16'),
(10, 2, 34, 30, NULL, 798000.00, 'full_payment', '2026-06-05 07:29:19', 'pending', '2026-06-05 07:29:19'),
(24, 1, 46, 30, 25, 2390000.00, 'installment', '2026-06-05 10:14:05', 'completed', '2026-06-05 10:14:05'),
(25, 2, 31, 33, NULL, 798000.00, 'full_payment', '2026-06-05 17:05:32', 'pending', '2026-06-05 17:05:32'),
(26, 9, 51, 30, 37, 1800000.00, 'full_payment', '2026-06-14 09:38:50', 'pending', '2026-06-14 09:38:50'),
(27, 17, 51, 30, 40, 1000000.00, 'full_payment', '2026-06-14 19:18:27', 'completed', '2026-06-14 19:18:27');

-- --------------------------------------------------------

--
-- Table structure for table `sales_contracts`
--

CREATE TABLE `sales_contracts` (
  `contract_id` int(11) NOT NULL,
  `sale_id` int(11) NOT NULL,
  `contract_url` varchar(500) DEFAULT NULL,
  `status` enum('draft','pending_signature','signed','cancelled') NOT NULL DEFAULT 'draft',
  `signed_at` timestamp NULL DEFAULT NULL,
  `reviewed_by` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `sales_contracts`
--

INSERT INTO `sales_contracts` (`contract_id`, `sale_id`, `contract_url`, `status`, `signed_at`, `reviewed_by`, `created_at`) VALUES
(1, 1, 'https://docs.automatik.ph/contracts/SC-2025-001.pdf', 'signed', '2025-03-10 06:00:00', 1, '2026-04-19 08:40:18'),
(2, 2, 'https://docs.automatik.ph/contracts/SC-2025-002.pdf', 'signed', '2025-04-01 02:00:00', 1, '2026-04-19 08:40:18'),
(19, 24, NULL, 'draft', NULL, NULL, '2026-06-05 10:14:05'),
(20, 25, NULL, 'draft', NULL, NULL, '2026-06-05 17:05:32'),
(21, 26, NULL, 'draft', NULL, NULL, '2026-06-14 09:38:50'),
(22, 27, NULL, 'draft', NULL, NULL, '2026-06-14 19:18:27');

-- --------------------------------------------------------

--
-- Table structure for table `service_bookings`
--

CREATE TABLE `service_bookings` (
  `booking_id` int(11) NOT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `vehicle_id` int(11) NOT NULL,
  `slot_id` int(11) NOT NULL,
  `booking_type` enum('test_drive','maintenance','repair') NOT NULL,
  `warranty_claim_id` int(11) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `status` enum('pending','confirmed','completed','cancelled','draft_estimate','awaiting_signature','in_progress','pending_supplement','ready_for_testing','ready_for_checkout') NOT NULL DEFAULT 'pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `assigned_to` int(11) DEFAULT NULL,
  `technician_notes` text DEFAULT NULL,
  `estimate_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`estimate_data`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `service_bookings`
--

INSERT INTO `service_bookings` (`booking_id`, `customer_id`, `vehicle_id`, `slot_id`, `booking_type`, `warranty_claim_id`, `notes`, `status`, `created_at`, `assigned_to`, `technician_notes`, `estimate_data`) VALUES
(2, 36, 1, 235, 'maintenance', NULL, 'baho', 'completed', '2026-06-13 14:58:24', 49, 'krazy customer', NULL),
(3, 36, 1, 1334, 'maintenance', NULL, 'Test booking', 'completed', '2026-06-13 20:49:44', 49, 'Checked engine, all good', NULL),
(4, 46, 11, 1490, 'test_drive', NULL, NULL, 'cancelled', '2026-06-14 02:19:44', 49, NULL, '{\"parts\": [{\"description\": \"Oil Filter\", \"unit_cost\": 850, \"qty\": 1}, {\"description\": \"Engine Oil 5L\", \"unit_cost\": 1200, \"qty\": 2}], \"labor\": [{\"description\": \"Change oil & filter\", \"hours\": 1.5, \"rate\": 600}], \"misc\": [{\"description\": \"Shop supplies\", \"amount\": 250}], \"subtotal\": 4300, \"tax_rate\": 12, \"tax\": 516, \"total\": 4816, \"customer_notes\": \"Customer reported engine noise\"}'),
(5, 36, 1, 1337, 'maintenance', NULL, 'Check engine light is on, also weird noise from front left wheel', 'completed', '2026-06-14 03:39:06', 49, NULL, NULL),
(6, 46, 1, 1412, 'repair', NULL, 'nasira wahaha', 'confirmed', '2026-06-14 03:40:01', 49, NULL, '{\"parts\": [{\"description\": \"Brake Pads\", \"unit_cost\": 2500, \"qty\": 1}], \"labor\": [{\"description\": \"Replace brake pads\", \"hours\": 1, \"rate\": 600}], \"misc\": [{\"description\": \"Blood & Sweat\", \"amount\": 300}], \"subtotal\": 3400, \"tax_rate\": 12, \"tax\": 408, \"total\": 3808, \"customer_notes\": \"nasira wahaha\"}'),
(7, 36, 1, 1415, 'repair', NULL, '', 'in_progress', '2026-06-14 03:55:53', 49, '', '{\"parts\": [{\"description\": \"Brake Pads\", \"unit_cost\": 2500, \"qty\": 1}], \"labor\": [{\"description\": \"Replace brake pads\", \"hours\": 1.5, \"rate\": 600}], \"misc\": [], \"subtotal\": 3400, \"tax_rate\": 12, \"tax\": 408, \"total\": 3808, \"customer_notes\": \"Check brake noise\"}'),
(8, 36, 1, 1501, 'repair', NULL, '', 'confirmed', '2026-06-14 03:58:03', 49, NULL, '{\"parts\": [{\"description\": \"Brake Pads\", \"unit_cost\": 2500, \"qty\": 1}], \"labor\": [{\"description\": \"Replace brake pads\", \"hours\": 1.5, \"rate\": 600}], \"misc\": [], \"subtotal\": 3400, \"tax_rate\": 12, \"tax\": 408, \"total\": 3808, \"customer_notes\": \"Check brake noise\"}'),
(9, 46, 1, 1500, 'maintenance', NULL, 'test', 'cancelled', '2026-06-14 04:02:49', 49, NULL, NULL),
(10, 36, 1, 1500, 'maintenance', NULL, '', 'completed', '2026-06-14 04:05:14', 49, NULL, NULL),
(11, 36, 1, 1335, 'maintenance', NULL, '', 'completed', '2026-06-14 04:17:40', 49, NULL, NULL),
(12, 46, 11, 1490, 'test_drive', NULL, '', 'completed', '2026-06-14 05:11:47', 30, NULL, NULL),
(13, 46, 11, 1494, 'test_drive', NULL, '', 'completed', '2026-06-14 08:03:33', 30, NULL, NULL),
(14, 46, 11, 1494, 'test_drive', NULL, '', 'confirmed', '2026-06-14 08:05:58', 30, NULL, NULL),
(15, NULL, 5, 1498, 'test_drive', NULL, 'Guest: Gianna Izabelle Cantillo <tanjirokamado22222@gmail.com>', 'pending', '2026-06-14 16:26:26', NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `service_slots`
--

CREATE TABLE `service_slots` (
  `slot_id` int(11) NOT NULL,
  `slot_datetime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `slot_type` enum('test_drive','maintenance','repair') NOT NULL,
  `capacity` int(11) NOT NULL DEFAULT 1,
  `is_available` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `service_slots`
--

INSERT INTO `service_slots` (`slot_id`, `slot_datetime`, `slot_type`, `capacity`, `is_available`, `created_at`) VALUES
(1334, '2026-06-15 02:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1335, '2026-06-14 04:17:40', 'maintenance', 1, 0, '2026-06-13 20:39:28'),
(1336, '2026-06-15 08:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1337, '2026-06-14 03:39:06', 'maintenance', 1, 0, '2026-06-13 20:39:28'),
(1338, '2026-06-16 06:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1339, '2026-06-16 08:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1340, '2026-06-17 02:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1341, '2026-06-17 06:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1342, '2026-06-17 08:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1343, '2026-06-18 02:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1344, '2026-06-18 06:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1345, '2026-06-18 08:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1346, '2026-06-19 02:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1347, '2026-06-19 06:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1348, '2026-06-19 08:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1349, '2026-06-20 02:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1350, '2026-06-20 06:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1351, '2026-06-20 08:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1352, '2026-06-22 02:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1353, '2026-06-22 06:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1354, '2026-06-22 08:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1355, '2026-06-23 02:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1356, '2026-06-23 06:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1357, '2026-06-23 08:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1358, '2026-06-24 02:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1359, '2026-06-24 06:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1360, '2026-06-24 08:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1361, '2026-06-25 02:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1362, '2026-06-25 06:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1363, '2026-06-25 08:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1364, '2026-06-26 02:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1365, '2026-06-26 06:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1366, '2026-06-26 08:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1367, '2026-06-27 02:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1368, '2026-06-27 06:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1369, '2026-06-27 08:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1370, '2026-06-29 02:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1371, '2026-06-29 06:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1372, '2026-06-29 08:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1373, '2026-06-30 02:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1374, '2026-06-30 06:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1375, '2026-06-30 08:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1376, '2026-07-01 02:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1377, '2026-07-01 06:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1378, '2026-07-01 08:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1379, '2026-07-02 02:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1380, '2026-07-02 06:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1381, '2026-07-02 08:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1382, '2026-07-03 02:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1383, '2026-07-03 06:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1384, '2026-07-03 08:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1385, '2026-07-04 02:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1386, '2026-07-04 06:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1387, '2026-07-04 08:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1388, '2026-07-06 02:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1389, '2026-07-06 06:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1390, '2026-07-06 08:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1391, '2026-07-07 02:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1392, '2026-07-07 06:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1393, '2026-07-07 08:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1394, '2026-07-08 02:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1395, '2026-07-08 06:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1396, '2026-07-08 08:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1397, '2026-07-09 02:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1398, '2026-07-09 06:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1399, '2026-07-09 08:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1400, '2026-07-10 02:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1401, '2026-07-10 06:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1402, '2026-07-10 08:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1403, '2026-07-11 02:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1404, '2026-07-11 06:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1405, '2026-07-11 08:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1406, '2026-07-13 02:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1407, '2026-07-13 06:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1408, '2026-07-13 08:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1409, '2026-07-14 02:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1410, '2026-07-14 06:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1411, '2026-07-14 08:00:00', 'maintenance', 1, 1, '2026-06-13 20:39:28'),
(1412, '2026-06-14 03:40:01', 'repair', 1, 0, '2026-06-13 20:39:28'),
(1413, '2026-06-15 06:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1414, '2026-06-15 08:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1415, '2026-06-14 03:55:53', 'repair', 1, 0, '2026-06-13 20:39:28'),
(1416, '2026-06-16 06:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1417, '2026-06-16 08:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1418, '2026-06-17 02:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1419, '2026-06-17 06:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1420, '2026-06-17 08:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1421, '2026-06-18 02:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1422, '2026-06-18 06:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1423, '2026-06-18 08:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1424, '2026-06-19 02:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1425, '2026-06-19 06:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1426, '2026-06-19 08:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1427, '2026-06-20 02:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1428, '2026-06-20 06:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1429, '2026-06-20 08:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1430, '2026-06-22 02:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1431, '2026-06-22 06:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1432, '2026-06-22 08:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1433, '2026-06-23 02:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1434, '2026-06-23 06:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1435, '2026-06-23 08:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1436, '2026-06-24 02:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1437, '2026-06-24 06:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1438, '2026-06-24 08:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1439, '2026-06-25 02:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1440, '2026-06-25 06:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1441, '2026-06-25 08:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1442, '2026-06-26 02:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1443, '2026-06-26 06:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1444, '2026-06-26 08:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1445, '2026-06-27 02:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1446, '2026-06-27 06:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1447, '2026-06-27 08:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1448, '2026-06-29 02:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1449, '2026-06-29 06:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1450, '2026-06-29 08:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1451, '2026-06-30 02:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1452, '2026-06-30 06:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1453, '2026-06-30 08:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1454, '2026-07-01 02:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1455, '2026-07-01 06:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1456, '2026-07-01 08:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1457, '2026-07-02 02:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1458, '2026-07-02 06:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1459, '2026-07-02 08:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1460, '2026-07-03 02:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1461, '2026-07-03 06:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1462, '2026-07-03 08:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1463, '2026-07-04 02:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1464, '2026-07-04 06:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1465, '2026-07-04 08:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1466, '2026-07-06 02:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1467, '2026-07-06 06:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1468, '2026-07-06 08:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1469, '2026-07-07 02:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1470, '2026-07-07 06:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1471, '2026-07-07 08:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1472, '2026-07-08 02:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1473, '2026-07-08 06:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1474, '2026-07-08 08:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1475, '2026-07-09 02:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1476, '2026-07-09 06:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1477, '2026-07-09 08:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1478, '2026-07-10 02:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1479, '2026-07-10 06:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1480, '2026-07-10 08:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1481, '2026-07-11 02:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1482, '2026-07-11 06:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1483, '2026-07-11 08:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1484, '2026-07-13 02:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1485, '2026-07-13 06:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1486, '2026-07-13 08:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1487, '2026-07-14 02:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1488, '2026-07-14 06:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1489, '2026-07-14 08:00:00', 'repair', 1, 1, '2026-06-13 20:39:28'),
(1490, '2026-06-15 02:00:00', 'test_drive', 3, 1, '2026-06-14 02:04:50'),
(1491, '2026-06-15 06:00:00', 'test_drive', 3, 1, '2026-06-14 02:04:50'),
(1492, '2026-06-16 02:00:00', 'test_drive', 3, 1, '2026-06-14 02:04:50'),
(1493, '2026-06-16 06:00:00', 'test_drive', 3, 1, '2026-06-14 02:04:50'),
(1494, '2026-06-17 02:00:00', 'test_drive', 3, 1, '2026-06-14 02:04:50'),
(1495, '2026-06-17 06:00:00', 'test_drive', 3, 1, '2026-06-14 02:04:50'),
(1496, '2026-06-18 02:00:00', 'test_drive', 3, 1, '2026-06-14 02:04:50'),
(1497, '2026-06-18 06:00:00', 'test_drive', 3, 1, '2026-06-14 02:04:50'),
(1498, '2026-06-20 02:00:00', 'test_drive', 3, 1, '2026-06-14 02:04:50'),
(1499, '2026-06-20 06:00:00', 'test_drive', 3, 1, '2026-06-14 02:04:50'),
(1500, '2026-06-14 04:05:14', 'maintenance', 1, 0, '2026-06-14 03:39:06'),
(1501, '2026-06-14 03:58:03', 'repair', 1, 0, '2026-06-14 03:55:45'),
(1502, '2026-06-16 02:00:00', 'repair', 1, 1, '2026-06-14 03:58:03'),
(1503, '2026-06-15 02:00:00', 'repair', 1, 1, '2026-06-14 04:02:37'),
(1504, '2026-06-16 02:00:00', 'maintenance', 1, 1, '2026-06-14 04:05:14'),
(1505, '2026-06-15 06:00:00', 'maintenance', 1, 1, '2026-06-14 04:17:57'),
(1506, '2026-07-15 02:00:00', 'maintenance', 1, 1, '2026-06-14 20:24:23'),
(1507, '2026-07-15 06:00:00', 'maintenance', 1, 1, '2026-06-14 20:24:23'),
(1508, '2026-07-15 08:00:00', 'maintenance', 1, 1, '2026-06-14 20:24:23');

-- --------------------------------------------------------

--
-- Table structure for table `suppliers`
--

CREATE TABLE `suppliers` (
  `supplier_id` int(11) NOT NULL,
  `company_name` varchar(150) NOT NULL,
  `contact_name` varchar(100) DEFAULT NULL,
  `contact_email` varchar(100) DEFAULT NULL,
  `contact_phone` varchar(20) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `suppliers`
--

INSERT INTO `suppliers` (`supplier_id`, `company_name`, `contact_name`, `contact_email`, `contact_phone`, `address`, `is_active`, `created_at`) VALUES
(1, 'Toyota Motors PH', 'Ramon Castillo', 'rcastillo@toyota.ph', '02-88001234', 'Santa Rosa, Laguna', 1, '2026-04-19 08:40:18'),
(2, 'Honda Cars PH', 'Liza Villanueva', 'lvillanueva@honda.ph', '02-88005678', 'Pasig City, Metro Manila', 1, '2026-04-19 08:40:18'),
(3, 'Hyundai Asia Resources', 'Kevin Ong', 'kong@hyundai.ph', '02-88009012', 'Mandaluyong, Metro Manila', 1, '2026-04-19 08:40:18'),
(4, 'BYD', NULL, NULL, NULL, NULL, 1, '2026-06-07 03:58:19'),
(6, 'Mitsubishi Motors Philippines', 'Mitsubishi', 'mitsubishi@gmail.com', '12345678901', 'Sample Address', 1, '2026-06-14 15:57:01'),
(7, 'Isuzu Philippines Corporation', 'Ricardo Valentino', 'rickyvalentino@gmail.com', '(+63) 9225553247', 'Cainta, Rizal', 1, '2026-06-14 18:21:13');

-- --------------------------------------------------------

--
-- Table structure for table `supplies`
--

CREATE TABLE `supplies` (
  `supply_id` int(11) NOT NULL,
  `supplier_id` int(11) NOT NULL,
  `part_name` varchar(150) NOT NULL,
  `part_number` varchar(50) NOT NULL,
  `unit_cost` decimal(10,2) NOT NULL,
  `stock_qty` int(11) NOT NULL DEFAULT 0,
  `reorder_level` int(11) NOT NULL DEFAULT 10,
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `supplies`
--

INSERT INTO `supplies` (`supply_id`, `supplier_id`, `part_name`, `part_number`, `unit_cost`, `stock_qty`, `reorder_level`, `updated_at`) VALUES
(2, 1, 'Genuine Toyota Engine Oil 5W-30 (1L)', 'TOY-5W30-01', 450.00, 120, 30, '2026-06-14 20:27:37'),
(3, 6, 'Mitsubishi Mirage Oil Filter', 'MIT-1230A182', 380.00, 80, 20, '2026-06-14 20:28:01'),
(4, 6, 'Mitsubishi Mirage Front Brake Pads Set', 'MIT-MZ690348', 1850.00, 40, 12, '2026-06-14 20:28:22'),
(5, 7, 'Isuzu D-Max Fuel Filter Element', 'ISU-8981430410', 1450.00, 35, 10, '2026-06-14 20:28:41'),
(6, 1, 'Genuine Toyota Premium Coolant (1L)', 'TOY-08889-80015', 320.00, 90, 25, '2026-06-14 20:29:05'),
(7, 6, 'Mitsubishi Montero Sport Air Filter', 'MIT-1500A608', 950.00, 45, 15, '2026-06-14 20:30:28'),
(8, 1, 'Toyota Vios Front Brake Pads Set', 'TOY-4465-YZZR7', 2200.00, 50, 15, '2026-06-14 20:30:47'),
(9, 7, 'Isuzu mu-X Cabin Air Filter', 'ISU-8981394280', 680.00, 60, 15, '2026-06-14 20:31:13'),
(10, 7, 'Isuzu L300 Clutch Disc', 'ISU-8941566410', 3400.00, 15, 5, '2026-06-14 20:31:30'),
(11, 1, 'Toyota Innova ATF WS Fluid (4L)', 'TOY-08886-02305', 2400.00, 18, 5, '2026-06-14 20:32:11'),
(12, 6, 'Mitsubishi Xpander Engine Air Filter', 'MIT-1500A687', 780.00, 40, 12, '2026-06-14 20:34:43'),
(13, 7, 'Isuzu D-Max Front Shock Absorber', 'ISU-8981926610', 3800.00, 16, 5, '2026-06-14 20:34:43'),
(14, 6, 'Mitsubishi Adventure Fuel Filter', 'MIT-MB220900', 550.00, 55, 15, '2026-06-14 20:34:43'),
(15, 6, 'Mitsubishi Lancer Spark Plug Set (4pcs)', 'MIT-MS851358', 880.00, 30, 10, '2026-06-14 20:34:43'),
(16, 7, 'Isuzu mu-X Rear Brake Pads Set', 'ISU-8982464190', 2100.00, 22, 6, '2026-06-14 20:34:43'),
(17, 7, 'Isuzu Travis Oil Filter', 'ISU-5876100110', 420.00, 100, 25, '2026-06-14 20:34:43'),
(18, 6, 'Mitsubishi Triton Cabin Air Filter', 'MIT-7803A112', 720.00, 48, 12, '2026-06-14 20:34:43'),
(19, 6, 'Mitsubishi Mirage Serpentine Belt', 'MIT-1340A193', 890.00, 32, 8, '2026-06-14 20:34:43'),
(20, 1, 'Toyota Fortuner Front Disc Rotor (Pair)', 'TOY-43512-0K090', 5800.00, 10, 4, '2026-06-14 20:34:43'),
(21, 7, 'Isuzu D-Max Wiper Blade Set (Pair)', 'ISU-8982542210', 950.00, 40, 10, '2026-06-14 20:34:43'),
(22, 1, 'Toyota Avanza Engine Air Filter', 'TOY-17801-BZ150', 620.00, 50, 15, '2026-06-14 20:34:43'),
(23, 6, 'Mitsubishi Strada Front Bumper Clip Set', 'MIT-MU000573', 350.00, 200, 50, '2026-06-14 20:34:43');

-- --------------------------------------------------------

--
-- Table structure for table `system_settings`
--

CREATE TABLE `system_settings` (
  `setting_id` int(11) NOT NULL,
  `setting_key` varchar(100) NOT NULL,
  `setting_value` text NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `updated_by` int(11) DEFAULT NULL,
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `system_settings`
--

INSERT INTO `system_settings` (`setting_id`, `setting_key`, `setting_value`, `description`, `updated_by`, `updated_at`) VALUES
(1, 'default_commission_rate', '3.5', 'Default agent commission rate in percent', 6, '2026-06-06 12:39:40'),
(2, 'chatbot_enabled', '1', 'Toggle AI chatbot on/off', 6, '2026-06-14 17:59:57'),
(3, 'max_loan_term_months', '60', 'Maximum allowed loan term in months', 1, '2026-04-19 08:40:18');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `hashed_password` varchar(255) NOT NULL,
  `email` varchar(100) NOT NULL,
  `role` enum('admin','agent','customer','finance_staff','service_advisor') NOT NULL,
  `email_verified` tinyint(1) NOT NULL DEFAULT 0,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `last_login` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `must_reset_password` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `username`, `hashed_password`, `email`, `role`, `email_verified`, `is_active`, `last_login`, `created_at`, `must_reset_password`) VALUES
(1, 'admin_jose', '$2b$12$mockhashadmin001', 'jose.admin@automatik.ph', 'admin', 1, 1, NULL, '2026-04-19 08:40:18', 0),
(2, 'agent_miguel', 'scrypt:32768:8:1$nqpzKGkeh2xNe4Y5$4fd26f44d4442c5a2e97d14df37a8a090be16314b768bcf9b50cea631d939ecc7e910d02559c6d2515d6a8e36aae4075b9f93babee5cac8babf793b46f2ec30c', 'miguel.reyes@automatik.ph', 'agent', 1, 1, '2026-06-10 00:52:56', '2026-04-19 08:40:18', 0),
(3, 'agent_anna', '$2b$12$mockhashagent002', 'anna.santos@automatik.ph', 'agent', 1, 1, NULL, '2026-04-19 08:40:18', 0),
(4, 'cust_pedro', '$2b$12$mockhashcust001', 'pedro.garcia@gmail.com', 'customer', 1, 1, NULL, '2026-04-19 08:40:18', 0),
(5, 'cust_maria', '$2b$12$mockhashcust002', 'maria.dela.cruz@gmail.com', 'customer', 1, 1, NULL, '2026-04-19 08:40:18', 0),
(6, 'admin', 'scrypt:32768:8:1$nXqPc1y7Nvwgw9p3$42eeba3f312feb2b1c8f2df8697a891307286f9a62788467d3a47676c7ffcc5646d614c04f55ca44338f321e3b7c1b47fd8982c177a243ba4699895ccf9f97a2', 'admin@gmail.com', 'admin', 1, 1, '2026-06-15 03:08:34', '2026-05-20 03:39:23', 0),
(29, 'Gianna@22', 'scrypt:32768:8:1$BkWX6slOlHiO8aJ0$e541be3a6bc2c0355f0fa551843e94293e0f45e29c5559452b82f00ab4a4caf9138820b0aa2a62245ef975a335e0ff55fd573ad5614c9308e0751a133b688b58', 'giannaizabelle14@gmail.com', 'agent', 0, 1, NULL, '2026-05-20 17:31:59', 0),
(30, 'gianna252', 'scrypt:32768:8:1$4cI1giXl3fNBxW9s$13e5dc249cc53a2c7a7cafc406725a323dc75b0435ad4cddfc9f7939de3c82517b0fcaf9a9b9f32cc4b87910efe6e14281a9795bb75449ff2e03b789a1e6e0da', 'lancegomoa@gmail.com', 'agent', 1, 1, '2026-06-15 02:47:06', '2026-05-21 14:55:27', 0),
(31, 'CUST-test', 'scrypt:32768:8:1$dyhPTqMQfJlUKHEj$5114377b7642892450dfa6f7a429228857eb42d2371c8dccdb040cd1011751d9c6c2f97b90c417b673fc9e1a097467ba9907b2eebc1ff10c209df938ddb15789', 'test@example.com', 'customer', 0, 1, NULL, '2026-05-25 18:39:48', 0),
(33, 'agent1', 'scrypt:32768:8:1$mvKUxcBalVhLL0rM$2a807e4e3d748a500c87f0030616d0c5fe5bfc3a0bd57c51a5134fc354a14a0f210db5ec837b1ef3bf3af780c5097901a43a2457d137195bc6ea14c08fe35871', 'agent1@example.com', 'agent', 0, 1, NULL, '2026-05-25 18:41:26', 0),
(34, 'cust_juan', 'scrypt:32768:8:1$XJXGJKB51UK4PCPx$52c93db88bb15af1326dc508d8ca0af982a82087148b5cd061da31d95e8a5f30ea150680679ea46b80a0658d0bbf8c20e446b4f78b3aed1b5d4abf322abfc2ca', 'juan.luna@email.com', 'customer', 1, 1, NULL, '2026-06-03 15:49:24', 0),
(35, 'cust_luisa', 'scrypt:32768:8:1$XJXGJKB51UK4PCPx$52c93db88bb15af1326dc508d8ca0af982a82087148b5cd061da31d95e8a5f30ea150680679ea46b80a0658d0bbf8c20e446b4f78b3aed1b5d4abf322abfc2ca', 'luisa.mercado@email.com', 'customer', 1, 1, NULL, '2026-06-03 15:49:24', 0),
(36, 'cust_carlos', 'scrypt:32768:8:1$XJXGJKB51UK4PCPx$52c93db88bb15af1326dc508d8ca0af982a82087148b5cd061da31d95e8a5f30ea150680679ea46b80a0658d0bbf8c20e446b4f78b3aed1b5d4abf322abfc2ca', 'carlos.reyes@email.com', 'customer', 1, 1, NULL, '2026-06-03 15:49:24', 0),
(37, 'cust_angela', 'scrypt:32768:8:1$XJXGJKB51UK4PCPx$52c93db88bb15af1326dc508d8ca0af982a82087148b5cd061da31d95e8a5f30ea150680679ea46b80a0658d0bbf8c20e446b4f78b3aed1b5d4abf322abfc2ca', 'angela.v@email.com', 'customer', 1, 1, '2026-06-10 05:14:12', '2026-06-03 15:49:24', 0),
(46, 'CUST-tanjirokamad-1894', 'scrypt:32768:8:1$1zqgTCgOeiYwVgiN$55e80a898e8af199bae3b2f9fa9631f4b968795e7e98634f7384c000c8175c6627aa819eb2266a209af7194f1e8df9943f28afbdf28642068822dc40ab97c68f', 'tanjirokamado22222@gmail.com', 'customer', 1, 1, '2026-06-14 19:20:23', '2026-06-05 10:14:05', 0),
(48, 'finance_staff1', 'scrypt:32768:8:1$NNlwjVpq9pSqzz7A$de47ab6719bba4996237e6fcd40997883ab55af87c44ebe5b78883220412a56d7493fbd23ecc67345ac9300a12b1f75fdd7640c20927d48678079f608af40a31', 'finance@automatik.com', 'finance_staff', 1, 1, '2026-06-15 03:12:13', '2026-06-10 04:53:07', 0),
(49, 'advisor1', 'scrypt:32768:8:1$s9mnWfl9hKX6v0ji$bc47436a328793ce2b88a358d7b108a537d7a66d2b1a74101c0b2be81dc8ca8b69bc1b21adf1fcc4d879b7bda9fba6ad6a112d81f9a25562ba7c39cc14cac704', 'advisor@automatik.com', 'service_advisor', 1, 1, '2026-06-15 02:47:39', '2026-06-10 04:53:07', 0),
(50, 'izabelle', 'scrypt:32768:8:1$KDu8VRvPq0dNd97C$981a547a91a5322e2113c4ff0c92b9cc54907aa09633301702d7a7ce69165171477172429d814882abf850a20c8411a05b4dd8b3c61543b6a9b304c186efeab2', 'izabellegianna@gmail.com', 'agent', 0, 1, NULL, '2026-06-13 18:05:02', 0),
(51, 'CUST-giannaizabel-3886', 'scrypt:32768:8:1$qzRy1OuIbvPKzd05$6a31592aa66333b20cb4a7137c71fa1efa62d44fe01acf32a544f3c1edf1a356c7423ead02bdf416dc1cf3e4f72f1758c980ae7b4e0a2beb8b6cb09de9186e43', 'lancekit223@gmail.com', 'customer', 1, 1, NULL, '2026-06-14 09:38:50', 0),
(54, 'LanceKitt', 'scrypt:32768:8:1$Sxc7WzAWjGQ9vWUr$76795e686bcf22b69eb055a1b87a76b7db323e3a7461aa7faf5fadc3dbebee38b821af51753fd8c3c005d6734776eff2006b5adb8a767ca18b1f23074e6ee71b', 'lance.gomos222@gmail.com', 'customer', 0, 1, NULL, '2026-06-15 03:02:51', 1);

-- --------------------------------------------------------

--
-- Table structure for table `user_profile`
--

CREATE TABLE `user_profile` (
  `user_id` int(11) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `province` varchar(100) DEFAULT NULL,
  `zip_code` varchar(10) DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  `gender` enum('male','female','prefer_not_to_say') DEFAULT NULL,
  `profile_picture_url` varchar(500) DEFAULT NULL,
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `user_profile`
--

INSERT INTO `user_profile` (`user_id`, `full_name`, `phone_number`, `address`, `city`, `province`, `zip_code`, `date_of_birth`, `gender`, `profile_picture_url`, `updated_at`) VALUES
(1, 'Jose Ramirez', '09171234567', '123 Rizal St', 'Manila', 'Metro Manila', '1000', NULL, 'male', NULL, '2026-04-19 08:40:18'),
(2, 'Miguel Reyes', '09181234568', '456 Mabini Ave', 'Quezon City', 'Metro Manila', '1100', NULL, 'male', NULL, '2026-04-19 08:40:18'),
(3, 'Anna Santos', '09191234569', '789 Luna Blvd', 'Makati', 'Metro Manila', '1200', NULL, 'female', NULL, '2026-04-19 08:40:18'),
(4, 'Pedro Garcia', '09201234570', '12 Sampaguita St', 'Pasig', 'Metro Manila', '1600', NULL, 'male', NULL, '2026-04-19 08:40:18'),
(5, 'Maria Dela Cruz', '09211234571', '34 Rosal Ave', 'Marikina', 'Metro Manila', '1800', NULL, 'female', NULL, '2026-04-19 08:40:18'),
(29, 'Gianna Izabelle Cantillo', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2026-05-20 17:31:59'),
(30, 'Gianna Izabelle Cantillo', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2026-05-21 14:55:27'),
(33, 'Test Agent', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2026-05-25 18:41:26'),
(34, 'Juan Luna', '09171230001', '42 P. Burgos St', 'Manila', 'Metro Manila', '1000', NULL, NULL, NULL, '2026-06-03 15:49:24'),
(35, 'Luisa Mercado', '09181230002', '88 Scout Rallos St', 'Quezon City', 'Metro Manila', '1103', NULL, NULL, NULL, '2026-06-03 15:49:24'),
(36, 'Carlos Reyes', '09191230003', '15 F. Calderon St', 'Mandaluyong', 'Metro Manila', '1550', NULL, NULL, NULL, '2026-06-03 15:49:24'),
(37, 'Angela Villanueva', '09201230004', '7 Manga Ave', 'Pasig', 'Metro Manila', '1600', NULL, NULL, NULL, '2026-06-03 15:49:24'),
(46, 'Lance Kit Gom-os', '09776913684', '', NULL, NULL, NULL, NULL, NULL, NULL, '2026-06-14 04:32:49'),
(48, 'Finance Staff One', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2026-06-10 04:53:07'),
(49, 'Service Advisor One', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2026-06-10 04:53:07'),
(50, 'Gianna Izabelle Cantillo', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2026-06-13 18:05:02'),
(54, 'LanceKit22', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2026-06-15 03:02:51');

-- --------------------------------------------------------

--
-- Table structure for table `vehicles`
--

CREATE TABLE `vehicles` (
  `vehicle_id` int(11) NOT NULL,
  `supplier_id` int(11) NOT NULL,
  `vin` varchar(17) NOT NULL,
  `brand` varchar(50) NOT NULL,
  `model` varchar(100) NOT NULL,
  `year` smallint(6) NOT NULL,
  `color` varchar(50) DEFAULT NULL,
  `body_type` varchar(20) DEFAULT NULL,
  `seating_capacity` int(11) DEFAULT NULL,
  `transmission` enum('manual','automatic') DEFAULT NULL,
  `fuel_type` enum('gasoline','diesel','electric','hybrid') DEFAULT NULL,
  `price` decimal(12,2) NOT NULL,
  `status` enum('available','reserved','discontinued','delivered') NOT NULL DEFAULT 'available',
  `specs_json` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`specs_json`)),
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `vehicles`
--

INSERT INTO `vehicles` (`vehicle_id`, `supplier_id`, `vin`, `brand`, `model`, `year`, `color`, `body_type`, `seating_capacity`, `transmission`, `fuel_type`, `price`, `status`, `specs_json`, `created_at`) VALUES
(1, 1, '1HGBH41JXMN109186', 'Toyota', 'Fortuner GR Sport', 2025, 'Phantom Brown', 'SUV', 7, 'automatic', 'diesel', 2390000.00, 'delivered', NULL, '2026-04-19 08:40:18'),
(2, 1, '1HGBH41JXMN109187', 'Toyota', 'testing', 2025, 'Pearl White', 'Sedan', 5, 'automatic', 'gasoline', 798000.00, 'delivered', NULL, '2026-04-19 08:40:18'),
(3, 2, '2HGFB2F59DH519681', 'Honda', 'CR-V RS Turbo', 2024, 'Sonic Gray', 'SUV', 5, 'automatic', 'gasoline', 1899000.00, 'delivered', NULL, '2026-04-19 08:40:18'),
(4, 3, '5NPE34AF8FH002518', 'Hyundai', 'Tucson HTRAC', 2025, 'Abyss Black', 'SUV', 5, 'automatic', 'gasoline', 1648000.00, 'delivered', NULL, '2026-04-19 08:40:18'),
(5, 2, '2HGFB2F59DH519682', 'Honda', 'Civic RS Turbo', 2024, 'Rallye Red', 'Sedan', 5, 'manual', 'gasoline', 1249000.00, 'discontinued', 'null', '2026-04-19 08:40:18'),
(9, 2, '2HGFB2F59DH519684', 'Honda', 'SADASD', 2025, NULL, 'sedan', 4, 'manual', 'gasoline', 20000000.00, 'discontinued', 'null', '2026-06-07 03:42:56'),
(11, 4, '121asdasdasd', 'BYD', 'SEALION', 2026, 'SILVER GRAY', 'sedan', 4, 'manual', 'gasoline', 2000000.00, 'discontinued', '{\n\"hello\": \"testing\"\n\n}', '2026-06-10 01:59:16'),
(12, 1, 'JT2BG22K5P1234567', 'Toyota', 'Vios 1.3 XLE M/T', 2023, 'Black', 'sedan', 5, 'automatic', 'gasoline', 868000.00, 'available', '{\n  \"overall_dimensions_mm\": {\n    \"length\": 4425,\n    \"width\": 1730,\n    \"height\": 1475\n  },\n  \"wheelbase_mm\": 2550,\n  \"seating_capacity\": 5,\n  \"engine\": {\n    \"type\": \"Dual VVT-i, 4-Cylinder In-Line DOHC 16V EFI\",\n    \"displacement_cc\": 1329,\n    \"maximum_output\": {\n      \"power_ps\": 99,\n      \"rpm\": 6000\n    },\n    \"maximum_torque\": {\n      \"torque_nm\": 123,\n      \"rpm\": 4200\n    }\n  },\n  \"fuel_capacity_l\": 42,\n  \"power_transmission\": \"CVT\",\n  \"brakes\": {\n    \"front\": \"Ventilated Discs\",\n    \"rear\": \"Drum\"\n  },\n  \"tires\": \"185/60 R15\",\n  \"wheels\": {\n    \"size_inches\": 15,\n    \"material\": \"Alloy\"\n  }\n}', '2026-06-14 15:19:15'),
(13, 6, 'MMTFA3CD8NH765432', 'Mitsubishi', 'Montero Sport 4WD 8AT', 2022, 'White', 'suv', 7, 'automatic', 'diesel', 735000.00, 'available', 'null', '2026-06-14 15:58:28'),
(14, 1, 'MNBAXXMA4RJ112233', 'Toyota', 'Ativ 1.5 HEV CVT	', 2022, 'White	', 'sedan', 5, 'automatic', 'gasoline', 1208000.00, 'available', 'null', '2026-06-14 18:19:18'),
(15, 7, 'MPATFS87JMT998877', 'Isuzu', 'F-Series FRR90MS	', 2023, 'White	', 'pickup', 6, 'automatic', 'gasoline', 4500000.00, 'available', 'null', '2026-06-14 18:22:22'),
(16, 1, 'JTEBR3FJ2SK445566', 'Toyota', 'Wigo G CVT', 2023, 'Grey', 'hatchback', 5, 'automatic', 'gasoline', 735000.00, 'available', 'null', '2026-06-14 18:25:04'),
(17, 6, 'ML32AUHJ7PH334455', 'Mitsubishi', 'Xpander GLS A/T	', 2022, 'Grey	', 'other', 7, 'automatic', 'gasoline', 1099000.00, 'reserved', 'null', '2026-06-14 18:41:20'),
(18, 1, 'MMTHE4PU3RH654987', 'Toyota', 'Camry 2.5 V HEV CVT	', 2022, 'Black	', 'sedan', 5, 'automatic', 'gasoline', 2677000.00, 'available', 'null', '2026-06-14 18:43:16'),
(19, 6, 'MK2XR63F2RH998811', 'Mitsubishi', 'Mirage GLX CVT	', 2022, 'Red	', 'hatchback', 5, 'automatic', 'gasoline', 711000.00, 'available', 'null', '2026-06-14 18:49:58'),
(20, 1, 'ML32F3FJ6NH123789', 'Toyota', 'Alphard 2.5 HEV CVT	', 2025, 'White', 'other', 7, 'manual', 'gasoline', 4691000.00, 'available', 'null', '2026-06-15 02:50:13');

-- --------------------------------------------------------

--
-- Table structure for table `vehicle_photos`
--

CREATE TABLE `vehicle_photos` (
  `photo_id` int(11) NOT NULL,
  `vehicle_id` int(11) NOT NULL,
  `photo_url` varchar(500) NOT NULL,
  `sort_order` int(11) NOT NULL DEFAULT 0,
  `uploaded_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `vehicle_photos`
--

INSERT INTO `vehicle_photos` (`photo_id`, `vehicle_id`, `photo_url`, `sort_order`, `uploaded_at`) VALUES
(9, 12, '/static/uploads/vehicles/1781450355_TOYOTA_BLACK.jpg', 1, '2026-06-14 15:19:15'),
(10, 13, '/static/uploads/vehicles/1781452745_MONTERO.jpg', 1, '2026-06-14 15:59:05'),
(11, 14, '/static/uploads/vehicles/1781461158_ATIV.webp', 1, '2026-06-14 18:19:18'),
(12, 15, '/static/uploads/vehicles/1781461596_isuzu-f-series-2018-brand-new-5aae0dfdd277b.jpg', 1, '2026-06-14 18:26:36'),
(13, 16, '/static/uploads/vehicles/1781462330_WIGO.jpg', 1, '2026-06-14 18:38:50'),
(14, 17, '/static/uploads/vehicles/1781462480_XPANDER.webp', 1, '2026-06-14 18:41:20'),
(15, 18, '/static/uploads/vehicles/1781462659_camry.jpg', 1, '2026-06-14 18:44:19'),
(16, 19, '/static/uploads/vehicles/1781463028_mirage.jpg', 1, '2026-06-14 18:50:28'),
(17, 20, '/static/uploads/vehicles/1781491850_toyota.com_.ph404alphard-3.jpg', 1, '2026-06-15 02:50:50');

-- --------------------------------------------------------

--
-- Table structure for table `warranty_claims`
--

CREATE TABLE `warranty_claims` (
  `claim_id` int(11) NOT NULL,
  `sale_id` int(11) NOT NULL,
  `vehicle_id` int(11) NOT NULL,
  `claim_type` enum('repair','replacement','refund') NOT NULL,
  `description` text NOT NULL,
  `status` enum('submitted','under_review','approved','rejected','resolved') NOT NULL DEFAULT 'submitted',
  `reviewed_by` int(11) DEFAULT NULL,
  `resolution` text DEFAULT NULL,
  `submitted_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `resolved_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `warranty_claims`
--

INSERT INTO `warranty_claims` (`claim_id`, `sale_id`, `vehicle_id`, `claim_type`, `description`, `status`, `reviewed_by`, `resolution`, `submitted_at`, `resolved_at`) VALUES
(1, 1, 4, 'repair', 'Air conditioning unit not cooling properly after 2 months of use.', 'resolved', 1, NULL, '2025-05-12 01:00:00', '2026-06-14 07:00:06'),
(2, 3, 1, 'repair', 'The engine check light has been intermittent since the second week of ownership. Dealership inspection suggested a possible sensor issue. Requesting warranty repair.', 'resolved', 49, NULL, '2026-06-03 15:49:24', '2026-06-13 16:33:02'),
(3, 24, 1, 'repair', 'asdasd', 'resolved', 6, NULL, '2026-06-14 03:20:17', '2026-06-14 08:36:34'),
(4, 24, 1, 'repair', 'qweqweqwe', 'resolved', 49, NULL, '2026-06-14 03:23:09', '2026-06-14 07:00:05');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `access_tokens`
--
ALTER TABLE `access_tokens`
  ADD PRIMARY KEY (`token_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `agent_commissions`
--
ALTER TABLE `agent_commissions`
  ADD PRIMARY KEY (`commission_id`),
  ADD KEY `sale_id` (`sale_id`),
  ADD KEY `agent_id` (`agent_id`);

--
-- Indexes for table `agent_details`
--
ALTER TABLE `agent_details`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `employee_number` (`employee_number`);

--
-- Indexes for table `agent_tasks`
--
ALTER TABLE `agent_tasks`
  ADD PRIMARY KEY (`task_id`),
  ADD KEY `agent_id` (`agent_id`),
  ADD KEY `inquiry_id` (`inquiry_id`);

--
-- Indexes for table `amortization_schedule`
--
ALTER TABLE `amortization_schedule`
  ADD PRIMARY KEY (`schedule_id`),
  ADD UNIQUE KEY `uq_loan_month` (`loan_id`,`month_number`);

--
-- Indexes for table `audit_logs`
--
ALTER TABLE `audit_logs`
  ADD PRIMARY KEY (`log_id`);

--
-- Indexes for table `chatbot_logs`
--
ALTER TABLE `chatbot_logs`
  ADD PRIMARY KEY (`log_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `inquiry_id` (`inquiry_id`);

--
-- Indexes for table `customer_details`
--
ALTER TABLE `customer_details`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `customer_number` (`customer_number`);

--
-- Indexes for table `documents`
--
ALTER TABLE `documents`
  ADD PRIMARY KEY (`document_id`),
  ADD KEY `sale_id` (`sale_id`);

--
-- Indexes for table `inquiries`
--
ALTER TABLE `inquiries`
  ADD PRIMARY KEY (`inquiry_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `agent_id` (`agent_id`),
  ADD KEY `vehicle_id` (`vehicle_id`);

--
-- Indexes for table `insurance_records`
--
ALTER TABLE `insurance_records`
  ADD PRIMARY KEY (`insurance_id`),
  ADD UNIQUE KEY `policy_number` (`policy_number`),
  ADD KEY `vehicle_id` (`vehicle_id`),
  ADD KEY `sale_id` (`sale_id`),
  ADD KEY `customer_id` (`customer_id`);

--
-- Indexes for table `loan_details`
--
ALTER TABLE `loan_details`
  ADD PRIMARY KEY (`loan_id`),
  ADD UNIQUE KEY `sale_id` (`sale_id`);

--
-- Indexes for table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`notification_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `payments`
--
ALTER TABLE `payments`
  ADD PRIMARY KEY (`payment_id`),
  ADD KEY `sale_id` (`sale_id`),
  ADD KEY `schedule_id` (`schedule_id`),
  ADD KEY `recorded_by` (`recorded_by`);

--
-- Indexes for table `sales`
--
ALTER TABLE `sales`
  ADD PRIMARY KEY (`sale_id`),
  ADD KEY `vehicle_id` (`vehicle_id`),
  ADD KEY `customer_id` (`customer_id`),
  ADD KEY `agent_id` (`agent_id`),
  ADD KEY `inquiry_id` (`inquiry_id`);

--
-- Indexes for table `sales_contracts`
--
ALTER TABLE `sales_contracts`
  ADD PRIMARY KEY (`contract_id`),
  ADD KEY `sale_id` (`sale_id`),
  ADD KEY `reviewed_by` (`reviewed_by`);

--
-- Indexes for table `service_bookings`
--
ALTER TABLE `service_bookings`
  ADD PRIMARY KEY (`booking_id`),
  ADD KEY `customer_id` (`customer_id`),
  ADD KEY `vehicle_id` (`vehicle_id`),
  ADD KEY `slot_id` (`slot_id`),
  ADD KEY `warranty_claim_id` (`warranty_claim_id`),
  ADD KEY `assigned_to` (`assigned_to`);

--
-- Indexes for table `service_slots`
--
ALTER TABLE `service_slots`
  ADD PRIMARY KEY (`slot_id`);

--
-- Indexes for table `suppliers`
--
ALTER TABLE `suppliers`
  ADD PRIMARY KEY (`supplier_id`);

--
-- Indexes for table `supplies`
--
ALTER TABLE `supplies`
  ADD PRIMARY KEY (`supply_id`),
  ADD UNIQUE KEY `part_number` (`part_number`),
  ADD KEY `supplier_id` (`supplier_id`);

--
-- Indexes for table `system_settings`
--
ALTER TABLE `system_settings`
  ADD PRIMARY KEY (`setting_id`),
  ADD UNIQUE KEY `setting_key` (`setting_key`),
  ADD KEY `updated_by` (`updated_by`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `user_profile`
--
ALTER TABLE `user_profile`
  ADD PRIMARY KEY (`user_id`);

--
-- Indexes for table `vehicles`
--
ALTER TABLE `vehicles`
  ADD PRIMARY KEY (`vehicle_id`),
  ADD UNIQUE KEY `vin` (`vin`),
  ADD KEY `supplier_id` (`supplier_id`);

--
-- Indexes for table `vehicle_photos`
--
ALTER TABLE `vehicle_photos`
  ADD PRIMARY KEY (`photo_id`),
  ADD KEY `vehicle_id` (`vehicle_id`);

--
-- Indexes for table `warranty_claims`
--
ALTER TABLE `warranty_claims`
  ADD PRIMARY KEY (`claim_id`),
  ADD KEY `fk_wc_sale` (`sale_id`),
  ADD KEY `fk_wc_vehicle` (`vehicle_id`),
  ADD KEY `fk_wc_admin` (`reviewed_by`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `agent_commissions`
--
ALTER TABLE `agent_commissions`
  MODIFY `commission_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- AUTO_INCREMENT for table `agent_tasks`
--
ALTER TABLE `agent_tasks`
  MODIFY `task_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `amortization_schedule`
--
ALTER TABLE `amortization_schedule`
  MODIFY `schedule_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=636;

--
-- AUTO_INCREMENT for table `audit_logs`
--
ALTER TABLE `audit_logs`
  MODIFY `log_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=217;

--
-- AUTO_INCREMENT for table `chatbot_logs`
--
ALTER TABLE `chatbot_logs`
  MODIFY `log_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `documents`
--
ALTER TABLE `documents`
  MODIFY `document_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- AUTO_INCREMENT for table `inquiries`
--
ALTER TABLE `inquiries`
  MODIFY `inquiry_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=41;

--
-- AUTO_INCREMENT for table `insurance_records`
--
ALTER TABLE `insurance_records`
  MODIFY `insurance_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `loan_details`
--
ALTER TABLE `loan_details`
  MODIFY `loan_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `notification_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=361;

--
-- AUTO_INCREMENT for table `payments`
--
ALTER TABLE `payments`
  MODIFY `payment_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=34;

--
-- AUTO_INCREMENT for table `sales`
--
ALTER TABLE `sales`
  MODIFY `sale_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

--
-- AUTO_INCREMENT for table `sales_contracts`
--
ALTER TABLE `sales_contracts`
  MODIFY `contract_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- AUTO_INCREMENT for table `service_bookings`
--
ALTER TABLE `service_bookings`
  MODIFY `booking_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `service_slots`
--
ALTER TABLE `service_slots`
  MODIFY `slot_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1509;

--
-- AUTO_INCREMENT for table `suppliers`
--
ALTER TABLE `suppliers`
  MODIFY `supplier_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `supplies`
--
ALTER TABLE `supplies`
  MODIFY `supply_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- AUTO_INCREMENT for table `system_settings`
--
ALTER TABLE `system_settings`
  MODIFY `setting_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=55;

--
-- AUTO_INCREMENT for table `vehicles`
--
ALTER TABLE `vehicles`
  MODIFY `vehicle_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT for table `vehicle_photos`
--
ALTER TABLE `vehicle_photos`
  MODIFY `photo_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT for table `warranty_claims`
--
ALTER TABLE `warranty_claims`
  MODIFY `claim_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `access_tokens`
--
ALTER TABLE `access_tokens`
  ADD CONSTRAINT `access_tokens_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `agent_commissions`
--
ALTER TABLE `agent_commissions`
  ADD CONSTRAINT `agent_commissions_ibfk_1` FOREIGN KEY (`sale_id`) REFERENCES `sales` (`sale_id`),
  ADD CONSTRAINT `agent_commissions_ibfk_2` FOREIGN KEY (`agent_id`) REFERENCES `agent_details` (`user_id`);

--
-- Constraints for table `agent_details`
--
ALTER TABLE `agent_details`
  ADD CONSTRAINT `agent_details_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `agent_tasks`
--
ALTER TABLE `agent_tasks`
  ADD CONSTRAINT `agent_tasks_ibfk_1` FOREIGN KEY (`agent_id`) REFERENCES `agent_details` (`user_id`),
  ADD CONSTRAINT `agent_tasks_ibfk_2` FOREIGN KEY (`inquiry_id`) REFERENCES `inquiries` (`inquiry_id`) ON DELETE SET NULL;

--
-- Constraints for table `amortization_schedule`
--
ALTER TABLE `amortization_schedule`
  ADD CONSTRAINT `amortization_schedule_ibfk_1` FOREIGN KEY (`loan_id`) REFERENCES `loan_details` (`loan_id`);

--
-- Constraints for table `chatbot_logs`
--
ALTER TABLE `chatbot_logs`
  ADD CONSTRAINT `chatbot_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL,
  ADD CONSTRAINT `chatbot_logs_ibfk_2` FOREIGN KEY (`inquiry_id`) REFERENCES `inquiries` (`inquiry_id`) ON DELETE SET NULL;

--
-- Constraints for table `customer_details`
--
ALTER TABLE `customer_details`
  ADD CONSTRAINT `customer_details_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `documents`
--
ALTER TABLE `documents`
  ADD CONSTRAINT `documents_ibfk_1` FOREIGN KEY (`sale_id`) REFERENCES `sales` (`sale_id`);

--
-- Constraints for table `inquiries`
--
ALTER TABLE `inquiries`
  ADD CONSTRAINT `inquiries_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL,
  ADD CONSTRAINT `inquiries_ibfk_2` FOREIGN KEY (`agent_id`) REFERENCES `agent_details` (`user_id`) ON DELETE SET NULL,
  ADD CONSTRAINT `inquiries_ibfk_3` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`vehicle_id`);

--
-- Constraints for table `insurance_records`
--
ALTER TABLE `insurance_records`
  ADD CONSTRAINT `insurance_records_ibfk_1` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`vehicle_id`),
  ADD CONSTRAINT `insurance_records_ibfk_2` FOREIGN KEY (`sale_id`) REFERENCES `sales` (`sale_id`),
  ADD CONSTRAINT `insurance_records_ibfk_3` FOREIGN KEY (`customer_id`) REFERENCES `customer_details` (`user_id`) ON DELETE SET NULL;

--
-- Constraints for table `loan_details`
--
ALTER TABLE `loan_details`
  ADD CONSTRAINT `loan_details_ibfk_1` FOREIGN KEY (`sale_id`) REFERENCES `sales` (`sale_id`);

--
-- Constraints for table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `payments`
--
ALTER TABLE `payments`
  ADD CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`sale_id`) REFERENCES `sales` (`sale_id`),
  ADD CONSTRAINT `payments_ibfk_2` FOREIGN KEY (`schedule_id`) REFERENCES `amortization_schedule` (`schedule_id`) ON DELETE SET NULL,
  ADD CONSTRAINT `payments_ibfk_3` FOREIGN KEY (`recorded_by`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `sales`
--
ALTER TABLE `sales`
  ADD CONSTRAINT `sales_ibfk_1` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`vehicle_id`),
  ADD CONSTRAINT `sales_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `customer_details` (`user_id`) ON DELETE SET NULL,
  ADD CONSTRAINT `sales_ibfk_3` FOREIGN KEY (`agent_id`) REFERENCES `agent_details` (`user_id`),
  ADD CONSTRAINT `sales_ibfk_4` FOREIGN KEY (`inquiry_id`) REFERENCES `inquiries` (`inquiry_id`) ON DELETE SET NULL;

--
-- Constraints for table `sales_contracts`
--
ALTER TABLE `sales_contracts`
  ADD CONSTRAINT `sales_contracts_ibfk_1` FOREIGN KEY (`sale_id`) REFERENCES `sales` (`sale_id`),
  ADD CONSTRAINT `sales_contracts_ibfk_2` FOREIGN KEY (`reviewed_by`) REFERENCES `users` (`user_id`) ON DELETE SET NULL;

--
-- Constraints for table `service_bookings`
--
ALTER TABLE `service_bookings`
  ADD CONSTRAINT `service_bookings_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customer_details` (`user_id`) ON DELETE SET NULL,
  ADD CONSTRAINT `service_bookings_ibfk_2` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`vehicle_id`),
  ADD CONSTRAINT `service_bookings_ibfk_3` FOREIGN KEY (`slot_id`) REFERENCES `service_slots` (`slot_id`),
  ADD CONSTRAINT `service_bookings_ibfk_4` FOREIGN KEY (`warranty_claim_id`) REFERENCES `warranty_claims` (`claim_id`) ON DELETE SET NULL,
  ADD CONSTRAINT `service_bookings_ibfk_5` FOREIGN KEY (`assigned_to`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `supplies`
--
ALTER TABLE `supplies`
  ADD CONSTRAINT `supplies_ibfk_1` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`supplier_id`);

--
-- Constraints for table `system_settings`
--
ALTER TABLE `system_settings`
  ADD CONSTRAINT `system_settings_ibfk_1` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`) ON DELETE SET NULL;

--
-- Constraints for table `user_profile`
--
ALTER TABLE `user_profile`
  ADD CONSTRAINT `user_profile_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `vehicles`
--
ALTER TABLE `vehicles`
  ADD CONSTRAINT `vehicles_ibfk_1` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`supplier_id`);

--
-- Constraints for table `vehicle_photos`
--
ALTER TABLE `vehicle_photos`
  ADD CONSTRAINT `vehicle_photos_ibfk_1` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`vehicle_id`) ON DELETE CASCADE;

--
-- Constraints for table `warranty_claims`
--
ALTER TABLE `warranty_claims`
  ADD CONSTRAINT `fk_wc_admin` FOREIGN KEY (`reviewed_by`) REFERENCES `users` (`user_id`) ON DELETE SET NULL,
  ADD CONSTRAINT `fk_wc_sale` FOREIGN KEY (`sale_id`) REFERENCES `sales` (`sale_id`),
  ADD CONSTRAINT `fk_wc_vehicle` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`vehicle_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
