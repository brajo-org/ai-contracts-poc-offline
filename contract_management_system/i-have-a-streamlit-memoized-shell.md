# Contract Management UI Redesign — Codex Build Plan

## Context

The POC's Streamlit frontend is a single 37-line file (`app/ui/streamlit_app.py`) that renders a raw dataframe and a markdown summary. This undersells the system's capabilities — it runs a full pipeline (intake → normalize → segment → extract → risk rules → redline generation) across 17 contracts but shows none of that structure in the UI.

The goal is to expand to three focused pages that each surface a distinct capability: interactive risk triage, executive risk assessment, and clause-level redlining with user interaction.

---

## Project Root

```
C:\Users\jonesbrade\ai-contracts-poc-offline\contract_management_system\
```

Run Streamlit from this directory with: `streamlit run app/ui/streamlit_app.py`

---

## Architecture Change: Single File → Multi-Page

**Before:** `app/ui/streamlit_app.py` (37 lines, single page)

**After:**
```
app/ui/
├── streamlit_app.py              ← REPLACE: becomes homepage/nav shell
├── components/
│   └── data_loader.py            ← CREATE: shared data access layer
└── pages/
    ├── 1_Contract_Changes.py     ← CREATE: enhanced existing functionality
    ├── 2_Risk_Assessment.py      ← CREATE: new page
    └── 3_Redlining.py            ← CREATE: new page
```

Streamlit automatically creates sidebar navigation from the `pages/` directory. No routing code needed.

Also create: `.streamlit/config.toml` for custom theme.

---

## Step 1 — Shared Data Loader

**File:** `app/ui/components/data_loader.py`

Create a module with these functions (use `@st.cache_data` on all of them):

```python
def get_all_runs(base_path="outputs/runs") -> list[Path]
    # Returns sorted list of RUN_* directories, newest first

def load_risk_signals(run_dir: Path) -> pd.DataFrame
    # Reads risk_signals.jsonl, adds severity_order column:
    # High=1, Medium=2, Low=3
    # Returns sorted by severity_order then document_id

def load_redlines(run_dir: Path) -> pd.DataFrame
    # Reads redlines.jsonl
    # Joins risk_id → severity from risk_signals for the same run

def load_run_summary(run_dir: Path) -> str
    # Reads run_summary.md as string

def load_intake_manifest(run_dir: Path) -> pd.DataFrame
    # Reads intake_manifest.json (list of intake records)
    # Returns DataFrame with columns: document_id, source_filename

def load_extractions(run_dir: Path) -> pd.DataFrame
    # Reads extractions.jsonl

def get_doc_label_map(run_dir: Path) -> dict[str, str]
    # Returns {document_id: source_filename} from intake_manifest
    # Used to show readable filenames instead of DOC-XXXX codes
```

**Data shapes to expect:**

risk_signals.jsonl record:
```json
{"run_id": "...", "document_id": "DOC-0001", "rule_id": "R001",
 "severity": "High", "field_triggered": "ExpirationDate",
 "message": "Missing expiration date", "evidence": "NOT_FOUND",
 "section_id": null, "clause_id": null,
 "rule_inputs": {"field_value": null, "confidence": 0.85},
 "fired_at": "2026-04-22T19:04:08Z"}
```

redlines.jsonl record:
```json
{"document_id": "DOC-0001", "clause_id": "C-0000",
 "section_id": null, "risk_id": "R001",
 "original_text": "", "proposed_text": "[ADD] Remediation for R001: ...",
 "rationale": "Template redline produced from deterministic risk signal.",
 "change_type": "replace", "source": "template", "confidence": 0.8}
```

intake_manifest.json is a list of records:
```json
[{"document_id": "DOC-0001", "source_filename": "CTR-001_MSA_Apex_Industrial.pdf", ...}]
```

---

## Step 2 — Theme Configuration

**File:** `.streamlit/config.toml`

```toml
[theme]
primaryColor = "#1E40AF"
backgroundColor = "#0F172A"
secondaryBackgroundColor = "#1E293B"
textColor = "#F1F5F9"
font = "sans serif"
```

**Custom CSS** — inject via `st.markdown()` with `unsafe_allow_html=True` at top of each page:

```css
/* Severity badge styling */
.badge-high   { background:#DC2626; color:white; padding:2px 8px; border-radius:4px; font-size:12px; font-weight:600; }
.badge-medium { background:#D97706; color:white; padding:2px 8px; border-radius:4px; font-size:12px; font-weight:600; }
.badge-low    { background:#16A34A; color:white; padding:2px 8px; border-radius:4px; font-size:12px; font-weight:600; }

/* Stoplight KPI cards */
.kpi-card { border-radius:8px; padding:16px; text-align:center; cursor:pointer; }
.kpi-total  { background:#1E293B; border:1px solid #334155; }
.kpi-high   { background:#7F1D1D; border:1px solid #DC2626; }
.kpi-medium { background:#78350F; border:1px solid #D97706; }
.kpi-low    { background:#14532D; border:1px solid #16A34A; }
```

