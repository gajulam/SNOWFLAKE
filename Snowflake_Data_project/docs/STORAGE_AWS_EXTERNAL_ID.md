# STORAGE_AWS_EXTERNAL_ID — What It Is and Where to Get It

## Summary

`STORAGE_AWS_EXTERNAL_ID` is **created by Snowflake** when you create a Storage Integration. You do **not** create or choose this value yourself. It is used in AWS IAM so that only your Snowflake account can assume your IAM role.

---

## Where It Comes From

1. **Snowflake creates it** when you run:
   ```sql
   CREATE STORAGE INTEGRATION s3_iceberg_integration
     TYPE = EXTERNAL_STAGE
     STORAGE_PROVIDER = 'S3'
     ENABLED = TRUE
     STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::YOUR_ACCOUNT:role/YourSnowflakeRole'
     STORAGE_ALLOWED_LOCATIONS = ('s3://your-bucket/your-path/');
   ```

2. **You retrieve it** from Snowflake:
   ```sql
   DESC INTEGRATION s3_iceberg_integration;
   -- or
   SHOW INTEGRATIONS LIKE 's3_iceberg_integration';
   ```

3. **Output** will include something like:
   ```
   property              | value
   ----------------------|--------------------------------------------------
   STORAGE_AWS_IAM_USER_ARN | arn:aws:iam::123456789012:user/snowflake-...
   STORAGE_AWS_EXTERNAL_ID  | EA36930_SFCRole=2_0IFVrXd60z+ohiZOXDakcrjIO+E=
   ```

---

## Why It Exists (Security)

- **External ID** is an AWS feature for cross-account or third-party access.
- Snowflake uses it so that **only your Snowflake account** can assume your IAM role.
- Someone who knows your role ARN but not this external ID cannot assume the role.
- Each Snowflake Storage Integration gets its own external ID.

---

## Correct Setup Order

| Step | Where | Action |
|------|--------|--------|
| 1 | Snowflake | Create Storage Integration (provide `STORAGE_AWS_ROLE_ARN`, `STORAGE_ALLOWED_LOCATIONS`) |
| 2 | Snowflake | Run `DESC INTEGRATION <name>` and note `STORAGE_AWS_EXTERNAL_ID` and `STORAGE_AWS_IAM_USER_ARN` |
| 3 | AWS IAM | Create or edit the IAM role your Snowflake integration uses |
| 4 | AWS IAM | Add a **Trust Policy** that allows Snowflake to assume the role using the values from step 2 |

---

## AWS IAM Trust Policy (Example)

Use the values from `DESC INTEGRATION`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:user/snowflake-xxxxx"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "EA36930_SFCRole=2_0IFVrXd60z+ohiZOXDakcrjIO+E="
        }
      }
    }
  ]
}
```

Replace:
- `arn:aws:iam::123456789012:user/snowflake-xxxxx` with your **STORAGE_AWS_IAM_USER_ARN**
- `EA36930_SFCRole=2_...` with your **STORAGE_AWS_EXTERNAL_ID**

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using an invented ID | Use only the value from `DESC INTEGRATION` |
| Hardcoding a generic ID | Each integration has its own external ID; copy it from Snowflake |
| Using an old ID after recreating the integration | Run `DESC INTEGRATION` again; the ID changes when you recreate the integration |
| Mismatched values in trust policy | `Principal.AWS` must be `STORAGE_AWS_IAM_USER_ARN`; `sts:ExternalId` must be `STORAGE_AWS_EXTERNAL_ID` |

---

## What About the CREATE STORAGE INTEGRATION Syntax?

You **do not** pass `STORAGE_AWS_EXTERNAL_ID` into `CREATE STORAGE INTEGRATION`. Snowflake generates it. In some documentation or older SQL you might see it listed; that usually refers to the value you **output** from the integration, not something you input.

Correct `CREATE STORAGE INTEGRATION` syntax:

```sql
CREATE STORAGE INTEGRATION s3_iceberg_integration
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = 'S3'
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::211125758501:role/SnowflakeS3AccessRole'
  STORAGE_ALLOWED_LOCATIONS = ('s3://snowflake-bronze-delta-mahi/root/crime_iceberg/');
```

Then run `DESC INTEGRATION s3_iceberg_integration` to get `STORAGE_AWS_EXTERNAL_ID` for your AWS trust policy.
