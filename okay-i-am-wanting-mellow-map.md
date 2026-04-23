# Plan: Streamlit UI Overhaul — Soft UI Evolution + Functional Changes

## Context
Combines the original UI overhaul request with net-new requirements from the
AI Contracts POC peer review meeting (`AI_Contracts_POC_Enhancements.md`).
The app currently uses a dark slate theme (navy `#0F172A` bg). Switching to
Soft UI Evolution (light lavender-white, indigo accents, soft shadows).
Functional upgrades: home redirect, clickable KPI stoplight, per-contract KPI
counts, reworked Executive Summary, full-document redlining canvas with
multi-format export, explanation panels per flag, run metadata display, Coupa
export placeholder, and a Clause Library placeholder page.

---

## Files to Modify / Create

| File | Change |
|------|--------|
| `contract_management_system/.streamlit/config.toml` | Swap to Soft UI Evolution colors |
| `app/ui/streamlit_app.py` | Replace nav table with `st.switch_page` redirect |
| `app/ui/pages/1_Contract_Changes.py` | **Rename** → `1_Risk_Identification.py`; clickable KPIs; contract filter to sidebar; KPI counts reflect selected contract; expandable explanation panel per flag |
| `app/ui/pages/2_Risk_Assessment.py` | **Rename** → `2_Executive_Summary.py`; full rewrite with pie chart, run metadata, per-contract executive view |
| `app/ui/pages/3_Redlining.py` | Full-document canvas + Excel/Word/PDF + Coupa placeholder export |
| `app/ui/pages/4_Clause_Library.py` | **New** — P1 placeholder page for searchable clause library |
| `app/ui/components/data_loader.py` | Add `load_contract_text()` for PDF/docx extraction |

---

## 0. Page Renaming  *(net-new from meeting notes)*

The current page names blur the line between "identifying risks" and "reviewing
completed changes." Rename to clarify intent:

| Old filename | New filename | New display title |
|---|---|---|
| `1_Contract_Changes.py` | `1_Risk_Identification.py` | Risk Identification |
| `2_Risk_Assessment.py` | `2_Executive_Summary.py` | Executive Summary |
| `3_Redlining.py` | `3_Redlining.py` | Redlining (unchanged) |

Update `streamlit_app.py` switch target to point to the new filename.
Update all cross-page `st.switch_page` references if any.

---

## 1. Soft UI Evolution Theme

### `.streamlit/config.toml`
```toml
[theme]
primaryColor      = "#6366F1"
backgroundColor   = "#F5F3FF"
secondaryBackgroundColor = "#FFFFFF"
textColor         = "#1E1B4B"
font              = "sans serif"
```

### Shared CSS (injected via `st.markdown` at top of each page)
Apply this block to all 3 pages. Key rules:
- Fonts: Varela Round (headings) + Nunito Sans (body) via Google Fonts `@import`
- Cards: `background: #FFFFFF; border-radius: 10px; box-shadow: 0 2px 8px rgba(99,102,241,0.08)`
- Hover: `box-shadow` deepens + `transform: translateY(-1px)` in 200ms
- KPI boxes: white background, `border-left: 4px solid <severity-color>`, number colored by severity
- Severity badges: pill shape with light tinted background (not solid dark blocks)
  - High: `#FEF2F2` bg, `#DC2626` text, `#FECACA` border
  - Medium: `#FFFBEB` bg, `#D97706` text, `#FDE68A` border
  - Low: `#F0FDF4` bg, `#16A34A` text, `#BBF7D0` border

---

## 2. Home Page → Auto-Redirect

`streamlit_app.py` becomes a one-liner redirect. No navigation table needed:
```python
st.set_page_config(page_title="Contract Intelligence", layout="wide")
st.switch_page("pages/1_Contract_Changes.py")
```

---

## 3. Clickable KPI Stoplight Cards (1_Risk_Identification.py)

### Remove separate filter buttons
Delete the four `st.button` calls ("Show All", "Filter Critical", etc.) that appear below each KPI HTML div.

### Make the KPI box itself the click target
After each KPI `st.markdown(...)` block, render a `st.button` with an empty label.
Use CSS `:has()` selector to make that button invisible and overlaid on the card above it:

```css
/* Overlay button sits on top of the KPI card with 0 opacity */
div[data-testid="element-container"]:has(.kpi-box) + div[data-testid="element-container"] button {
    margin-top: -90px;
    height: 90px;
    opacity: 0;
    cursor: pointer !important;
    position: relative;
    z-index: 10;
    background: transparent !important;
    border: none !important;
}
```

