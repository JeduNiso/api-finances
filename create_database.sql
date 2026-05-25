-- ============================================================
-- Django Finance API - Full Database Schema
-- Run this script to create all tables from scratch
-- ============================================================

SET FOREIGN_KEY_CHECKS = 0;

-- ------------------------------------------------------------
-- Django system tables
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_uniq` (`app_label`, `model`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_uniq` (`content_type_id`, `codename`),
  CONSTRAINT `auth_permission_content_type_id_fk` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_uniq` (`group_id`, `permission_id`),
  CONSTRAINT `auth_group_permissions_group_id_fk` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_group_permissions_permission_id_fk` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- App tables (no foreign key dependencies)
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `banks` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `banks_name_uniq` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `categories` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `icon` varchar(50) DEFAULT NULL,
  `color` varchar(20) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `categories_name_uniq` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `roles` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `role` varchar(50) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `roles_role_uniq` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- Users (depends on roles)
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `users` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL DEFAULT 0,
  `name` varchar(100) NOT NULL,
  `username` varchar(50) DEFAULT NULL,
  `email` varchar(100) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `email_verified_at` datetime(6) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `is_staff` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `role_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_username_uniq` (`username`),
  UNIQUE KEY `users_email_uniq` (`email`),
  CONSTRAINT `users_role_id_fk` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- M2M: users <-> auth_group
CREATE TABLE IF NOT EXISTS `api_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `api_user_groups_user_id_group_id_uniq` (`user_id`, `group_id`),
  CONSTRAINT `api_user_groups_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `api_user_groups_group_id_fk` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- M2M: users <-> auth_permission
