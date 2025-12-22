-- PostgreSQL initialization script for Memora Core
-- This script runs when the PostgreSQL container starts for the first time

-- Create database if it doesn't exist (handled by environment variables)
-- Create extensions that might be useful
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Set timezone
SET timezone = 'UTC';

-- Create a read-only user for backups (optional)
-- CREATE USER memora_readonly WITH PASSWORD 'readonly_password_2024';
-- GRANT CONNECT ON DATABASE memora_db TO memora_readonly;
-- GRANT USAGE ON SCHEMA public TO memora_readonly;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO memora_readonly;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO memora_readonly;