---

## Step 3 — Page 1: Contract Changes (Enhanced)

**File:** `app/ui/pages/1_Contract_Changes.py`

### Layout

**Sidebar:**
- Run selector dropdown (same pattern as original, use `get_all_runs()`)

**Main area:**

#### Section A — Stoplight KPI Row
Use `st.columns(4)` to render four metric cards:
- **Total Changes** — count of all risk_signals for selected run
- **Critical (High)** — count where severity == "High", red background
- **Medium** — count where severity == "Medium", amber background
- **Low** — count where severity == "Low", green background

Each KPI card is a `st.button()`. Clicking one sets `st.session_state["severity_filter"]` to that severity string (or "All" for the total card). Active filter card shows a highlighted border.

#### Section B — Quick Filter Bar
Row of: 
- `st.selectbox("Document", ["All"] + doc_list)` → `st.session_state["doc_filter"]`
- Active filter pills showing current filters with an X to clear

#### Section C — Changes Table
Apply both filters to the DataFrame, then render with `st.dataframe()` using column config:

```python
st.dataframe(
    filtered_df[[
        "document_label",   # mapped from doc_label_map
        "rule_id",
        "severity",         # render as colored badge via column_config
        "field_triggered",
        "message",
        "evidence",
    ]],
    column_config={
        "severity": st.column_config.TextColumn("Severity"),
        "document_label": st.column_config.TextColumn("Contract"),
    },
    use_container_width=True,
)
```

Default sort: severity_order ASC (High first), then document_id ASC.

Show row count: `st.caption(f"Showing {len(filtered_df)} of {len(df)} signals")`

---

## Step 4 — Page 2: Risk Assessment

**File:** `app/ui/pages/2_Risk_Assessment.py`

### Layout

**Sidebar:**
- Same run selector as Page 1

**Main area:**

#### Section A — Executive Summary
```python
st.subheader("Executive Summary")
st.info(load_run_summary(selected_run))  # or st.markdown() for richer rendering
```
Add key stats inline:
- Documents processed (from run_summary or len(intake_manifest))
- Total risk signals
- High severity count
- Mean extraction confidence (from extractions.jsonl)

#### Section B — Severity Distribution Chart
```python
severity_counts = df["severity"].value_counts().reindex(["High", "Medium", "Low"], fill_value=0)
st.bar_chart(severity_counts)
```
Or use `st.plotly_chart()` with a color-mapped horizontal bar chart if plotly is available (it is not in requirements — add `plotly>=5.0` to requirements.txt if desired, otherwise use `st.bar_chart`).

#### Section C — Risk Breakdown by Contract
For each document (sorted by High count desc):
```python
with st.expander(f"{doc_label} — {high_count} High / {med_count} Med / {low_count} Low"):
    st.dataframe(doc_df[["rule_id", "severity", "field_triggered", "message"]])
```

---

## Step 5 — Page 3: Redlining

**File:** `app/ui/pages/3_Redlining.py`

### Layout

**Sidebar:**
- Same run selector
- Contract selector: `st.selectbox("Contract", doc_labels)` — populates from `get_doc_label_map()`

**Main area:**

#### Section A — AI Suggested Changes
For each redline record for the selected document:

```python
for i, row in redlines_for_doc.iterrows():
    with st.container():
        st.markdown(f"**{row['risk_id']}** — {row['change_type'].upper()}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Original Text**")
            st.code(row["original_text"] or "(no original text — addition required)", language=None)
        with col2:
            st.markdown("**Proposed Change**")
            st.code(row["proposed_text"], language=None)
        
        st.caption(f"Rationale: {row['rationale']} | Confidence: {row['confidence']:.0%}")
        
        decision_key = f"decision_{row['document_id']}_{row['risk_id']}"
        current = st.session_state.get(decision_key, "Pending")
        
        c1, c2, c3 = st.columns([1, 1, 4])
        if c1.button("Accept", key=f"accept_{i}"):
            st.session_state[decision_key] = "Accepted"
        if c2.button("Reject", key=f"reject_{i}"):
            st.session_state[decision_key] = "Rejected"
        st.markdown(f"Status: **{current}**")
        
        if current not in ("Accepted", "Rejected"):
            edited = st.text_area("Edit proposed text", value=row["proposed_text"], key=f"edit_{i}")
            if edited != row["proposed_text"]:
                st.session_state[decision_key] = "Edited"
                st.session_state[f"edited_text_{i}"] = edited
        
        st.divider()
```

