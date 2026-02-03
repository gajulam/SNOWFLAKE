-- ============================================
-- Create External Iceberg Table in Snowflake
-- Zero-Copy: Data stays in S3, Snowflake queries directly
-- ============================================

-- Use your database and schema
USE DATABASE SNOWFLAKE_LEARNING_DB;
USE SCHEMA PUBLIC;

-- Step 1: Create or verify storage integration for Iceberg location
-- (You may already have this from the bronze pipeline setup)
-- If not, create one:
CREATE STORAGE INTEGRATION IF NOT EXISTS s3_iceberg_integration
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = 'S3'
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::211125758501:role/SnowflakeS3AccessRole'
  STORAGE_AWS_EXTERNAL_ID = 'snowflake-mahi-2024-7f3a9b2c-4d5e-6f7a-8b9c-0d1e2f3a4b5c'
  STORAGE_ALLOWED_LOCATIONS = ('s3://snowflake-bronze-delta-mahi/root/crime_iceberg/');

-- Step 2: Create external stage for the Iceberg location
CREATE OR REPLACE STAGE s3_iceberg_stage
  URL = 's3://snowflake-bronze-delta-mahi/root/crime_iceberg/'
  STORAGE_INTEGRATION = s3_iceberg_integration;

-- Step 3: Create external Iceberg table
-- Note: This assumes the Iceberg table already exists in S3 with metadata
-- The data must be in Iceberg format (Parquet files + metadata) in S3
-- 
-- Option A: Using AWS Glue Catalog (Recommended if you registered table in Glue)
CREATE OR REPLACE ICEBERG TABLE BRONZE_CRIMES_ICEBERG
  EXTERNAL_VOLUME = 'iceberg_volume'  -- Create external volume first (see configure_catalog.sql)
  CATALOG = 'SNOWFLAKE'
  BASE_LOCATION = 's3://snowflake-bronze-delta-mahi/root/crime_iceberg/';

-- Option B: If using AWS Glue Catalog (alternative syntax)
-- CREATE OR REPLACE ICEBERG TABLE BRONZE_CRIMES_ICEBERG
--   CATALOG = 'AwsDataCatalog'
--   EXTERNAL_VOLUME = 'iceberg_volume'
--   CATALOG_TABLE = 'crime_data_db.crime_iceberg';

-- Option C: Direct S3 path (if not using catalog)
-- Note: Check your Snowflake edition - some require catalog integration
-- CREATE OR REPLACE ICEBERG TABLE BRONZE_CRIMES_ICEBERG
--   EXTERNAL_VOLUME = 'iceberg_volume'
--   BASE_LOCATION = 's3://snowflake-bronze-delta-mahi/root/crime_iceberg/';

-- Step 4: Verify the external table
DESC EXTERNAL TABLE BRONZE_CRIMES_ICEBERG;

-- Step 5: Test query (zero-copy - data stays in S3)
SELECT COUNT(*) FROM BRONZE_CRIMES_ICEBERG;

-- Step 6: Query sample data
SELECT * FROM BRONZE_CRIMES_ICEBERG LIMIT 10;

