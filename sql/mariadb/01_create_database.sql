-- ============================================================
-- MariaDB - Database & User Setup
-- For: core, module-user
-- ============================================================

CREATE DATABASE IF NOT EXISTS storage_3d_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_general_ci;

-- Grant privileges (adjust as needed)
-- CREATE USER 'app_user'@'%' IDENTIFIED BY 'app_password';
-- GRANT ALL PRIVILEGES ON storage_3d_db.* TO 'app_user'@'%';
-- FLUSH PRIVILEGES;

USE storage_3d_db;

-- ============================================================
-- module-user tables (prefix: MOD_USER_)
-- ============================================================

CREATE TABLE IF NOT EXISTS MOD_USER_USERS (
    USER_ID     BIGINT AUTO_INCREMENT PRIMARY KEY,
    USERNAME    VARCHAR(50)  NOT NULL UNIQUE,
    EMAIL       VARCHAR(100) NOT NULL,
    CREATED_AT  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    UPDATED_AT  DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
