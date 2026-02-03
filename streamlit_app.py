# Crime Data Dashboard for Police & Stations
# Table: SNOWFLAKE_LEARNING_DB.PUBLIC.GOLD_CRIMES_BY_DISTRICT
# Schema: DISTRICT, INCIDENT_COUNT, ARREST_COUNT, DOMESTIC_COUNT,
#         TOP_PRIMARY_TYPE, ARREST_RATE_PCT, GOLD_LOADED_AT
"""
CREATE OR REPLACE TABLE SNOWFLAKE_LEARNING_DB.PUBLIC.GOLD_CRIMES_BY_DISTRICT (
    DISTRICT NUMBER(38,0),
    INCIDENT_COUNT NUMBER(38,0),
    ARREST_COUNT NUMBER(38,0),
    DOMESTIC_COUNT NUMBER(38,0),
    TOP_PRIMARY_TYPE VARCHAR(16777216),
    ARREST_RATE_PCT NUMBER(10,2),
    GOLD_LOADED_AT TIMESTAMP_NTZ(9) DEFAULT CURRENT_TIMESTAMP()
);
"""
import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Crime Dashboard", page_icon="🛡️", layout="wide")
st.title("Crime Dashboard — Police & Station Intelligence")
st.caption("District-level crime aggregates (Gold layer).")

# Connect
session = get_active_session()

TABLE = "SNOWFLAKE_LEARNING_DB.PUBLIC.GOLD_CRIMES_BY_DISTRICT"

# Muted green (low) to red (high) colorscale
COLORSCALE = [[0, "#b8e0b8"], [0.5, "#fff4b8"], [1, "#e8a090"]]

# ---- Filters (sidebar) ----
st.sidebar.header("Filters")

# District filter
try:
    dist_row = session.sql(f"SELECT DISTINCT DISTRICT FROM {TABLE} WHERE DISTRICT IS NOT NULL ORDER BY DISTRICT").collect()
    all_districts = [r["DISTRICT"] for r in dist_row]
except Exception:
    all_districts = []
district_sel = st.sidebar.multiselect("District", options=all_districts, default=[], help="Leave empty for all districts")

# Top primary type filter
try:
    type_row = session.sql(f"SELECT DISTINCT TOP_PRIMARY_TYPE FROM {TABLE} WHERE TOP_PRIMARY_TYPE IS NOT NULL ORDER BY TOP_PRIMARY_TYPE").collect()
    all_types = [r["TOP_PRIMARY_TYPE"] for r in type_row]
except Exception:
    all_types = []
type_sel = st.sidebar.multiselect("Top crime type", options=all_types, default=[], help="Filter by dominant crime type in district")

# Min incident count
min_incidents = st.sidebar.number_input("Min incident count", min_value=0, value=0, help="Hide districts below this threshold")

# ---- Build WHERE ----
def build_where():
    parts = ["1=1"]
    if district_sel:
        parts.append(f"DISTRICT IN ({','.join(str(d) for d in district_sel)})")
    if type_sel:
        types_sql = ",".join([f"'{t}'" for t in type_sel])
        parts.append(f"TOP_PRIMARY_TYPE IN ({types_sql})")
    if min_incidents > 0:
        parts.append(f"INCIDENT_COUNT >= {min_incidents}")
    return " AND ".join(parts)

where_clause = build_where()

# ---- KPIs ----
st.subheader("Summary")

kpi_sql = f"""
    SELECT
        COALESCE(SUM(INCIDENT_COUNT), 0) AS total_incidents,
        COALESCE(SUM(ARREST_COUNT), 0) AS total_arrests,
        COALESCE(SUM(DOMESTIC_COUNT), 0) AS total_domestic,
        COUNT(DISTINCT DISTRICT) AS district_count
    FROM {TABLE}
    WHERE {where_clause}
"""
try:
    kpi = session.sql(kpi_sql).to_pandas().iloc[0]
    total = int(kpi["TOTAL_INCIDENTS"]) if pd.notna(kpi["TOTAL_INCIDENTS"]) else 0
    arrests = int(kpi["TOTAL_ARRESTS"]) if pd.notna(kpi["TOTAL_ARRESTS"]) else 0
    domestic = int(kpi["TOTAL_DOMESTIC"]) if pd.notna(kpi["TOTAL_DOMESTIC"]) else 0
    districts = int(kpi["DISTRICT_COUNT"]) if pd.notna(kpi["DISTRICT_COUNT"]) else 0
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total incidents", f"{total:,}")
    c2.metric("Total arrests", f"{arrests:,}")
    c3.metric("Domestic incidents", f"{domestic:,}")
    c4.metric("Districts", f"{districts}")
    if total == 0:
        st.info("No data for selected filters. Clear filters or lower min incident count.")