The KPI HTML div gets `cursor: pointer` and `:hover` shadow deepening via CSS.
The overlaid invisible button captures the click and sets `st.session_state["changes_sev_filter"]`.

### Active filter highlight
When a filter is active, the corresponding KPI box gets an extra CSS class
`kpi-active` (injected dynamically via Python f-string) with a stronger border
and background tint to show which is selected.

---

## 4. KPI Counts Reflect Selected Contract (1_Risk_Identification.py)

**Problem**: KPIs currently computed from the full run's `df` before the
contract filter is applied.

**Fix**: Move the contract `selectbox` to the **sidebar** (alongside the Run
selector). This way the contract selection is available before rendering the
KPI row. Compute counts from a contract-pre-filtered frame:

```python
# Sidebar — comes before KPI calc
selected_run = st.sidebar.selectbox("Run", runs, ...)
doc_label_map = get_doc_label_map(run_key)
df["contract"] = df["document_id"].map(doc_label_map).fillna(df["document_id"])
contract_options = ["All"] + sorted(df["contract"].unique().tolist())
doc_filter = st.sidebar.selectbox("Contract", contract_options, key="changes_doc_filter")

# Apply contract filter before computing KPI counts
kpi_df = df[df["contract"] == doc_filter] if doc_filter != "All" else df
total        = len(kpi_df)
high_count   = int((kpi_df["severity"] == "High").sum())
medium_count = int((kpi_df["severity"] == "Medium").sum())
low_count    = int((kpi_df["severity"] == "Low").sum())
```

Severity filter (from clicking KPI) is then applied on top of `kpi_df` for the table.
Remove the old `col_sev, col_doc` filter bar row (contract is now in sidebar,
severity is shown as `st.caption` below KPIs).

---

## 4b. Explanation Panel Per Flag  *(net-new from meeting notes)*

On the Risk Identification page, each row in the signal table should be
expandable to show a detail panel answering:
- **Triggering Rule** — `rule_id` + a plain-English description (from the
  `message` field)
- **Evidence Text** — the `evidence` value extracted from the contract
- **Severity Rationale** — why this severity level was assigned (use
  `rule_inputs` JSON if present, otherwise show confidence score)

Implementation: replace the flat `st.dataframe` with a loop of
`st.expander(label)` rows, one per signal. Each expander contains a 3-column
layout: Triggering Rule | Evidence | Severity Rationale. This satisfies the
meeting note requirement for "explanation panels per flag."

---

## 5. Executive Summary — Full Rewrite (2_Executive_Summary.py)

### New page structure

**Sidebar**: Run selector + Contract selector (same pattern as Risk Identification).

**Run metadata bar** *(net-new from meeting notes)* — always visible at top of
page regardless of contract selection. A thin info strip showing:
`Run: RUN_20260423_140756  |  Started: 2026-04-23 14:07  |  Documents: 10`
Pulled from the run directory name + `intake_manifest` row count.

**"All contracts" view** (when "All" selected):
- Row of 4 styled metric cards: Docs Processed, Total Signals, Critical Count, Medium Count
- **Pie chart** *(net-new — meeting notes say "pie charts preferred")* showing
  severity distribution (High / Medium / Low) — use `plotly` `px.pie` with the
  Soft UI Evolution palette. `plotly` is already in `requirements.txt`.
- Per-contract summary table: one row per contract showing name + severity pill counts
- "Tyson AI Agent Analysis" placeholder card

**Single contract view** (when a contract is selected):
- Contract header card: contract name + overall risk level badge (highest severity present)
- 3-column metric row: Critical / Medium / Low counts
- **Pie chart** for that contract's severity split
- "Top Risk Items" — first 3 High-severity signals as narrative cards (field name + message)
- Full signal table for that contract (rule_id, severity badge, field, issue, evidence)
- "Tyson AI Agent Analysis" placeholder

### Remove from page
- `load_run_summary` markdown expander (full run log is not executive-appropriate)
- `st.bar_chart` (replaced by plotly pie chart)
- The old expandable per-contract tables (replaced by the structured sections above)

---

## 6. Redlining — Full-Document Canvas (3_Redlining.py)

### Step A: Add `load_contract_text()` to `data_loader.py`

