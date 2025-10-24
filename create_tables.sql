-- Funza Mama Database Tables Creation Script
-- Run this in phpMyAdmin or MySQL command line

-- Create users table
CREATE TABLE IF NOT EXISTS `users` (
  `user_ID` int(11) NOT NULL AUTO_INCREMENT,
  `first_name` varchar(100) NOT NULL,
  `second_name` varchar(100) NOT NULL,
  `username` varchar(100) NOT NULL UNIQUE,
  `email` varchar(255) NOT NULL UNIQUE,
  `password_hash` varchar(255) NOT NULL,
  `avatar` varchar(255) DEFAULT NULL,
  `email_verified` tinyint(1) DEFAULT 0,
  `email_verification_token` varchar(255) DEFAULT NULL,
  `last_login` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create quiz_questions table
CREATE TABLE IF NOT EXISTS `quiz_questions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `scenario` varchar(50) NOT NULL,
  `question` text NOT NULL,
  `options` text NOT NULL,
  `answer` varchar(255) NOT NULL,
  `correct_reason` text,
  `incorrect_reason` text,
  `used` tinyint(1) DEFAULT 0,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`user_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create user_responses table
CREATE TABLE IF NOT EXISTS `user_responses` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `user_id` int(11) NOT NULL,
  `question_id` int(11) DEFAULT NULL,
  `selected_option` varchar(255) NOT NULL,
  `is_correct` tinyint(1) NOT NULL,
  `attempt_number` int(11) DEFAULT 1,
  `stage` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `question_id` (`question_id`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`user_ID`),
  FOREIGN KEY (`question_id`) REFERENCES `quiz_questions`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create badge table
CREATE TABLE IF NOT EXISTS `badge` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_ID` int(11) NOT NULL,
  `badge_name` varchar(100) NOT NULL,
  `score` int(11) NOT NULL,
  `number_of_attempts` int(11) NOT NULL,
  `progress` float NOT NULL,
  `claimed` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `user_ID` (`user_ID`),
  FOREIGN KEY (`user_ID`) REFERENCES `users`(`user_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create game_stages table
CREATE TABLE IF NOT EXISTS `game_stages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `user_ID` int(11) NOT NULL,
  `stage_name` enum('Preconception','Antenatal','Birth','Postnatal') NOT NULL,
  `number_of_attempts` int(11) DEFAULT 0,
  `overall_score` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_ID` (`user_ID`),
  FOREIGN KEY (`user_ID`) REFERENCES `users`(`user_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create user_scenario_progress table
CREATE TABLE IF NOT EXISTS `user_scenario_progress` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `user_id` int(11) NOT NULL,
  `scenario` varchar(50) NOT NULL,
  `attempt_count` int(11) DEFAULT 0,
  `last_attempt_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `completed` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`user_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create user_question_history table for adaptive learning
CREATE TABLE IF NOT EXISTS `user_question_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `user_id` int(11) NOT NULL,
  `stage` varchar(50) NOT NULL,
  `question_text` text NOT NULL,
  `question_hash` varchar(64) NOT NULL,
  `is_correct` tinyint(1) NOT NULL,
  `attempt_count` int(11) DEFAULT 1,
  `last_attempted` datetime DEFAULT CURRENT_TIMESTAMP,
  `difficulty_level` int(11) DEFAULT 1,
  `needs_review` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `stage` (`stage`),
  KEY `question_hash` (`question_hash`),
  KEY `needs_review` (`needs_review`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`user_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create feedback table for user feedback system
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