except Exception as e:
    st.error(f"Could not load summary: {e}")

# ---- Charts ----
st.subheader("Incidents by district")
dist_sql = f"""
    SELECT DISTRICT, INCIDENT_COUNT
    FROM {TABLE}
    WHERE {where_clause}
    ORDER BY INCIDENT_COUNT DESC
"""
try:
    dist_df = session.sql(dist_sql).to_pandas()
    if len(dist_df) > 0:
        dist_df["DISTRICT"] = dist_df["DISTRICT"].astype(str)
        fig = px.bar(dist_df, x="DISTRICT", y="INCIDENT_COUNT", color="INCIDENT_COUNT",
                     color_continuous_scale=COLORSCALE, labels={"INCIDENT_COUNT": "Incidents"})
        fig.update_layout(showlegend=False, coloraxis_showscale=True, margin=dict(t=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for selected filters.")
except Exception:
    st.info("No district data for selected filters.")

st.subheader("Arrest rate by district (%)")
arrest_sql = f"""
    SELECT DISTRICT, ARREST_RATE_PCT
    FROM {TABLE}
    WHERE {where_clause} AND ARREST_RATE_PCT IS NOT NULL
    ORDER BY ARREST_RATE_PCT DESC
"""
try:
    arrest_df = session.sql(arrest_sql).to_pandas()
    if len(arrest_df) > 0:
        arrest_df["DISTRICT"] = arrest_df["DISTRICT"].astype(str)
        fig = px.bar(arrest_df, x="DISTRICT", y="ARREST_RATE_PCT", color="ARREST_RATE_PCT",
                     color_continuous_scale=COLORSCALE, labels={"ARREST_RATE_PCT": "Arrest rate %"})
        fig.update_layout(showlegend=False, coloraxis_showscale=True, margin=dict(t=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No arrest rate data for selected filters.")
except Exception:
    st.info("No arrest rate data for selected filters.")

st.subheader("Top crime type by district")
type_sql = f"""
    SELECT TOP_PRIMARY_TYPE, COUNT(*) AS district_count, SUM(INCIDENT_COUNT) AS total_incidents
    FROM {TABLE}
    WHERE {where_clause} AND TOP_PRIMARY_TYPE IS NOT NULL
    GROUP BY TOP_PRIMARY_TYPE
    ORDER BY total_incidents DESC
    LIMIT 15
"""
try:
    type_df = session.sql(type_sql).to_pandas()
    if len(type_df) > 0:
        fig = px.bar(type_df, x="TOP_PRIMARY_TYPE", y="TOTAL_INCIDENTS", color="TOTAL_INCIDENTS",
                     color_continuous_scale=COLORSCALE, labels={"TOTAL_INCIDENTS": "Incidents", "TOP_PRIMARY_TYPE": "Crime type"})
        fig.update_layout(showlegend=False, coloraxis_showscale=True, margin=dict(t=20), xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for selected filters.")
except Exception:
    st.info("No crime type data for selected filters.")

# ---- Forecast (if available) ----
st.subheader("Next week forecast")
try:
    fc = session.sql("""
        SELECT DISTRICT, FORECAST_WEEK, ROUND(PREDICTED_CRIMES, 1) AS PREDICTED_CRIMES
        FROM SNOWFLAKE_LEARNING_DB.PUBLIC.CRIME_FORECASTS_NEXT_WEEK
        ORDER BY PREDICTED_CRIMES DESC
    """).to_pandas()
    if len(fc) > 0:
        st.dataframe(fc, use_container_width=True, hide_index=True)
    else:
        st.caption("Run the notebook to populate forecasts.")
except Exception:
    st.caption("Run the notebook to populate CRIME_FORECASTS_NEXT_WEEK.")

# ---- Data table ----
st.subheader("District details")
detail_sql = f"""
    SELECT DISTRICT, INCIDENT_COUNT, ARREST_COUNT, DOMESTIC_COUNT, TOP_PRIMARY_TYPE, ARREST_RATE_PCT
    FROM {TABLE}
    WHERE {where_clause}
    ORDER BY INCIDENT_COUNT DESC
"""
try:
    detail_df = session.sql(detail_sql).to_pandas()
    st.dataframe(detail_df, use_container_width=True, hide_index=True)
except Exception as e:
    st.error(f"Could not load data: {e}")
