# Converting CSV to Iceberg Format

Your 14 million row CSV dataset needs to be converted to Iceberg format before Snowflake can query it as an external Iceberg table.

## Option 1: AWS Glue (Recommended - No Local Machine)

### Steps:

1. **Go to AWS Glue Console**
   - Navigate to AWS Glue Studio
   - Create a new ETL job

2. **Use the provided script**
   - Copy the script from `scripts/aws_glue_csv_to_iceberg.py`
   - Paste into Glue Studio script editor

3. **Configure Job Parameters**
   - `INPUT_PATH`: Your current CSV location in S3 (e.g., `s3://bucket/path/to/csv/`)
   - `OUTPUT_PATH`: `s3://snowflake-bronze-delta-mahi/root/crime_iceberg/`

4. **Run the Job**
   - Glue will convert CSV → Parquet → Iceberg format
   - Creates metadata files automatically
   - All done in AWS, no local machine needed

5. **Verify Output**
   - Check S3: `s3://snowflake-bronze-delta-mahi/root/crime_iceberg/`
   - Should see: `data/` folder (Parquet files) and `metadata/` folder

## Option 2: Snowflake External Table (CSV - Not Iceberg)

If you want to query CSV directly without Iceberg conversion:

```sql
-- Create external table for CSV (simpler, but not Iceberg)
CREATE OR REPLACE EXTERNAL TABLE BRONZE_CRIMES_CSV_EXTERNAL
  WITH LOCATION = @s3_csv_stage
  FILE_FORMAT = (TYPE = CSV, SKIP_HEADER = 1)
  PATTERN = '.*\.csv';

-- Create stage for CSV location
CREATE OR REPLACE STAGE s3_csv_stage
  URL = 's3://your-bucket/path/to/csv/'
  STORAGE_INTEGRATION = s3_iceberg_integration;
```

**Note**: This is a regular external table, not Iceberg. For true Iceberg with zero-copy and advanced features, use Option 1.

## Option 3: Use Snowflake to Write Iceberg (If Supported)

Some Snowflake editions support writing to external Iceberg tables:

```sql
-- Read from CSV external table
CREATE OR REPLACE EXTERNAL TABLE source_csv AS
SELECT * FROM @s3_csv_stage
FILE_FORMAT = (TYPE = CSV);

-- Write to Iceberg (if your Snowflake edition supports it)
INSERT INTO BRONZE_CRIMES_ICEBERG
SELECT * FROM source_csv;
```

Check your Snowflake edition capabilities for this feature.

## What Gets Created

After conversion, your S3 structure will be:

```
s3://snowflake-bronze-delta-mahi/root/crime_iceberg/
├── data/
│   ├── 00000-0-*.parquet
│   ├── 00001-0-*.parquet
│   └── ... (Parquet files)
├── metadata/
│   ├── snap-*.avro
│   ├── v*.metadata.json
│   └── ... (Iceberg metadata)
└── _spark_metadata/ (if using Spark)
```

## Next Steps

Once conversion is complete:
1. Run `sql/iceberg/create_iceberg_external_table.sql` in Snowflake
2. Start querying with zero-copy!

