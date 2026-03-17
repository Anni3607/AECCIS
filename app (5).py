# =========================================================
# AECCIS STREAMLIT APP
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="AECCIS Dashboard", layout="wide")

# -------------------------------
# LOAD DATA
# -------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("data/cloud_cost_final_output.csv")

df = load_data()

# -------------------------------
# TITLE
# -------------------------------
st.title("💡 AECCIS: Cloud Cost Intelligence Dashboard")

# -------------------------------
# SIDEBAR FILTERS
# -------------------------------
st.sidebar.header("Filters")

services = st.sidebar.multiselect(
    "Select Services",
    options=df['service'].unique(),
    default=df['service'].unique()
)

ais_filter = st.sidebar.slider(
    "Minimum AIS Score",
    0, 100, 0
)

filtered_df = df[
    (df['service'].isin(services)) &
    (df['ais_score'] >= ais_filter)
]

# -------------------------------
# METRICS
# -------------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Records", len(filtered_df))
col2.metric("Anomalies", filtered_df['anomaly_flag'].sum())
col3.metric("Avg AIS", round(filtered_df['ais_score'].mean(), 2))
col4.metric("Max AIS", round(filtered_df['ais_score'].max(), 2))

# -------------------------------
# COST TREND
# -------------------------------
st.subheader("📈 Cost Trend")

fig = px.line(
    filtered_df,
    x="timestamp",
    y="cost",
    color="service",
    title="Cost Over Time"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# ANOMALY HIGHLIGHT
# -------------------------------
st.subheader("🚨 Anomaly Detection")

anom_df = filtered_df[filtered_df['anomaly_flag'] == 1]

fig2 = px.scatter(
    filtered_df,
    x="timestamp",
    y="cost",
    color="anomaly_flag",
    title="Anomalies Highlighted"
)

st.plotly_chart(fig2, use_container_width=True)

# -------------------------------
# AIS DISTRIBUTION
# -------------------------------
st.subheader("📊 AIS Score Distribution")

fig3 = px.histogram(
    filtered_df,
    x="ais_score",
    nbins=30,
    title="AIS Score Distribution"
)

st.plotly_chart(fig3, use_container_width=True)

# -------------------------------
# ANOMALY TYPE BREAKDOWN
# -------------------------------
st.subheader("🧠 Anomaly Type Breakdown")

fig4 = px.pie(
    anom_df,
    names="anomaly_type",
    title="Anomaly Types"
)

st.plotly_chart(fig4, use_container_width=True)

# -------------------------------
# ROOT CAUSE ANALYSIS
# -------------------------------
st.subheader("🔍 Root Cause Analysis")

fig5 = px.bar(
    anom_df['root_cause'].value_counts().reset_index(),
    x="count",
    y="index",
    orientation='h',
    title="Root Cause Frequency"
)

st.plotly_chart(fig5, use_container_width=True)

# -------------------------------
# TOP ANOMALIES TABLE
# -------------------------------
st.subheader("🔥 Top Anomalies")

top_n = st.slider("Select Top N", 5, 20, 10)

top_anomalies = anom_df.sort_values(
    by="ais_score", ascending=False
).head(top_n)

st.dataframe(top_anomalies[
    ['service', 'cost', 'ais_score', 'anomaly_type', 'root_cause', 'confidence']
])

# -------------------------------
# INTERACTIVE INSPECTOR
# -------------------------------
st.subheader("🔬 Anomaly Inspector")

selected_index = st.selectbox(
    "Select Row Index",
    anom_df.index
)

row = anom_df.loc[selected_index]

st.write("### Details")
st.json({
    "Service": row['service'],
    "Cost": float(row['cost']),
    "AIS Score": float(row['ais_score']),
    "Type": row['anomaly_type'],
    "Root Cause": row['root_cause'],
    "Confidence": float(row['confidence']),
    "Recommended Action": row['recommended_action']
})

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.markdown("AECCIS: Adaptive Explainable Cloud Cost Intelligence System")