```python
@st.cache_data
def load_contract_text(run_dir: str, document_id: str) -> str:
    manifest = load_intake_manifest(run_dir)
    if manifest.empty:
        return ""
    row = manifest[manifest["document_id"] == document_id]
    if row.empty or "source_path" not in row.columns:
        return ""
    source_path = Path(row.iloc[0]["source_path"])
    if not source_path.is_absolute():
        # resolve relative to project root (2 levels above run_dir's 'outputs/')
        source_path = Path(run_dir).parents[1] / source_path
    if source_path.suffix.lower() == ".pdf":
        import pdfplumber
        with pdfplumber.open(source_path) as pdf:
            return "\n\n".join(p.extract_text() or "" for p in pdf.pages)
    if source_path.suffix.lower() == ".docx":
        from docx import Document
        return "\n".join(p.text for p in Document(source_path).paragraphs)
    return ""
```

### Step B: Build the canvas

Replace the current "AI Suggested Changes" loop with a document canvas:

1. Load full contract text via `load_contract_text(run_key, selected_doc)`.
2. Build an in-memory copy of the text.
3. For each redline (sorted by position / order):
   - If `original_text` is non-empty and found in the document text, replace it with:
     `<del style="background:#FEE2E2;text-decoration:line-through;color:#991B1B">ORIG</del><ins style="background:#DCFCE7;text-decoration:underline;color:#166534">PROPOSED</ins>`
   - If `original_text` is empty (addition), append a superscript marker `[+N]` and track it in a additions list.
4. Wrap the processed HTML in a scrollable container:
   ```html
   <div style="background:#fff;border-radius:10px;padding:24px 32px;
               box-shadow:0 2px 8px rgba(99,102,241,0.08);
               max-height:600px;overflow-y:auto;font-family:'Nunito Sans';
               line-height:1.7;white-space:pre-wrap;">
       {processed_text}
   </div>
   ```
5. Render via `st.markdown(..., unsafe_allow_html=True)`.

If contract text cannot be extracted (empty string), fall back to the current
card-per-change layout with inline diff styling.

### Step C: Review panel

Below the canvas, render a collapsible "Review Changes" expander.
Inside: one row per redline showing risk_id, severity badge, proposed text,
and Accept / Reject / Edit buttons (same session-state logic as current code).

### Step D: Export (replace JSON download)

Three `st.download_button` buttons side by side:

**Excel** — `openpyxl` via `pandas.to_excel(BytesIO(), engine="openpyxl")`:
- Sheet: "Redlines" with columns Contract, Risk ID, Severity, Original, Proposed, Decision
- Sheet: "Custom Changes" with Clause Ref, Proposed Text

**Word** — `python-docx` (already in requirements):
- Title: contract filename
- For each redline: heading (Risk ID + Severity), paragraph with strikethrough run
  (original) + underline run (proposed), decision status line
- For each custom change: heading "Custom", paragraph with proposed text

**PDF** — `reportlab`:
- Use `SimpleDocTemplate` + `Paragraph` with inline HTML-style text
- Same structure as Word export

All three use `io.BytesIO()` and `st.download_button` with appropriate MIME types
(`application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`,
`application/vnd.openxmlformats-officedocument.wordprocessingml.document`,
`application/pdf`).

**"Send to Coupa" placeholder** *(net-new from meeting notes — P0 integration)*:
A fourth button labeled "Send to Coupa" rendered as a disabled/greyed-out
`st.button` with a tooltip "Integration coming in Phase 2". This satisfies
the P0 requirement to surface the downstream API integration touchpoint
without building the actual API call yet.

Remove the existing `Download decisions.json` button.

---


## Verification

1. Run `streamlit run app/ui/streamlit_app.py` from `contract_management_system/`
2. App immediately lands on **Risk Identification** (no home screen)
3. Sidebar shows Risk Identification page title (not "Contract Changes")
4. KPI boxes are white with colored left border; clicking each box filters the table; no separate filter buttons visible
5. Change Contract in sidebar — KPI counts update to that contract's totals
6. Expand a row in the signal table — explanation panel appears with Triggering Rule, Evidence, Severity Rationale
7. Navigate to **Executive Summary** — run metadata bar is visible; pie chart renders; "All" shows aggregate; selecting a contract shows contract-specific pie + top risks
8. Navigate to **Redlining** — scrollable document canvas shows inline red/green changes; Review Changes expander has Accept/Reject; Excel / Word / PDF download buttons work; "Send to Coupa" button is visible but disabled
9. Verify Soft UI Evolution theme: light lavender background, white cards, indigo accent color, no dark navy backgrounds anywhere
