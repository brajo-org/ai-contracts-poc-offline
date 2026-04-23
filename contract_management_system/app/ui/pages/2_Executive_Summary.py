from __future__ import annotations

from datetime import datetime
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).parents[3]))
from app.ui.components.data_loader import get_all_runs, get_doc_label_map, load_intake_manifest, load_risk_signals

st.set_page_config(page_title="Executive Summary", layout="wide")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@400;600;700&family=Varela+Round&display=swap');
html, body, [class*="css"]  { font-family: 'Nunito Sans', sans-serif; }
h1, h2, h3 { font-family: 'Varela Round', sans-serif; }
.card {background:#FFFFFF;border-radius:10px;box-shadow:0 2px 8px rgba(99,102,241,0.08);padding:14px 18px;}
.meta-strip{background:#EEF2FF;border-radius:10px;padding:10px 14px;border:1px solid #C7D2FE;font-size:0.95rem;}
.badge{padding:2px 10px;border-radius:999px;font-size:12px;font-weight:700;border:1px solid transparent;display:inline-block;}
.badge-High{background:#FEF2F2;color:#DC2626;border-color:#FECACA;}
.badge-Medium{background:#FFFBEB;color:#D97706;border-color:#FDE68A;}
.badge-Low{background:#F0FDF4;color:#16A34A;border-color:#BBF7D0;}
</style>
""",
    unsafe_allow_html=True,
)

st.title("Executive Summary")

runs = get_all_runs()
if not runs:
    st.error("No runs found. Run the pipeline first.")
    st.stop()

selected_run = st.sidebar.selectbox("Run", runs, format_func=lambda p: p.name)
run_key = str(selected_run)

manifest = load_intake_manifest(run_key)
df = load_risk_signals(run_key)

if df.empty:
    st.info("No risk signals found for this run.")
    st.stop()

doc_label_map = get_doc_label_map(run_key)
df["contract"] = df["document_id"].map(doc_label_map).fillna(df["document_id"])
contract_options = ["All"] + sorted(df["contract"].unique().tolist())
selected_contract = st.sidebar.selectbox("Contract", contract_options, key="summary_doc_filter")

started_fmt = "Unknown"
try:
    started = datetime.strptime(Path(run_key).name, "RUN_%Y%m%d_%H%M%S")
    started_fmt = started.strftime("%Y-%m-%d %H:%M")
except ValueError:
    pass

st.markdown(
    f"<div class='meta-strip'><b>Run:</b> {Path(run_key).name} &nbsp;|&nbsp; "
    f"<b>Started:</b> {started_fmt} &nbsp;|&nbsp; "
    f"<b>Documents:</b> {len(manifest) if not manifest.empty else 0}</div>",
    unsafe_allow_html=True,
)
st.write("")

def severity_pie(input_df: pd.DataFrame, key: str):
    sev_counts = (
        input_df["severity"].value_counts().reindex(["High", "Medium", "Low"], fill_value=0)
        .rename_axis("Severity").reset_index(name="Count")
    )
    fig = px.pie(
        sev_counts,
        names="Severity",
        values="Count",
        color="Severity",
        color_discrete_map={"High": "#DC2626", "Medium": "#D97706", "Low": "#16A34A"},
        hole=0.35,
    )
    fig.update_layout(margin=dict(l=10, r=10, t=30, b=10), height=320)
    st.plotly_chart(fig, use_container_width=True, key=key)

if selected_contract == "All":
    docs_processed = len(manifest) if not manifest.empty else df["document_id"].nunique()
    total_signals = len(df)
    high = int((df["severity"] == "High").sum())
    medium = int((df["severity"] == "Medium").sum())

    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(f"<div class='card'><b>Docs Processed</b><br><span style='font-size:2rem;font-weight:700'>{docs_processed}</span></div>", unsafe_allow_html=True)
    m2.markdown(f"<div class='card'><b>Total Signals</b><br><span style='font-size:2rem;font-weight:700'>{total_signals}</span></div>", unsafe_allow_html=True)
    m3.markdown(f"<div class='card'><b>Critical Count</b><br><span style='font-size:2rem;font-weight:700;color:#DC2626'>{high}</span></div>", unsafe_allow_html=True)
    m4.markdown(f"<div class='card'><b>Medium Count</b><br><span style='font-size:2rem;font-weight:700;color:#D97706'>{medium}</span></div>", unsafe_allow_html=True)

    st.subheader("Severity Distribution")
    severity_pie(df, "all_contracts_pie")

    st.subheader("Per-Contract Summary")
    rows = []
    for contract, part in df.groupby("contract"):
        rows.append(
            {
                "Contract": contract,
                "High": int((part["severity"] == "High").sum()),
                "Medium": int((part["severity"] == "Medium").sum()),
                "Low": int((part["severity"] == "Low").sum()),
            }
        )
    table = pd.DataFrame(rows).sort_values(["High", "Medium", "Low"], ascending=[False, False, False])
    st.dataframe(table, use_container_width=True, hide_index=True)

    st.markdown("<div class='card'><b>Tyson AI Agent Analysis</b><br>Placeholder for narrative summary and recommended legal review sequence.</div>", unsafe_allow_html=True)
else:
    cdf = df[df["contract"] == selected_contract].copy()
    if cdf.empty:
        st.info("No risk signals found for this contract.")
        st.stop()

    overall = "Low"
    if (cdf["severity"] == "High").any():
        overall = "High"
    elif (cdf["severity"] == "Medium").any():
        overall = "Medium"

    st.markdown(
        f"<div class='card'><h3 style='margin:0'>{selected_contract}</h3>"
        f"<div style='margin-top:8px'>Overall Risk: <span class='badge badge-{overall}'>{overall}</span></div></div>",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Critical", int((cdf["severity"] == "High").sum()))
    c2.metric("Medium", int((cdf["severity"] == "Medium").sum()))
    c3.metric("Low", int((cdf["severity"] == "Low").sum()))

    st.subheader("Severity Split")
    severity_pie(cdf, "single_contract_pie")

    st.subheader("Top Risk Items")
    top = cdf[cdf["severity"] == "High"].head(3)
    if top.empty:
        st.info("No critical items for this contract.")
    else:
        for _, row in top.iterrows():
            st.markdown(
                f"<div class='card'><b>{row.get('field_triggered', 'Unknown field')}</b><br>{row.get('message', '')}</div>",
                unsafe_allow_html=True,
            )

    st.subheader("Full Signal Table")
    out = cdf[["rule_id", "severity", "field_triggered", "message", "evidence"]].rename(
        columns={
            "rule_id": "Rule",
            "severity": "Severity",
            "field_triggered": "Field",
            "message": "Issue",
            "evidence": "Evidence",
        }
    )
    st.dataframe(out, use_container_width=True, hide_index=True)

    st.markdown("<div class='card'><b>Tyson AI Agent Analysis</b><br>Placeholder for contract-level analysis and mitigation strategy.</div>", unsafe_allow_html=True)
