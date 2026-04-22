from __future__ import annotations

import json
from pathlib import Path

import streamlit as st


st.title("Offline Contract Management System")
base = Path("outputs/runs")
runs = sorted([p for p in base.glob("RUN_*") if p.is_dir()], reverse=True)

if not runs:
    st.info("No runs found.")
    st.stop()

selected = st.selectbox("Run", runs, format_func=lambda p: p.name)

st.subheader("Run Summary")
summary_path = selected / "run_summary.md"
if summary_path.exists():
    st.markdown(summary_path.read_text(encoding="utf-8"))

st.subheader("Risk Signals")
risk_path = selected / "risk_signals.jsonl"
if risk_path.exists():
    rows = [json.loads(line) for line in risk_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    st.dataframe(rows)

st.subheader("Artifacts")
for p in sorted(selected.iterdir()):
    st.write(p.name)
