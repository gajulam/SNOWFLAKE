# CI/CD Setup: GitHub → Snowflake

Edits pushed to GitHub automatically deploy to Snowflake.

## Deployed Artifacts

| File | Snowflake Object |
|------|------------------|
| `streamlit_app.py` | Streamlit app `CRIME_DASHBOARD` |
| `notebooks/ML_WEEKLY_PREDICTION.ipynb` | Notebook `ML_WEEKLY_PREDICTION` |

To deploy `script.ipynb` (when you add it), add an entity in `snowflake.yml` and a deploy step in the workflow.

## GitHub Secrets

Add these in **Settings → Secrets and variables → Actions**:

| Secret | Example | Description |
|--------|---------|-------------|
| `SNOWFLAKE_ACCOUNT` | `xy12345.us-east-2.aws` | Account identifier |
| `SNOWFLAKE_USER` | `myuser` | Username |
| `SNOWFLAKE_PASSWORD` | `••••••••` | Password |

## Configuration

- **Warehouse**: `snowflake.yml` uses `COMPUTE_WH`. Change it if your warehouse has another name.
- **Database/Schema**: Deploys to `SNOWFLAKE_LEARNING_DB.PUBLIC`.

## Flow

1. Edit `streamlit_app.py` or `notebooks/ML_WEEKLY_PREDICTION.ipynb` locally
2. Commit and push to `main` or `master`
3. GitHub Actions runs and deploys to Snowflake
4. Open the Streamlit app and notebook in Snowsight
