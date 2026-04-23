from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parents[3]))
from app.ui.components.data_loader import (
    get_all_runs,
    get_doc_label_map,
    load_redlines,
    load_risk_signals,
)

st.set_page_config(page_title="Redlining", layout="wide")

st.markdown("""
<style>
.redline-card {
    background: #1E293B;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 12px;
    border-left: 4px solid #1E40AF;
}
.status-Accepted { color: #4ADE80; font-weight: 700; }
.status-Rejected { color: #F87171; font-weight: 700; }
.status-Edited   { color: #FBBF24; font-weight: 700; }
.status-Pending  { color: #94A3B8; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

st.title("Redlining")

# --- Sidebar: run + contract selectors ---
runs = get_all_runs()
if not runs:
    st.error("No runs found. Run the pipeline first.")
    st.stop()

selected_run = st.sidebar.selectbox("Run", runs, format_func=lambda p: p.name)
run_key = str(selected_run)

doc_label_map = get_doc_label_map(run_key)
label_to_doc  = {v: k for k, v in doc_label_map.items()}

redlines_df = load_redlines(run_key)
risk_df     = load_risk_signals(run_key)

# Enrich redlines with severity from risk signals
if not redlines_df.empty and not risk_df.empty:
    sev_map = risk_df.set_index("rule_id")["severity"].to_dict()
    redlines_df["severity"] = redlines_df["risk_id"].map(sev_map).fillna("Unknown")

all_labels = list(doc_label_map.values()) if doc_label_map else []
if not all_labels:
    all_labels = redlines_df["document_id"].unique().tolist() if not redlines_df.empty else []

selected_label = st.sidebar.selectbox("Contract", sorted(all_labels))
selected_doc   = label_to_doc.get(selected_label, selected_label)

# --- Main area ---
st.markdown(f"### {selected_label}")
st.caption(f"Document ID: `{selected_doc}`")

doc_redlines = redlines_df[redlines_df["document_id"] == selected_doc] if not redlines_df.empty else redlines_df

st.divider()

# --- Section A: AI Suggested Changes ---
st.subheader("AI Suggested Changes")

if doc_redlines.empty:
    st.info("No AI-suggested redlines for this contract.")
else:
    for i, row in doc_redlines.reset_index(drop=True).iterrows():
        decision_key    = f"rl_decision_{selected_doc}_{row['risk_id']}"
        edited_text_key = f"rl_edited_{selected_doc}_{row['risk_id']}"
        current_status  = st.session_state.get(decision_key, "Pending")

        sev = row.get("severity", "Unknown")
        sev_colors = {"High": "#DC2626", "Medium": "#D97706", "Low": "#16A34A"}
        sev_color  = sev_colors.get(sev, "#94A3B8")

        st.markdown(
            f"**{row['risk_id']}** &nbsp;|&nbsp; "
            f"<span style='color:{sev_color};font-weight:700'>{sev}</span> &nbsp;|&nbsp; "
            f"`{row.get('change_type', 'replace').upper()}`",
            unsafe_allow_html=True,
        )

        col_orig, col_prop = st.columns(2)
        with col_orig:
            st.markdown("**Original Text**")
            orig = row.get("original_text") or ""
            st.code(orig if orig.strip() else "(no original text — addition required)", language=None)
        with col_prop:
            st.markdown("**AI Proposed Change**")
            st.code(row.get("proposed_text", ""), language=None)

        st.caption(
            f"Rationale: {row.get('rationale', '')} &nbsp;|&nbsp; "
            f"Confidence: {row.get('confidence', 0):.0%}"
        )

        btn_col1, btn_col2, status_col = st.columns([1, 1, 5])
        with btn_col1:
            if st.button("✓ Accept", key=f"accept_{selected_doc}_{i}"):
                st.session_state[decision_key] = "Accepted"
                st.session_state.pop(edited_text_key, None)
                st.rerun()
        with btn_col2:
            if st.button("✗ Reject", key=f"reject_{selected_doc}_{i}"):
                st.session_state[decision_key] = "Rejected"
                st.session_state.pop(edited_text_key, None)
                st.rerun()
        with status_col:
            status_color = {"Accepted": "#4ADE80", "Rejected": "#F87171",
                            "Edited": "#FBBF24", "Pending": "#94A3B8"}.get(current_status, "#94A3B8")
            st.markdown(
                f"Status: <span style='color:{status_color};font-weight:700'>{current_status}</span>",
                unsafe_allow_html=True,
            )

        if current_status not in ("Accepted", "Rejected"):
            edited = st.text_area(
                "Edit proposed text (optional)",
                value=st.session_state.get(edited_text_key, row.get("proposed_text", "")),
                key=f"edit_area_{selected_doc}_{i}",
                height=80,
            )
            if edited != row.get("proposed_text", ""):
                st.session_state[decision_key]    = "Edited"
                st.session_state[edited_text_key] = edited

        st.divider()

# --- Section B: Custom Changes ---
st.subheader("Add Custom Change")

custom_key = f"rl_custom_{selected_doc}"
if custom_key not in st.session_state:
    st.session_state[custom_key] = []

with st.form(key=f"custom_form_{selected_doc}", clear_on_submit=True):
    clause_ref  = st.text_input("Clause / Section Reference (e.g. Section 4.2)")
    custom_text = st.text_area("Proposed Change Text", height=100)
    submitted   = st.form_submit_button("Add Change")
    if submitted and custom_text.strip():
        st.session_state[custom_key].append({
            "clause_ref": clause_ref,
            "proposed_text": custom_text,
            "source": "user",
        })
        st.success("Custom change added.")

if st.session_state[custom_key]:
    st.markdown("**Custom Changes Added:**")
    for idx, c in enumerate(st.session_state[custom_key]):
        col_c, col_del = st.columns([10, 1])
        with col_c:
            ref = f"[{c['clause_ref']}] " if c['clause_ref'] else ""
            st.markdown(f"- {ref}{c['proposed_text']}")
        with col_del:
            if st.button("✕", key=f"del_custom_{selected_doc}_{idx}"):
                st.session_state[custom_key].pop(idx)
                st.rerun()

st.divider()

# --- Section C: Export Decisions ---
st.subheader("Export Decisions")

def collect_decisions() -> list[dict]:
    out = []
    if doc_redlines.empty:
        return out
    for _, row in doc_redlines.reset_index(drop=True).iterrows():
        decision_key    = f"rl_decision_{selected_doc}_{row['risk_id']}"
        edited_text_key = f"rl_edited_{selected_doc}_{row['risk_id']}"
        decision = st.session_state.get(decision_key, "Pending")
        if decision == "Accepted":
            final_text = row.get("proposed_text", "")
        elif decision == "Edited":
            final_text = st.session_state.get(edited_text_key, row.get("proposed_text", ""))
        else:
            final_text = None
        out.append({
            "document_id": selected_doc,
            "risk_id":     row["risk_id"],
            "decision":    decision,
            "final_text":  final_text,
            "source":      "ai",
        })
    for c in st.session_state.get(custom_key, []):
        out.append({
            "document_id":  selected_doc,
            "clause_ref":   c["clause_ref"],
            "final_text":   c["proposed_text"],
            "decision":     "Accepted",
            "source":       "user",
        })
    return out

decisions = collect_decisions()
st.download_button(
    label="Download decisions.json",
    data=json.dumps(decisions, indent=2),
    file_name=f"decisions_{selected_doc}.json",
    mime="application/json",
    disabled=not decisions,
)
