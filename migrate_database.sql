-- Migration script to add missing columns to existing database
-- Run this in phpMyAdmin or MySQL command line

-- Add missing columns to users table
ALTER TABLE `users` 
ADD COLUMN `email_verified` tinyint(1) DEFAULT 0 AFTER `avatar`,
ADD COLUMN `email_verification_token` varchar(255) DEFAULT NULL AFTER `email_verified`,
ADD COLUMN `last_login` datetime DEFAULT NULL AFTER `email_verification_token`,
ADD COLUMN `created_at` datetime DEFAULT CURRENT_TIMESTAMP AFTER `last_login`,
ADD COLUMN `role` varchar(20) DEFAULT 'user' AFTER `created_at`,
ADD COLUMN `age` int(3) DEFAULT NULL AFTER `role`,
ADD COLUMN `gender` varchar(10) DEFAULT NULL AFTER `age`;

-- Create feedback table if it doesn't exist
CREATE TABLE IF NOT EXISTS `feedback` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `user_name` varchar(100) NOT NULL,
  `email` varchar(255) NOT NULL,
  `category` varchar(50) NOT NULL,
  `message` text NOT NULL,
  `status` varchar(20) DEFAULT 'pending',
  `admin_reply` text DEFAULT NULL,
  `screenshot_path` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `status` (`status`),
  KEY `category` (`category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Update existing users to have email_verified = 1 (for backward compatibility)
UPDATE `users` SET `email_verified` = 1 WHERE `email_verified` IS NULL;
