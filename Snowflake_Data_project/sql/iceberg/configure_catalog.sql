-- ============================================
-- Configure Iceberg Catalog Integration
-- Options: AWS Glue Catalog or S3-based catalog
-- ============================================

USE DATABASE SNOWFLAKE_LEARNING_DB;
USE SCHEMA PUBLIC;

-- Option 1: Create External Volume (Required for Iceberg tables)
-- External volumes allow Snowflake to read/write Iceberg tables in S3

CREATE OR REPLACE EXTERNAL VOLUME iceberg_volume
  STORAGE_LOCATIONS = (
    (
      NAME = 's3-iceberg-location'
      STORAGE_PROVIDER = 'S3'
      STORAGE_BASE_URL = 's3://snowflake-bronze-delta-mahi/root/crime_iceberg/'
      STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::211125758501:role/SnowflakeS3AccessRole'
    )
  );

-- Verify external volume was created
SHOW EXTERNAL VOLUMES LIKE 'iceberg_volume';
DESC EXTERNAL VOLUME iceberg_volume;

-- Option 2: AWS Glue Catalog Integration
-- This allows Snowflake to use AWS Glue as the catalog for Iceberg tables
-- (Optional - only if you registered the table in Glue Catalog)

-- Option 2: Direct S3 Catalog (if not using Glue)
-- The external table can point directly to S3 location
-- No catalog integration needed - Snowflake reads metadata from S3

-- Verify storage integration exists
SHOW INTEGRATIONS LIKE 's3_iceberg_integration';

-- Get integration details
DESC INTEGRATION s3_iceberg_integration;

