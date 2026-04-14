-- ============================================================
-- OracleDB - User & Tablespace Setup
-- For: module-inventory
-- Run as SYSDBA
-- ============================================================

-- 1. Create tablespace (adjust path for your environment)
-- CREATE TABLESPACE TBS_INVENTORY
--     DATAFILE '/opt/oracle/oradata/ORCL/tbs_inventory01.dbf'
--     SIZE 100M
--     AUTOEXTEND ON NEXT 50M MAXSIZE 1G
--     LOGGING
--     EXTENT MANAGEMENT LOCAL
--     SEGMENT SPACE MANAGEMENT AUTO;

-- 2. Create user
CREATE USER inventory_user IDENTIFIED BY inventory1234
    DEFAULT TABLESPACE USERS
    TEMPORARY TABLESPACE TEMP
    QUOTA UNLIMITED ON USERS;

-- 3. Grant privileges
GRANT CONNECT, RESOURCE TO inventory_user;
GRANT CREATE SESSION TO inventory_user;
GRANT CREATE TABLE TO inventory_user;
GRANT CREATE SEQUENCE TO inventory_user;
GRANT CREATE VIEW TO inventory_user;