CREATE TABLE IF NOT EXISTS `api_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `api_user_user_permissions_user_id_permission_id_uniq` (`user_id`, `permission_id`),
  CONSTRAINT `api_user_user_permissions_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `api_user_user_permissions_permission_id_fk` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- Families (depends on users)
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `families` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `owner_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `families_owner_id_fk` FOREIGN KEY (`owner_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- Accounts (depends on banks, families)
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `accounts` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `account_number` varchar(50) NOT NULL,
  `balance` decimal(15,2) NOT NULL DEFAULT 0.00,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `bank_id` bigint NOT NULL,
  `family_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accounts_account_number_uniq` (`account_number`),
  CONSTRAINT `accounts_bank_id_fk` FOREIGN KEY (`bank_id`) REFERENCES `banks` (`id`),
  CONSTRAINT `accounts_family_id_fk` FOREIGN KEY (`family_id`) REFERENCES `families` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- Debts (depends on users, accounts)
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `debts` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `creditor` varchar(150) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `original_amount` decimal(15,2) NOT NULL,
  `current_balance` decimal(15,2) NOT NULL,
  `monthly_payment` decimal(15,2) DEFAULT NULL,
  `interest_rate` decimal(5,2) NOT NULL DEFAULT 0.00,
  `start_date` date DEFAULT NULL,
  `due_date` date DEFAULT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'active',
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `account_id` bigint DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `debts_account_id_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE SET NULL,
  CONSTRAINT `debts_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `debts_payments` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `amount` decimal(15,2) NOT NULL,
  `paid_at` date NOT NULL,
  `notes` varchar(255) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `account_id` bigint NOT NULL,
  `debt_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `debts_payments_account_id_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`),
  CONSTRAINT `debts_payments_debt_id_fk` FOREIGN KEY (`debt_id`) REFERENCES `debts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- Expenses (depends on accounts, categories)
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `expenses` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  `amount` decimal(15,2) NOT NULL,
  `day_of_month` smallint NOT NULL,
  `frequency` varchar(20) NOT NULL DEFAULT 'monthly',
  `active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `account_id` bigint NOT NULL,
  `category_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `expenses_account_id_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`),
  CONSTRAINT `expenses_category_id_fk` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `expenses_log` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `amount_paid` decimal(15,2) NOT NULL,
  `paid_at` date NOT NULL,
  `notes` varchar(255) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `account_id` bigint NOT NULL,
  `expense_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `expenses_log_account_id_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`),
  CONSTRAINT `expenses_log_expense_id_fk` FOREIGN KEY (`expense_id`) REFERENCES `expenses` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- Family members (depends on families, users)
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `family_members` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `role` varchar(20) NOT NULL DEFAULT 'member',
  `joined_at` datetime(6) NOT NULL,
  `family_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `family_members_family_id_user_id_uniq` (`family_id`, `user_id`),
  CONSTRAINT `family_members_family_id_fk` FOREIGN KEY (`family_id`) REFERENCES `families` (`id`) ON DELETE CASCADE,
  CONSTRAINT `family_members_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- Spending (depends on users, accounts, categories)
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `spending` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `amount` decimal(15,2) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `spent_at` date NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `account_id` bigint NOT NULL,
  `category_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `spending_account_id_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`),
  CONSTRAINT `spending_category_id_fk` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`),
  CONSTRAINT `spending_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- Users <-> Accounts M2M (depends on users, accounts)
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `users_accounts` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `account_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_accounts_user_id_account_id_uniq` (`user_id`, `account_id`),
  CONSTRAINT `users_accounts_account_id_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE,
  CONSTRAINT `users_accounts_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- JWT Token Blacklist (simplejwt, depends on users)
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `token_blacklist_outstandingtoken` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `token` longtext NOT NULL,
  `jti` varchar(255) NOT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `expires_at` datetime(6) NOT NULL,
  `user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token_blacklist_outstandingtoken_jti_uniq` (`jti`),
  CONSTRAINT `token_blacklist_outstandingtoken_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `token_blacklist_blacklistedtoken` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `blacklisted_at` datetime(6) NOT NULL,
  `token_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token_blacklist_blacklistedtoken_token_id_uniq` (`token_id`),
  CONSTRAINT `token_blacklist_blacklistedtoken_token_id_fk` FOREIGN KEY (`token_id`) REFERENCES `token_blacklist_outstandingtoken` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;

-- ------------------------------------------------------------
-- Mark all Django migrations as applied
-- (so `manage.py migrate` won't try to re-run them)
-- ------------------------------------------------------------

INSERT IGNORE INTO `django_migrations` (`app`, `name`, `applied`) VALUES
  ('contenttypes', '0001_initial',                          NOW(6)),
  ('contenttypes', '0002_remove_content_type_name',         NOW(6)),
  ('auth',         '0001_initial',                          NOW(6)),
  ('auth',         '0002_alter_permission_name_max_length', NOW(6)),
  ('auth',         '0003_alter_user_email_max_length',      NOW(6)),
  ('auth',         '0004_alter_user_username_opts',         NOW(6)),
  ('auth',         '0005_alter_user_last_login_null',       NOW(6)),
  ('auth',         '0006_require_contenttypes_0002',        NOW(6)),
  ('auth',         '0007_alter_validators_add_error_messages', NOW(6)),
  ('auth',         '0008_alter_user_username_max_length',   NOW(6)),
  ('auth',         '0009_alter_user_last_name_max_length',  NOW(6)),
  ('auth',         '0010_alter_group_name_max_length',      NOW(6)),
  ('auth',         '0011_update_proxy_permissions',         NOW(6)),
  ('auth',         '0012_alter_user_first_name_max_length', NOW(6)),
  ('api',          '0001_initial',                          NOW(6)),
  ('token_blacklist', '0001_initial',                       NOW(6)),
  ('token_blacklist', '0002_outstandingtoken_jti_hex',      NOW(6)),
  ('token_blacklist', '0003_auto_20171017_2007',            NOW(6)),
  ('token_blacklist', '0004_auto_20171017_2013',            NOW(6)),
  ('token_blacklist', '0005_remove_outstandingtoken_jti',   NOW(6)),
  ('token_blacklist', '0006_auto_20171017_2113',            NOW(6)),
  ('token_blacklist', '0007_auto_20171017_2214',            NOW(6)),
  ('token_blacklist', '0008_migrate_to_bigautofield',       NOW(6)),
  ('token_blacklist', '0009_update_jti_field',              NOW(6)),
  ('token_blacklist', '0010_fix_migrate',                   NOW(6)),
  ('token_blacklist', '0011_linearize_history',             NOW(6)),
  ('token_blacklist', '0012_alter_outstandingtoken_user',   NOW(6));
