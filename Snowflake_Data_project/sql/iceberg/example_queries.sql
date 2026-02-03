-- ============================================
-- Example Queries for Iceberg External Table
-- Zero-Copy: All queries read directly from S3
-- ============================================

USE DATABASE SNOWFLAKE_LEARNING_DB;
USE SCHEMA PUBLIC;

-- 1. Basic SELECT queries (zero-copy)
SELECT COUNT(*) as total_records FROM BRONZE_CRIMES_ICEBERG;

-- 2. Filtered queries
SELECT * FROM BRONZE_CRIMES_ICEBERG 
WHERE PRIMARY_TYPE = 'THEFT'
LIMIT 100;

-- 3. Aggregations
SELECT 
    PRIMARY_TYPE,
    COUNT(*) as incident_count,
    COUNT(DISTINCT CASE_NUMBER) as unique_cases
FROM BRONZE_CRIMES_ICEBERG
GROUP BY PRIMARY_TYPE
ORDER BY incident_count DESC;

-- 4. Date-based queries (if DATE column exists)
SELECT 
    YEAR,
    COUNT(*) as incidents_per_year
FROM BRONZE_CRIMES_ICEBERG
GROUP BY YEAR
ORDER BY YEAR DESC;

-- 5. JOIN with other tables (if needed)
-- SELECT 
--     i.CASE_NUMBER,
--     i.PRIMARY_TYPE,
--     i.DATE,
--     b.SOME_COLUMN
-- FROM BRONZE_CRIMES_ICEBERG i
-- JOIN BRONZE_CRIMES_2 b ON i.CASE_NUMBER = b.CASE_NUMBER;

-- ============================================
-- Data Modification (INSERT/UPDATE/DELETE)
-- Note: These operations write new Parquet files to S3
-- ============================================

-- 6. INSERT new records (writes to S3)
-- INSERT INTO BRONZE_CRIMES_ICEBERG 
-- (ID, CASE_NUMBER, DATE, PRIMARY_TYPE, ...)
-- VALUES 
-- (14053533, 'HY123462', '01/21/2024', 'THEFT', ...);

-- 7. UPDATE records (creates new Parquet files, old data preserved)
-- UPDATE BRONZE_CRIMES_ICEBERG
-- SET PRIMARY_TYPE = 'UPDATED_TYPE'
-- WHERE CASE_NUMBER = 'HY123459';

-- 8. DELETE records (marks for deletion, creates new metadata)
-- DELETE FROM BRONZE_CRIMES_ICEBERG
-- WHERE ID = 14053530;

-- 9. Check table statistics
SELECT 
    $1 as column_name,
    COUNT(*) as non_null_count
FROM BRONZE_CRIMES_ICEBERG
GROUP BY $1;

-- 10. Verify zero-copy - check that data is external
SHOW EXTERNAL TABLES LIKE 'BRONZE_CRIMES_ICEBERG';

