# Demo Guide — Contract Intelligence POC

_Last updated: 2026-04-23 | UI version: 3-page Streamlit app (commit `a008188`)_

---

## Prerequisites

Before starting, confirm you have the following installed:

```bash
python --version        # Python 3.10+ required
pip --version
streamlit --version     # should be 1.35+
```

If Streamlit is not installed:
```bash
pip install -r requirements.txt
```

---

## Step 1 — Start from the Right Directory

All commands must be run from the project root:

```
C:\Users\jonesbrade\ai-contracts-poc-offline\contract_management_system\
```

In Git Bash or your terminal:
```bash
cd /c/Users/jonesbrade/ai-contracts-poc-offline/contract_management_system
```

---

## Step 2 — Run the Pipeline (Generate Fresh Data)

If you want to run the pipeline fresh before launching the UI:

```bash
python -m app.main
```

**Expected output:**
```
Run complete: outputs/runs/RUN_YYYYMMDD_HHMMSS
```

A new timestamped run directory is created under `outputs/runs/`. This takes ~5–15 seconds for 17 contracts.

> **Note:** If you skip this step, the UI will load from the 3 existing runs already in `outputs/runs/`. You can demo the UI without re-running the pipeline.

---

## Step 3 — Launch the UI

```bash
streamlit run app/ui/streamlit_app.py
```

Your browser will open automatically to `http://localhost:8501`. If it doesn't, open it manually.

**Expected:** A dark-themed homepage with a navigation table and sidebar.

---

## Page-by-Page Demo Walkthrough

---

### Homepage

**What you see:**
- Title: "Contract Intelligence POC"
- Navigation table showing the 3 pages and their purpose
- Blue info banner: "Select a page from the sidebar to begin."

**What to do:**
- Point out the sidebar on the left — Streamlit automatically generates page links from the `pages/` directory
- Click **"1 Contract Changes"** in the sidebar to begin

---

### Page 1 — Contract Changes

**Purpose:** Triage all risk signals across the selected run. Quickly identify the most critical issues and filter down.

#### Demo Steps

**1. Run Selector**
- At the top of the sidebar, a dropdown shows all available runs (format: `RUN_YYYYMMDD_HHMMSS`)
- Select the most recent run
- The page data updates automatically

**2. Stoplight KPI Row**
- Four colored cards display across the top:
  - **Total Changes** — total risk signals for this run (slate/dark card)
  - **Critical** — count of High severity signals (red card)
  - **Medium** — count of Medium severity signals (amber card)
  - **Low** — count of Low severity signals (green card)
- Each card has a filter button beneath it

**3. Filter by Severity (Stoplight Interaction)**
- Click **"Filter Critical"** under the red card
  - The table below immediately filters to show only High severity signals
  - The caption updates: "Showing X of Y signals"
- Click **"Filter Medium"** — table switches to Medium signals only
- Click **"Show All"** — all signals return
- _This is the main interactive feature — highlight the speed of triage_

**4. Filter by Contract**
- Use the **"Filter by Contract"** dropdown (next to the severity label) to narrow to a specific document
- Combine: select "Filter Critical" + select a specific contract to see only that contract's critical issues

**5. Changes Table**
- Columns: Contract, Rule, Severity, Field, Issue, Evidence
- Default sort: Critical first, then Medium, then Low
- Note: Currently all contracts show similar signals — this is a known phase-1 data quality issue (PDF extraction). The UI structure is correct.

**Key talking points:**
- Reviewers can get to the highest-risk items in one click
- No need to scroll through a flat list — severity triage is immediate
- Contract filter allows per-document focus without leaving the page

---

### Page 2 — Risk Assessment

**Purpose:** Executive view of the run — summary statistics, severity distribution, and per-contract risk breakdown.

#### Demo Steps

**1. Run Selector**
- Same sidebar dropdown as Page 1 — selecting a run updates all sections

**2. Executive Summary Metrics**
- Five metric cards at the top:
  - Documents Processed
  - Total Risk Signals
  - Critical (High) count
  - Medium count
  - Low count
- Below the metrics: average extraction confidence percentage
- Click the **"Full Run Summary"** expander to see the raw `run_summary.md` content

**3. Severity Distribution Chart**
- A bar chart showing High / Medium / Low signal counts
- Gives a quick visual sense of the risk distribution across the run

**4. Risk Breakdown by Contract**
- Each contract gets its own expandable section
- Sorted by High count descending (most critical contracts at top)
- Each expander header shows: `Contract Name — 🔴 X Critical  🟡 Y Medium  🟢 Z Low`
- Click any expander to see that contract's rule-level breakdown (Rule, Severity, Field, Issue)

**Demo flow suggestion:**
1. Point to the metrics row — "This is what a legal ops manager sees first"
2. Show the chart — "Distribution tells you if this is a widespread problem or isolated"
3. Expand the top contract (highest High count) — "Drill into the worst offender"
4. Expand a second contract and compare — "Side-by-side risk profiles"

**Key talking points:**
- Executive summary is always at the top — no scrolling required for leadership view
- Contract-level rollup with severity counts allows prioritization of review queue
- Chart gives instant sense of overall run health

---

### Page 3 — Redlining

**Purpose:** Review AI-suggested contract edits, make decisions (Accept / Reject / Edit), add your own custom changes, and export the full decision record.

#### Demo Steps

**1. Contract Selector**
- The sidebar has two dropdowns: Run selector + Contract selector
- Select any contract from the Contract dropdown (shows filename, e.g., `CTR-001_MSA_Apex_Industrial.pdf`)
- The page loads that contract's AI-suggested redlines

