from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parents[3]))
from app.ui.components.data_loader import get_all_runs, get_doc_label_map, load_risk_signals

st.set_page_config(page_title="Risk Identification", layout="wide")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@400;600;700&family=Varela+Round&display=swap');
html, body, [class*="css"]  { font-family: 'Nunito Sans', sans-serif; }
h1, h2, h3 { font-family: 'Varela Round', sans-serif; }
.card {
    background: #FFFFFF;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(99,102,241,0.08);
    transition: all 200ms ease;
}
.card:hover {
    box-shadow: 0 6px 14px rgba(99,102,241,0.14);
    transform: translateY(-1px);
}
.kpi-box {
    padding: 18px 12px;
    border-radius: 10px;
    border: 1px solid #E5E7EB;
    border-left-width: 4px;
    cursor: pointer;
}
.kpi-total { border-left-color: #6366F1; }
.kpi-high { border-left-color: #DC2626; }
.kpi-medium { border-left-color: #D97706; }
.kpi-low { border-left-color: #16A34A; }
.kpi-active { border-color: #6366F1; background: #EEF2FF; }
.kpi-number { font-size: 2rem; font-weight: 700; }
.kpi-number-high { color: #DC2626; }
.kpi-number-medium { color: #D97706; }
.kpi-number-low { color: #16A34A; }
.kpi-label { font-size: 0.8rem; letter-spacing: 0.08em; text-transform: uppercase; color: #4B5563; }
.badge {padding:2px 10px;border-radius:999px;font-size:12px;font-weight:700;border:1px solid transparent;display:inline-block;}
.badge-High{background:#FEF2F2;color:#DC2626;border-color:#FECACA;}
.badge-Medium{background:#FFFBEB;color:#D97706;border-color:#FDE68A;}
.badge-Low{background:#F0FDF4;color:#16A34A;border-color:#BBF7D0;}
/* Overlay button sits on top of the KPI card with 0 opacity */
div[data-testid="element-container"]:has(.kpi-box) + div[data-testid="element-container"] button {
    margin-top: -96px;
    height: 96px;
    opacity: 0;
    cursor: pointer !important;
    position: relative;
    z-index: 10;
    background: transparent !important;
    border: none !important;
}
</style>
""",
    unsafe_allow_html=True,
)

st.title("Risk Identification")

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

doc_label_map = get_doc_label_map(run_key)
df["contract"] = df["document_id"].map(doc_label_map).fillna(df["document_id"])
contract_options = ["All"] + sorted(df["contract"].unique().tolist())
doc_filter = st.sidebar.selectbox("Contract", contract_options, key="changes_doc_filter")

kpi_df = df[df["contract"] == doc_filter] if doc_filter != "All" else df

if "changes_sev_filter" not in st.session_state:
    st.session_state["changes_sev_filter"] = "All"

active_sev = st.session_state["changes_sev_filter"]
total = len(kpi_df)
high_count = int((kpi_df["severity"] == "High").sum())
medium_count = int((kpi_df["severity"] == "Medium").sum())
low_count = int((kpi_df["severity"] == "Low").sum())

st.markdown("### Risk Signal Overview")
col_t, col_h, col_m, col_l = st.columns(4)

def kpi_html(css: str, count: int, label: str, active: bool, num_class: str = "") -> str:
    active_class = "kpi-active" if active else ""
    return (
        f"<div class='kpi-box card {css} {active_class}'>"
        f"<div class='kpi-number {num_class}'>{count}</div>"
        f"<div class='kpi-label'>{label}</div></div>"
    )

with col_t:
    st.markdown(kpi_html("kpi-total", total, "Total Flags", active_sev == "All"), unsafe_allow_html=True)
    if st.button(" ", key="kpi_all", use_container_width=True):
        st.session_state["changes_sev_filter"] = "All"

with col_h:
    st.markdown(kpi_html("kpi-high", high_count, "Critical", active_sev == "High", "kpi-number-high"), unsafe_allow_html=True)
    if st.button(" ", key="kpi_high", use_container_width=True):
        st.session_state["changes_sev_filter"] = "High"

with col_m:
    st.markdown(kpi_html("kpi-medium", medium_count, "Medium", active_sev == "Medium", "kpi-number-medium"), unsafe_allow_html=True)
    if st.button(" ", key="kpi_medium", use_container_width=True):
        st.session_state["changes_sev_filter"] = "Medium"

with col_l:
    st.markdown(kpi_html("kpi-low", low_count, "Low", active_sev == "Low", "kpi-number-low"), unsafe_allow_html=True)
    if st.button(" ", key="kpi_low", use_container_width=True):
        st.session_state["changes_sev_filter"] = "Low"

filtered = kpi_df.copy()
if active_sev != "All":
    filtered = filtered[filtered["severity"] == active_sev]

st.caption(f"Active severity filter: **{active_sev}** · Showing **{len(filtered)}** of **{total}** signals")
st.divider()

if filtered.empty:
    st.info("No signals for the selected filters.")
    st.stop()

for idx, row in filtered.reset_index(drop=True).iterrows():
    sev = row.get("severity", "Low")
    field = row.get("field_triggered", "Unknown field")
    msg = row.get("message", "")
    label = f"{idx+1}. {row.get('contract', 'Contract')} · {field} · {sev}"
    with st.expander(label):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**Triggering Rule**")
            st.write(f"`{row.get('rule_id', 'N/A')}`")
            st.write(msg or "No rule explanation available.")
        with c2:
            st.markdown("**Evidence Text**")
            st.write(row.get("evidence", "No evidence captured."))
        with c3:
            st.markdown("**Severity Rationale**")
            rule_inputs = row.get("rule_inputs")
            rationale = None
            if isinstance(rule_inputs, dict):
                rationale = ", ".join(f"{k}: {v}" for k, v in rule_inputs.items())
            elif isinstance(rule_inputs, str) and rule_inputs.strip():
                try:
                    parsed = json.loads(rule_inputs)
                    if isinstance(parsed, dict):
                        rationale = ", ".join(f"{k}: {v}" for k, v in parsed.items())
                except json.JSONDecodeError:
                    rationale = rule_inputs
            if rationale:
                st.write(rationale)
            else:
                conf = row.get("confidence")
                if conf is not None:
                    st.write(f"Severity {sev} assigned with confidence: {float(conf):.0%}")
                else:
                    st.write(f"Severity level marked as {sev} based on rule trigger output.")
            st.markdown(f"<span class='badge badge-{sev}'>{sev}</span>", unsafe_allow_html=True)
