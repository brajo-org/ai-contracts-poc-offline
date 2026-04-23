from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parents[3]))
from app.ui.components.data_loader import (
    get_all_runs,
    get_doc_label_map,
    load_risk_signals,
)

st.set_page_config(page_title="Contract Changes", layout="wide")

st.markdown("""
<style>
.kpi-box {
    border-radius: 10px;
    padding: 18px 10px;
    text-align: center;
    border: 2px solid transparent;
    transition: border 0.2s;
}
.kpi-total  { background: #1E293B; border-color: #334155; }
.kpi-high   { background: #7F1D1D; border-color: #DC2626; }
.kpi-medium { background: #78350F; border-color: #D97706; }
.kpi-low    { background: #14532D; border-color: #16A34A; }
.kpi-number { font-size: 2rem; font-weight: 700; }
.kpi-label  { font-size: 0.8rem; letter-spacing: 0.08em; text-transform: uppercase; opacity: 0.8; }
.badge-High   { background:#DC2626; color:white; padding:2px 8px; border-radius:4px; font-size:12px; font-weight:600; }
.badge-Medium { background:#D97706; color:white; padding:2px 8px; border-radius:4px; font-size:12px; font-weight:600; }
.badge-Low    { background:#16A34A; color:white; padding:2px 8px; border-radius:4px; font-size:12px; font-weight:600; }
</style>
""", unsafe_allow_html=True)

st.title("Contract Changes")

# --- Sidebar: run selector ---
runs = get_all_runs()
if not runs:
    st.error("No runs found. Run the pipeline first.")
    st.stop()

selected_run = st.sidebar.selectbox("Run", runs, format_func=lambda p: p.name)
run_key = str(selected_run)

df = load_risk_signals(run_key)

if df.empty:
    st.info("No risk signals found for this run.")
    st.stop()

# --- Stoplight KPI row ---
total = len(df)
high_count   = int((df["severity"] == "High").sum())
medium_count = int((df["severity"] == "Medium").sum())
low_count    = int((df["severity"] == "Low").sum())

st.markdown("### Risk Signal Overview")

if "changes_sev_filter" not in st.session_state:
    st.session_state["changes_sev_filter"] = "All"

col_t, col_h, col_m, col_l = st.columns(4)

with col_t:
    st.markdown(f"""
    <div class="kpi-box kpi-total">
        <div class="kpi-number">{total}</div>
        <div class="kpi-label">Total Changes</div>
    </div>""", unsafe_allow_html=True)
    if st.button("Show All", key="btn_all", use_container_width=True):
        st.session_state["changes_sev_filter"] = "All"

with col_h:
    st.markdown(f"""
    <div class="kpi-box kpi-high">
        <div class="kpi-number">{high_count}</div>
        <div class="kpi-label">Critical</div>
    </div>""", unsafe_allow_html=True)
    if st.button("Filter Critical", key="btn_high", use_container_width=True):
        st.session_state["changes_sev_filter"] = "High"

with col_m:
    st.markdown(f"""
    <div class="kpi-box kpi-medium">
        <div class="kpi-number">{medium_count}</div>
        <div class="kpi-label">Medium</div>
    </div>""", unsafe_allow_html=True)
    if st.button("Filter Medium", key="btn_med", use_container_width=True):
        st.session_state["changes_sev_filter"] = "Medium"

with col_l:
    st.markdown(f"""
    <div class="kpi-box kpi-low">
        <div class="kpi-number">{low_count}</div>
        <div class="kpi-label">Low</div>
    </div>""", unsafe_allow_html=True)
    if st.button("Filter Low", key="btn_low", use_container_width=True):
        st.session_state["changes_sev_filter"] = "Low"

st.divider()

# --- Filter bar ---
doc_label_map = get_doc_label_map(run_key)
df["contract"] = df["document_id"].map(doc_label_map).fillna(df["document_id"])

col_sev, col_doc = st.columns([1, 3])
active_sev = st.session_state["changes_sev_filter"]

with col_sev:
    st.markdown(f"**Severity filter:** `{active_sev}`")

with col_doc:
    doc_options = ["All"] + sorted(df["contract"].unique().tolist())
    doc_filter = st.selectbox("Filter by Contract", doc_options, key="changes_doc_filter")

# --- Apply filters ---
filtered = df.copy()
if active_sev != "All":
    filtered = filtered[filtered["severity"] == active_sev]
if doc_filter != "All":
    filtered = filtered[filtered["contract"] == doc_filter]

st.caption(f"Showing **{len(filtered)}** of **{total}** signals")

# --- Table ---
display_cols = ["contract", "rule_id", "severity", "field_triggered", "message", "evidence"]
available = [c for c in display_cols if c in filtered.columns]

st.dataframe(
    filtered[available].rename(columns={
        "contract": "Contract",
        "rule_id": "Rule",
        "severity": "Severity",
        "field_triggered": "Field",
        "message": "Issue",
        "evidence": "Evidence",
    }),
    use_container_width=True,
    hide_index=True,
)