**2. AI Suggested Changes Panel**
- Each redline suggestion shows as a card with:
  - **Risk ID and Severity** (color-coded: red=High, amber=Medium, green=Low)
  - **Change type** (e.g., REPLACE)
  - **Original Text** (left column) — the clause text before the change
  - **AI Proposed Change** (right column) — what the system suggests adding/replacing
  - **Rationale and Confidence** — explanation and confidence score
  - **Status** — starts as `Pending`

**3. Accept a Suggestion**
- Find any redline card
- Click **"✓ Accept"**
- Status immediately updates to **Accepted** (green)
- The edit text area disappears — decision is locked

**4. Reject a Suggestion**
- Click **"✗ Reject"** on a different card
- Status updates to **Rejected** (red)

**5. Edit a Suggestion**
- Leave a card in Pending state
- Find the text area below the card (labeled "Edit proposed text (optional)")
- Modify the proposed text — type your own language
- Status automatically updates to **Edited** (amber) as you type

**6. Add a Custom Change**
- Scroll past the AI suggestions to **"Add Custom Change"**
- Fill in:
  - **Clause / Section Reference** — e.g., "Section 4.2 Liability"
  - **Proposed Change Text** — your custom redline language
- Click **"Add Change"**
- A success message appears and your custom change is listed below the form
- Custom changes can be removed with the ✕ button

**7. Export Decisions**
- Scroll to the bottom — **"Export Decisions"** section
- Click **"Download decisions.json"**
- A JSON file downloads containing every AI suggestion with its decision (Accepted/Rejected/Edited/Pending) plus all custom changes

**Sample exported JSON structure:**
```json
[
  {
    "document_id": "DOC-0001",
    "risk_id": "R001",
    "decision": "Accepted",
    "final_text": "[ADD] Remediation for R001: Missing expiration date",
    "source": "ai"
  },
  {
    "document_id": "DOC-0001",
    "risk_id": "R007",
    "decision": "Edited",
    "final_text": "Party shall include a liability cap not to exceed 2x annual contract value.",
    "source": "ai"
  },
  {
    "document_id": "DOC-0001",
    "clause_ref": "Section 4.2",
    "final_text": "Governing law shall be the State of Arkansas.",
    "decision": "Accepted",
    "source": "user"
  }
]
```

**Key talking points:**
- Every AI suggestion can be individually accepted, rejected, or rewritten — reviewers stay in control
- Custom changes let attorneys add language the AI didn't suggest
- The JSON export is the bridge to downstream workflows (DocuSign, contract management systems, Word)
- Decision state persists across page navigations within the same session (switch to Page 1, come back — decisions are preserved)

> **Important caveat to mention:** Decisions are stored in browser session memory. They clear if the page is fully refreshed. Always export before closing the session. Persistent storage is a Phase 2 item.

---

## Switching Between Runs

The run selector appears in the sidebar on every page. To compare two runs:

1. Note the current run's signal counts on Page 2
2. Switch to a different run in the sidebar dropdown
3. All pages update immediately — the metrics, table, and redlines all reflect the new run

---

## Known Limitations to Acknowledge During Demo

These are expected at this stage and should be addressed proactively:

| What You'll See | Why It Happens | Phase 2 Fix |
|---|---|---|
| All contracts show similar/identical risk signals | PDF extraction reads binary as UTF-8 — no real text extracted, so all keyword checks fail | Add PyMuPDF for real PDF parsing |
| Redline "Original Text" column is blank | Clause anchoring falls back to C-0000 with no text | Fix clause population in orchestrator |
| All extraction confidence shows ~85% | Confidence is hardcoded, not computed | Compute from actual field coverage |
| Decisions lost on page refresh | Session state only, no disk persistence | Auto-save to run directory |
| `.docx` export is plain text | Phase-1 pseudo-DOCX format | True tracked-changes DOCX with python-docx |

**Framing for stakeholders:** _"The pipeline structure, security posture, and UI are complete. Phase 2 focuses on extraction quality — swapping in a real PDF parser is a targeted change that doesn't touch any other module."_

---

## Troubleshooting

**"No runs found" on any page**
```bash
# Make sure you're in the right directory
cd /c/Users/jonesbrade/ai-contracts-poc-offline/contract_management_system
# Run the pipeline first
python -m app.main
```

**"ModuleNotFoundError: No module named 'app'"**
```bash
# Must run from the contract_management_system directory, not the parent
cd /c/Users/jonesbrade/ai-contracts-poc-offline/contract_management_system
streamlit run app/ui/streamlit_app.py
```

**Page doesn't open automatically**
- Open your browser manually to: `http://localhost:8501`

**Streamlit not found**
```bash
pip install streamlit>=1.35
```

**Port 8501 already in use**
```bash
streamlit run app/ui/streamlit_app.py --server.port 8502
```

---

## Quick Reference — File Locations

| Item | Path |
|---|---|
| Pipeline entry point | `app/main.py` |
| Streamlit homepage | `app/ui/streamlit_app.py` |
| Contract Changes page | `app/ui/pages/1_Contract_Changes.py` |
| Risk Assessment page | `app/ui/pages/2_Risk_Assessment.py` |
| Redlining page | `app/ui/pages/3_Redlining.py` |
| Shared data loader | `app/ui/components/data_loader.py` |
| Run outputs | `outputs/runs/RUN_*/` |
| Risk signals data | `outputs/runs/RUN_*/risk_signals.jsonl` |
| Redlines data | `outputs/runs/RUN_*/redlines.jsonl` |
| Risk rules config | `rules/core_poc_rules.yaml` |
| Theme config | `.streamlit/config.toml` |
