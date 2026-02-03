# Apache Iceberg Zero-Copy Setup with Snowflake

This setup allows you to query 14 million crime data rows directly from S3 using Snowflake as a query engine, with zero data copying into Snowflake.

## Architecture

- **Data Location**: `s3://snowflake-bronze-delta-mahi/root/crime_iceberg/`
- **Query Engine**: Snowflake (external table)
- **Data Format**: Apache Iceberg (Parquet files + metadata)
- **Zero-Copy**: Data stays in S3, Snowflake queries directly

## Prerequisites

1. **Iceberg Data in S3**: Your CSV data must first be converted to Iceberg format (Parquet + metadata)
2. **Storage Integration**: Already set up from bronze pipeline
3. **IAM Role**: Already configured with S3 access

## Setup Steps

### Step 1: Convert CSV to Iceberg Format

Your CSV data in S3 needs to be converted to Iceberg format first. Options:

**Option A: Use AWS Glue** (Recommended - no local scripts)
1. Create Glue ETL job to read CSV from S3
2. Convert to Parquet format
3. Write as Iceberg table to `s3://snowflake-bronze-delta-mahi/root/crime_iceberg/`

**Option B: Use Spark/PySpark** (One-time conversion)
- Run conversion script to transform CSV → Iceberg
- Outputs Parquet files + metadata to S3

### Step 2: Create External Iceberg Table in Snowflake

Run the SQL script to create the external table:

```sql
-- Run: sql/iceberg/create_iceberg_external_table.sql
```

This creates `BRONZE_CRIMES_ICEBERG` as an external table pointing to your S3 Iceberg data.

### Step 3: Query the Data

Once set up, query directly from Snowflake:

```sql
-- Zero-copy query - data stays in S3
SELECT COUNT(*) FROM BRONZE_CRIMES_ICEBERG;

SELECT * FROM BRONZE_CRIMES_ICEBERG 
WHERE PRIMARY_TYPE = 'THEFT'
LIMIT 100;
```

## Data Editing

### Via Snowflake SQL

```sql
-- INSERT new records (writes new Parquet files to S3)
INSERT INTO BRONZE_CRIMES_ICEBERG VALUES (...);

-- UPDATE records (creates new files, preserves old data)
UPDATE BRONZE_CRIMES_ICEBERG SET ... WHERE ...;

-- DELETE records (updates metadata)
DELETE FROM BRONZE_CRIMES_ICEBERG WHERE ...;
```

### Direct S3 Editing

If you edit Parquet files directly in S3:
1. Use Spark/PySpark to modify files
2. Update Iceberg metadata
3. Refresh Snowflake table view

## Important Notes

1. **Iceberg Format Required**: Data must be in Iceberg format (Parquet + metadata), not raw CSV
2. **Zero-Copy**: Data never moves into Snowflake - all queries read from S3
3. **Performance**: Queries may be slower than native Snowflake tables (network latency to S3)
4. **Metadata**: Iceberg maintains metadata files that track schema, partitions, and file versions

## Files

- `sql/iceberg/create_iceberg_external_table.sql` - Create external table
- `sql/iceberg/configure_catalog.sql` - Catalog configuration
- `sql/iceberg/example_queries.sql` - Example queries and operations
- `config/iceberg_config.yaml` - Configuration settings

## Next Steps

1. Convert your CSV data to Iceberg format (use AWS Glue or Spark)
2. Ensure data is in `s3://snowflake-bronze-delta-mahi/root/crime_iceberg/`
3. Run the SQL scripts to create the external table
4. Start querying!