#### Section B — Custom Changes
```python
st.subheader("Add Custom Change")
custom_clause = st.text_input("Clause / Section Reference")
custom_text = st.text_area("Proposed Change Text")
if st.button("Add Change"):
    custom_key = f"custom_{selected_doc}"
    if custom_key not in st.session_state:
        st.session_state[custom_key] = []
    st.session_state[custom_key].append({
        "clause_ref": custom_clause,
        "proposed_text": custom_text,
        "source": "user",
    })
    st.success("Change added.")

# Show existing custom changes
if st.session_state.get(f"custom_{selected_doc}"):
    st.subheader("Custom Changes Added")
    for c in st.session_state[f"custom_{selected_doc}"]:
        st.write(f"- [{c['clause_ref']}] {c['proposed_text']}")
```

#### Section C — Export Decisions
```python
if st.button("Export Decisions as JSON"):
    decisions = collect_all_decisions(selected_doc, redlines_for_doc)
    st.download_button(
        label="Download decisions.json",
        data=json.dumps(decisions, indent=2),
        file_name=f"decisions_{selected_doc}.json",
        mime="application/json",
    )
```

The `collect_all_decisions()` helper builds a list of:
```python
{
    "document_id": ...,
    "risk_id": ...,
    "decision": "Accepted" | "Rejected" | "Edited" | "Pending",
    "final_text": ...,  # edited text if Edited, proposed_text if Accepted
    "source": "ai" | "user",
}
```

---

## Step 6 — Replace streamlit_app.py

**File:** `app/ui/streamlit_app.py` — REPLACE entirely with:

```python
import streamlit as st

st.set_page_config(
    page_title="Contract Intelligence",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Contract Intelligence POC")
st.markdown("""
Welcome to the offline contract analysis system. Use the sidebar to navigate between pages.

| Page | Purpose |
|------|---------|
| **Contract Changes** | Triage all risk signals with stoplight filtering |
| **Risk Assessment** | Executive summary and per-contract risk breakdown |
| **Redlining** | Review AI-suggested edits and author custom changes |
""")

st.info("Select a page from the sidebar to begin.")
```

---

## Step 7 — Update Requirements

**File:** `requirements.txt` — add if not present:
```
plotly>=5.0
```
(Optional — only if Codex uses `st.plotly_chart`. `st.bar_chart` works without it.)

---

## Notes for Codex

1. **Working directory assumption:** All data paths (`outputs/runs/`, etc.) are relative to `contract_management_system/`. Run streamlit from that directory.

2. **intake_manifest.json location:** At `{run_dir}/intake_manifest.json`. It is a JSON array (not JSONL). Use `json.loads(path.read_text())`.

3. **Session state isolation:** Each page shares `st.session_state` across page navigations in the same session. Prefix all state keys with the page name to avoid collisions (e.g., `"changes_severity_filter"`, `"redline_decision_DOC-0001_R001"`).

4. **uipro-cli usage:** Run `uipro-cli` to generate color tokens, spacing scale, and component CSS that matches the dark theme specified in Step 2. Inject any generated CSS via `st.markdown('<style>...</style>', unsafe_allow_html=True)` at the top of each page file. Streamlit does not use React/JSX directly, so use the CSS output only, not the component JSX.

5. **Severity sort order:** Always sort High → Medium → Low using an explicit map `{"High": 1, "Medium": 2, "Low": 3}` rather than alphabetical.

6. **No new backend code needed.** All data already exists in the run output directories. Do not modify anything under `app/core/`.

---

## File Change Summary

| File | Action |
|------|--------|
| `app/ui/streamlit_app.py` | REPLACE (homepage shell) |
| `app/ui/components/data_loader.py` | CREATE |
| `app/ui/pages/1_Contract_Changes.py` | CREATE |
| `app/ui/pages/2_Risk_Assessment.py` | CREATE |
| `app/ui/pages/3_Redlining.py` | CREATE |
| `.streamlit/config.toml` | CREATE |
| `requirements.txt` | UPDATE (add plotly if using charts) |

---

## Verification

After Codex builds the files, verify with:

```bash
cd C:\Users\jonesbrade\ai-contracts-poc-offline\contract_management_system
streamlit run app/ui/streamlit_app.py
```

Checklist:
- [ ] Sidebar shows 3 page links
- [ ] Contract Changes: stoplight buttons filter the table
- [ ] Contract Changes: default sort is High first
- [ ] Risk Assessment: summary markdown renders at top, expandable docs below
- [ ] Redlining: selecting a contract shows its redlines
- [ ] Redlining: Accept/Reject buttons update status without page reload
- [ ] Redlining: Custom change form appends to the list
- [ ] Export button downloads valid JSON
