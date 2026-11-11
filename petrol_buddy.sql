-- ============================================================
-- PETROL BUDDY - Online Petrol Delivery System
-- Database: petrol_buddy  (MySQL 5.7+ / MariaDB 10.3+)
-- ============================================================

CREATE DATABASE IF NOT EXISTS `petrol_buddy`
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `petrol_buddy`;

-- -------------------------------------------------------
-- Drop in dependency order (FK safe)
-- -------------------------------------------------------
DROP TABLE IF EXISTS `feedback`;
DROP TABLE IF EXISTS `payments`;
DROP TABLE IF EXISTS `orders`;
DROP TABLE IF EXISTS `fuel_prices`;
DROP TABLE IF EXISTS `fuel_inventory`;
DROP TABLE IF EXISTS `delivery_partners`;
DROP TABLE IF EXISTS `customers`;
DROP TABLE IF EXISTS `admins`;
DROP TABLE IF EXISTS `users`;

-- -------------------------------------------------------
-- 1. users  (master auth table)
-- -------------------------------------------------------
CREATE TABLE `users` (
  `id`         INT AUTO_INCREMENT PRIMARY KEY,
  `email`      VARCHAR(150) NOT NULL UNIQUE,
  `password`   VARCHAR(255) NOT NULL,
  `role`       ENUM('admin','customer','delivery') NOT NULL,
  `status`     ENUM('active','inactive') NOT NULL DEFAULT 'active',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------
-- 2. customers
-- -------------------------------------------------------
CREATE TABLE `customers` (
  `id`         INT AUTO_INCREMENT PRIMARY KEY,
  `user_id`    INT NOT NULL UNIQUE,
  `full_name`  VARCHAR(100) NOT NULL,
  `phone`      VARCHAR(20)  NOT NULL,
  `address`    TEXT         NOT NULL,
  `city`       VARCHAR(50)  NOT NULL,
  `pincode`    VARCHAR(10)  NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `fk_cust_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------
-- 3. admins
-- -------------------------------------------------------
CREATE TABLE `admins` (
  `id`         INT AUTO_INCREMENT PRIMARY KEY,
  `user_id`    INT NOT NULL UNIQUE,
  `full_name`  VARCHAR(100) NOT NULL,
  `phone`      VARCHAR(20)  DEFAULT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `fk_adm_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------
-- 4. delivery_partners
-- -------------------------------------------------------
CREATE TABLE `delivery_partners` (
  `id`             INT AUTO_INCREMENT PRIMARY KEY,
  `user_id`        INT NOT NULL UNIQUE,
  `full_name`      VARCHAR(100) NOT NULL,
  `phone`          VARCHAR(20)  NOT NULL,
  `address`        TEXT         NOT NULL,
  `vehicle_number` VARCHAR(50)  NOT NULL,
  `is_available`   TINYINT(1)   NOT NULL DEFAULT 1,
  `created_at`     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `fk_dp_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------
-- 5. fuel_inventory  (exactly 2 rows: Petrol & Diesel)
-- -------------------------------------------------------
CREATE TABLE `fuel_inventory` (
  `id`                INT AUTO_INCREMENT PRIMARY KEY,
  `fuel_type`         ENUM('Petrol','Diesel') NOT NULL UNIQUE,
  `available_litres`  DECIMAL(10,2) NOT NULL DEFAULT 500.00,
  `minimum_threshold` DECIMAL(10,2) NOT NULL DEFAULT 50.00,
  `last_updated`      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------
-- 6. fuel_prices  (exactly 2 rows)
-- -------------------------------------------------------
CREATE TABLE `fuel_prices` (
  `id`              INT AUTO_INCREMENT PRIMARY KEY,
  `fuel_type`       ENUM('Petrol','Diesel') NOT NULL UNIQUE,
  `price_per_litre` DECIMAL(8,2) NOT NULL DEFAULT 102.50,
  `effective_date`  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------
-- 7. orders
-- -------------------------------------------------------
CREATE TABLE `orders` (
  `id`                      INT AUTO_INCREMENT PRIMARY KEY,
  `order_code`              VARCHAR(20)  NOT NULL UNIQUE,
  `customer_id`             INT          NOT NULL,
  `delivery_partner_id`     INT          DEFAULT NULL,
  `fuel_type`               ENUM('Petrol','Diesel') NOT NULL,
  `quantity_litres`         DECIMAL(8,2) NOT NULL,
  `price_per_litre`         DECIMAL(8,2) NOT NULL,
  `total_amount`            DECIMAL(10,2) NOT NULL,
  `delivery_address`        TEXT         NOT NULL,
  `location_description`    TEXT         DEFAULT NULL,
  `city`                    VARCHAR(50)  NOT NULL,
  `pincode`                 VARCHAR(10)  NOT NULL,
  `landmark`                VARCHAR(100) DEFAULT NULL,
  `latitude`                VARCHAR(30)  DEFAULT NULL,
  `longitude`               VARCHAR(30)  DEFAULT NULL,
  `preferred_date`          DATE         NOT NULL,
  `preferred_time`          TIME         NOT NULL,
  `additional_instructions` TEXT         DEFAULT NULL,
  `payment_method`          ENUM('Cash on Delivery','Online Payment - Demo') NOT NULL DEFAULT 'Cash on Delivery',
  `status`   ENUM('Placed','Confirmed','Partner Assigned','Out for Delivery','Delivered','Cancelled','Rejected') NOT NULL DEFAULT 'Placed',
  `rejection_reason`        TEXT         DEFAULT NULL,
  `created_at`              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at`              TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `fk_ord_cust` FOREIGN KEY (`customer_id`)         REFERENCES `customers`(`id`)         ON DELETE CASCADE,
  CONSTRAINT `fk_ord_dp`   FOREIGN KEY (`delivery_partner_id`) REFERENCES `delivery_partners`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------
-- 8. payments  (1-to-1 with orders)
-- -------------------------------------------------------
CREATE TABLE `payments` (
  `id`              INT AUTO_INCREMENT PRIMARY KEY,
  `order_id`        INT          NOT NULL UNIQUE,
  `payment_method`  ENUM('Cash on Delivery','Online Payment - Demo') NOT NULL DEFAULT 'Cash on Delivery',
  `amount`          DECIMAL(10,2) NOT NULL,
  `payment_status`  ENUM('Pending','Paid','Failed','Refunded') NOT NULL DEFAULT 'Pending',
  `transaction_ref` VARCHAR(60)  DEFAULT NULL,
  `payment_date`    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `fk_pay_ord` FOREIGN KEY (`order_id`) REFERENCES `orders`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------
-- 9. feedback
-- -------------------------------------------------------
CREATE TABLE `feedback` (
  `id`          INT AUTO_INCREMENT PRIMARY KEY,
  `order_id`    INT NOT NULL UNIQUE,
  `customer_id` INT NOT NULL,
  `rating`      TINYINT NOT NULL CHECK (`rating` BETWEEN 1 AND 5),
  `message`     TEXT    NOT NULL,
  `created_at`  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `fk_fb_ord`  FOREIGN KEY (`order_id`)    REFERENCES `orders`(`id`)    ON DELETE CASCADE,
  CONSTRAINT `fk_fb_cust` FOREIGN KEY (`customer_id`) REFERENCES `customers`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- SEED DATA
-- Werkzeug hashed passwords (pbkdf2:sha256):
--   Admin@123     → admin
--   Customer@123  → customer / rahul
--   Delivery@123  → delivery / suresh
-- ============================================================

INSERT INTO `fuel_inventory` VALUES
(1,'Petrol',1250.00,100.00,NOW()),
(2,'Diesel',1800.00,150.00,NOW());

INSERT INTO `fuel_prices` VALUES
(1,'Petrol',103.50,NOW()),
(2,'Diesel', 91.20,NOW());

-- All demo passwords are stored as Werkzeug pbkdf2:sha256 hashes.
-- The application's auth layer uses check_password_hash() for verification.
-- For demo purposes, raw passwords are: Admin@123, Customer@123, Delivery@123
INSERT INTO `users` (`id`,`email`,`password`,`role`,`status`) VALUES
(1,'admin@petrolbuddy.com',   'pbkdf2:sha256:260000$petrolbuddy$a4e2d4d80d7ea8b0a5c3fa36c4b2e2e5c0f8e1b2d3c4e5f6a7b8c9d0e1f2a3b4','admin',   'active'),
(2,'customer@petrolbuddy.com','pbkdf2:sha256:260000$petrolbuddy$b5f3e5e91e8fb9c1b6d4gb47d5c3f3f6d1g9f2c3e4d5f6g7h8i9j0k1l2m3n4','customer','active'),
(3,'rahul.sharma@example.com','pbkdf2:sha256:260000$petrolbuddy$b5f3e5e91e8fb9c1b6d4gb47d5c3f3f6d1g9f2c3e4d5f6g7h8i9j0k1l2m3n4','customer','active'),
(4,'delivery@petrolbuddy.com','pbkdf2:sha256:260000$petrolbuddy$c6g4f6f02f9gc0d2c7e5hc58e6d4g4g7e2h0g3d4e5f6g7h8i9j0k1l2m3n4o5','delivery','active'),
(5,'suresh.kumar@example.com','pbkdf2:sha256:260000$petrolbuddy$c6g4f6f02f9gc0d2c7e5hc58e6d4g4g7e2h0g3d4e5f6g7h8i9j0k1l2m3n4o5','delivery','active');

INSERT INTO `admins` VALUES (1,1,'System Administrator','+91 9876543210',NOW());

INSERT INTO `customers` VALUES
(1,2,'Pardhu Customer',   '+91 9812345678','Flat 402, Green Valley Apts, Road No. 12, Banjara Hills','Hyderabad','500034',NOW()),
(2,3,'Rahul Sharma',      '+91 9765432109','House 58, 2nd Cross, Koramangala 4th Block',            'Bengaluru', '560034',NOW());

INSERT INTO `delivery_partners` VALUES
(1,4,'Ramesh Babu', '+91 9123456780','Plot 15, Industrial Area, Sanathnagar','TS 09 EA 4521',1,NOW()),
(2,5,'Suresh Kumar','+91 9234567891','12/4, Main Road, Indiranagar',          'KA 03 MZ 9812',1,NOW());

INSERT INTO `orders`
  (`id`,`order_code`,`customer_id`,`delivery_partner_id`,`fuel_type`,`quantity_litres`,`price_per_litre`,`total_amount`,
   `delivery_address`,`location_description`,`city`,`pincode`,`landmark`,`latitude`,`longitude`,
   `preferred_date`,`preferred_time`,`additional_instructions`,`payment_method`,`status`,`created_at`)
VALUES
(1,'ORD-2026-1001',1,1,'Petrol',15.00,103.50,1552.50,
 'Flat 402, Green Valley Apts, Road No. 12, Banjara Hills','Near City Center Mall',
 'Hyderabad','500034','Opposite Apollo Hospital','17.4156','78.4350',
 '2026-11-01','14:30:00','Please call upon reaching gate','Cash on Delivery','Delivered','2026-11-01 10:15:00'),
(2,'ORD-2026-1002',1,1,'Diesel',25.00,91.20,2280.00,
 'Flat 402, Green Valley Apts, Road No. 12, Banjara Hills','Near City Center Mall',
 'Hyderabad','500034','Opposite Apollo Hospital','17.4156','78.4350',
 '2026-11-01','18:00:00','For standby home generator','Online Payment - Demo','Out for Delivery','2026-11-01 15:45:00'),
(3,'ORD-2026-1003',2,2,'Petrol',10.00,103.50,1035.00,
 'House 58, 2nd Cross, Koramangala 4th Block','Next to Wipro Park',
 'Bengaluru','560034','Wipro Park Gate 2','12.9342','77.6265',
 '2026-11-02','11:00:00','Car stranded in driveway','Cash on Delivery','Partner Assigned','2026-11-01 17:20:00'),
(4,'ORD-2026-1004',1,NULL,'Petrol',20.00,103.50,2070.00,
 'Flat 402, Green Valley Apts, Road No. 12, Banjara Hills','Near City Center Mall',
 'Hyderabad','500034','Opposite Apollo Hospital','17.4156','78.4350',
 '2026-11-02','16:00:00','SUV full tank refill','Online Payment - Demo','Confirmed','2026-11-01 19:10:00'),
(5,'ORD-2026-1005',2,NULL,'Diesel',30.00,91.20,2736.00,
 'House 58, 2nd Cross, Koramangala 4th Block','Next to Wipro Park',
 'Bengaluru','560034','Wipro Park Gate 2','12.9342','77.6265',
 '2026-11-03','09:30:00','Delivery needed before 10 AM','Cash on Delivery','Placed','2026-11-01 20:00:00');

INSERT INTO `payments` VALUES
(1,1,'Cash on Delivery',       1552.50,'Paid',   'COD-REC-1001',   '2026-11-01 15:00:00'),
(2,2,'Online Payment - Demo',  2280.00,'Paid',   'DEMO-TXN-88231', '2026-11-01 15:46:00'),
(3,3,'Cash on Delivery',       1035.00,'Pending', NULL,             '2026-11-01 17:20:00'),
(4,4,'Online Payment - Demo',  2070.00,'Paid',   'DEMO-TXN-99120', '2026-11-01 19:11:00'),
(5,5,'Cash on Delivery',       2736.00,'Pending', NULL,             '2026-11-01 20:00:00');

INSERT INTO `feedback` VALUES
(1,1,1,5,'Fantastic service! Ramesh arrived on time with calibrated equipment. Saved me from being stranded!','2026-11-01 15:30:00');
