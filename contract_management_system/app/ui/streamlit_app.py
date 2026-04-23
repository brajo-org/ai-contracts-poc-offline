from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="Contract Intelligence",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Contract Intelligence POC")

st.markdown("""
Use the sidebar to navigate between pages.

| Page | Purpose |
|---|---|
| **Contract Changes** | Triage all risk signals with stoplight filtering by severity |
| **Risk Assessment** | Executive summary and per-contract risk breakdown |
| **Redlining** | Review AI-suggested edits and author custom changes |
""")

st.info("Select a page from the sidebar to begin.")
