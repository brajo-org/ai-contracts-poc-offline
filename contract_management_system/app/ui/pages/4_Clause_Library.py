from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="Clause Library", layout="wide")

st.markdown(
    """
<style>
.card{background:#FFFFFF;border-radius:10px;box-shadow:0 2px 8px rgba(99,102,241,0.08);padding:16px;}
</style>
""",
    unsafe_allow_html=True,
)

st.title("Clause Library")
st.markdown("<div class='card'><b>Phase 1 Placeholder</b><br>Searchable clause library integration is planned for a future phase.</div>", unsafe_allow_html=True)
st.text_input("Search Clauses (coming soon)", disabled=True)
