"""
AWS Glue Script to Convert CSV to Iceberg Format
Run this in AWS Glue Studio - no local machine needed
Converts CSV data from S3 to Iceberg format (Parquet + metadata)
"""

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import functions as F
from pyspark.sql.types import *

# Initialize Glue context
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'INPUT_PATH', 'OUTPUT_PATH'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Configuration
INPUT_PATH = args.get('INPUT_PATH', 's3://snowflake-bronze-delta-mahi/crime_iceberg/Crimes_-_2025_20251213.csv')
OUTPUT_PATH = args.get('OUTPUT_PATH', 's3://snowflake-bronze-delta-mahi/crime_iceberg/')

# Read CSV data from S3
print(f"Reading CSV from: {INPUT_PATH}")
df = spark.read \
    .format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .option("delimiter", ",") \
    .load(INPUT_PATH)

# Show schema
print("DataFrame Schema:")
df.printSchema()

# Show row count
row_count = df.count()
print(f"Total rows: {row_count}")

# Data type conversions to match Snowflake schema
# Only convert columns that exist to avoid errors
if "ID" in df.columns:
    df = df.withColumn("ID", df["ID"].cast("long"))
if "ARREST" in df.columns:
    df = df.withColumn("ARREST", df["ARREST"].cast("boolean"))
if "DOMESTIC" in df.columns:
    df = df.withColumn("DOMESTIC", df["DOMESTIC"].cast("boolean"))
if "BEAT" in df.columns:
    df = df.withColumn("BEAT", df["BEAT"].cast("int"))
if "DISTRICT" in df.columns:
    df = df.withColumn("DISTRICT", df["DISTRICT"].cast("int"))
if "WARD" in df.columns:
    df = df.withColumn("WARD", df["WARD"].cast("int"))
if "COMMUNITY_AREA" in df.columns:
    df = df.withColumn("COMMUNITY_AREA", df["COMMUNITY_AREA"].cast("int"))
if "X_COORDINATE" in df.columns:
    df = df.withColumn("X_COORDINATE", df["X_COORDINATE"].cast("double"))
if "Y_COORDINATE" in df.columns:
    df = df.withColumn("Y_COORDINATE", df["Y_COORDINATE"].cast("double"))
if "YEAR" in df.columns:
    df = df.withColumn("YEAR", df["YEAR"].cast("int"))
if "LATITUDE" in df.columns:
    df = df.withColumn("LATITUDE", df["LATITUDE"].cast("double"))
if "LONGITUDE" in df.columns:
    df = df.withColumn("LONGITUDE", df["LONGITUDE"].cast("double"))

# Ensure OUTPUT_PATH has no trailing slash for Iceberg LOCATION
OUTPUT_PATH = OUTPUT_PATH.rstrip("/")

database_name = "crime_data_db"
table_name = "crime_iceberg"
full_table_name = f"{database_name}.{table_name}"

# Create database if it doesn't exist
print(f"Creating database {database_name} if not exists...")
spark.sql(f"CREATE DATABASE IF NOT EXISTS {database_name}")

# Register DataFrame as temp view so we can use it in Spark SQL
df.createOrReplaceTempView("source_data")

# Create Iceberg table in Glue Catalog with data at OUTPUT_PATH
# Drop existing table first for overwrite behavior
print(f"Creating Iceberg table {full_table_name} at {OUTPUT_PATH}...")
try:
    spark.sql(f"DROP TABLE IF EXISTS {full_table_name}")
    spark.sql(f"""
        CREATE TABLE {full_table_name}
        USING iceberg
        LOCATION '{OUTPUT_PATH}'
        TBLPROPERTIES (
            'write.format.default' = 'parquet',
            'write.parquet.compression-codec' = 'snappy'
        )
        AS SELECT * FROM source_data
    """)
    print("Iceberg table created successfully!")
    print(f"  Table: {full_table_name}")
    print(f"  Location: {OUTPUT_PATH}")
except Exception as e:
    print(f"Error creating Iceberg table: {e}")
    print("Attempting Parquet fallback...")
    df.write \
        .format("parquet") \
        .mode("overwrite") \
        .option("compression", "snappy") \
        .save(f"{OUTPUT_PATH}/data/")
    print(f"Parquet written to: {OUTPUT_PATH}/data/")
    raise

job.commit()

