from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parents[3]))
from app.ui.components.data_loader import (
    get_all_runs,
    get_doc_label_map,
    load_extractions,
    load_intake_manifest,
    load_risk_signals,
    load_run_summary,
)

st.set_page_config(page_title="Risk Assessment", layout="wide")

st.markdown("""
<style>
.metric-card {
    background: #1E293B;
    border-radius: 8px;
    padding: 14px 18px;
    border-left: 4px solid #1E40AF;
}
.sev-high   { color: #F87171; font-weight: 700; }
.sev-medium { color: #FBBF24; font-weight: 700; }
.sev-low    { color: #4ADE80; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

st.title("Risk Assessment")

# --- Sidebar: run selector ---
runs = get_all_runs()
if not runs:
    st.error("No runs found. Run the pipeline first.")
    st.stop()

selected_run = st.sidebar.selectbox("Run", runs, format_func=lambda p: p.name)
run_key = str(selected_run)

summary_text = load_run_summary(run_key)
df = load_risk_signals(run_key)
extractions = load_extractions(run_key)
doc_label_map = get_doc_label_map(run_key)

# --- Section A: Executive Summary ---
st.subheader("Executive Summary")

manifest = load_intake_manifest(run_key)
doc_count = len(manifest) if not manifest.empty else 0
total_signals = len(df)
high_count = int((df["severity"] == "High").sum()) if not df.empty else 0
med_count  = int((df["severity"] == "Medium").sum()) if not df.empty else 0
low_count  = int((df["severity"] == "Low").sum()) if not df.empty else 0

avg_confidence = None
if not extractions.empty and "confidence" in extractions.columns:
    avg_confidence = extractions["confidence"].mean()

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Documents Processed", doc_count)
m2.metric("Total Risk Signals", total_signals)
m3.metric("Critical (High)", high_count, delta=None)
m4.metric("Medium", med_count)
m5.metric("Low", low_count)

if avg_confidence is not None:
    st.caption(f"Average extraction confidence: **{avg_confidence:.0%}**")

with st.expander("Full Run Summary", expanded=True):
    st.markdown(summary_text)

st.divider()

# --- Section B: Severity Distribution ---
st.subheader("Severity Distribution")

if not df.empty:
    sev_counts = (
        df["severity"]
        .value_counts()
        .reindex(["High", "Medium", "Low"], fill_value=0)
        .rename_axis("Severity")
        .reset_index(name="Count")
    )
    st.bar_chart(sev_counts.set_index("Severity"))
else:
    st.info("No risk signals to chart.")

st.divider()

# --- Section C: Risk Breakdown by Contract ---
st.subheader("Risk Breakdown by Contract")

if df.empty:
    st.info("No risk signals found for this run.")
    st.stop()

df["contract"] = df["document_id"].map(doc_label_map).fillna(df["document_id"])

doc_summary = (
    df.groupby(["document_id", "contract", "severity"])
    .size()
    .unstack(fill_value=0)
    .reset_index()
)
for sev in ["High", "Medium", "Low"]:
    if sev not in doc_summary.columns:
        doc_summary[sev] = 0

doc_summary = doc_summary.sort_values("High", ascending=False)

for _, row in doc_summary.iterrows():
    label = f"{row['contract']} — " \
            f"🔴 {row['High']} Critical  🟡 {row['Medium']} Medium  🟢 {row['Low']} Low"
    with st.expander(label):
        doc_df = df[df["document_id"] == row["document_id"]][
            ["rule_id", "severity", "field_triggered", "message"]
        ].rename(columns={
            "rule_id": "Rule",
            "severity": "Severity",
            "field_triggered": "Field",
            "message": "Issue",
        })
        st.dataframe(doc_df, use_container_width=True, hide_index=True)
