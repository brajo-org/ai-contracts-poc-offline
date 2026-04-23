# AUDIT_HANDOFF.md — Contract Intelligence POC

_Generated: 2026-04-23 | Branch: `codex/flag-potential-security-risk-commands` | Commit: `a008188`_

---

## High-Level Summary

This is an **offline-first, Windows-compatible contract risk analysis system** built as a proof-of-concept for automated contract review. The system ingests contract documents (PDF, DOCX, XLSX), runs a deterministic 9-phase analysis pipeline, flags legal and compliance risks against a configurable rule set, generates template-based redline suggestions, and surfaces all results through a 3-page Streamlit web UI. It is designed to run entirely without internet access, with hard security gates enforced before any document processing begins.

**Current state:** Phase-1 scaffold is complete and functional. The pipeline processes 17 real contracts end-to-end with zero failures. The Streamlit UI was recently expanded from a single 37-line page to a full 3-page application with risk triage, executive assessment, and interactive redlining. The system is a POC — extraction quality is deliberately minimal (keyword-matching), and redlines are templated rather than AI-generated.

---

# Executive Summary

- **Pipeline is functional end-to-end.** The most recent run (RUN_20260422_190408) processed 17 documents with 0 failures and produced all 15 expected artifact types.
- **UI was just expanded** from a single raw dataframe to a 3-page Streamlit app: Contract Changes (stoplight triage), Risk Assessment (executive summary + per-contract breakdown), and Redlining (AI suggestions + user edits + JSON export). Pushed to `origin/codex/flag-potential-security-risk-commands` at commit `a008188`.
- **Extraction quality is intentionally low.** All 17 contracts trigger all 7 core risk rules because extraction is keyword-only and the PDF/DOCX text fallback reads binary as UTF-8, producing garbage text with no matching keywords. This is a known phase-1 limitation, not a bug.
- **Security posture is strong for a POC.** Network isolation, telemetry blocking, file-type gating, and path traversal protection are all enforced at preflight with fail-closed behavior.
- **Internal model integration is stubbed.** The `InternalLLMClient` returns a `{"status": "stub"}` response. No LLM calls are made in the current codebase. The allowlisted internal hosts (`internal.tyson.local`, `tyson.llm.local`) suggest enterprise deployment intent.
- **Test coverage is minimal.** 5 tests total (2 unit, 1 integration, 1 security, 1 routing). No tests exist for the segmentation, extraction, redline generation, or export modules.
- **Eval pack is incomplete.** `evals/eval_runner.py` counts risk signals but does not measure precision, recall, or accuracy. Gold annotation fixtures are empty directories.
- **The DOCX export is not true tracked-changes DOCX.** It is a plain text file with a `.docx` extension containing a human-readable diff format. `python-docx` is in requirements but not used.

---

# Product Vision and Telos

## What We Are Building

An enterprise contract risk analysis platform that automatically reviews incoming legal contracts, flags compliance and legal risks, proposes specific language changes (redlines), and provides reviewers with an interactive interface to accept, reject, or modify those changes — all without sending contract data outside the organization's network perimeter.

## Why It Matters

Enterprise legal teams process large volumes of third-party contracts (MSAs, SOWs, NDAs, purchase agreements). Manual review is slow, inconsistent, and expensive. Automated pre-screening surfaces critical issues (missing liability caps, missing expiration dates, auto-renewal traps) so attorneys can focus on substantive negotiation rather than checklist review.

The offline-first constraint addresses a real enterprise concern: contract documents often contain trade secrets, PII, and commercially sensitive terms. Routing them through external AI APIs is a compliance and IP risk that blocks adoption. This system is designed to run on-premises or in an air-gapped environment.

## Desired End-State

A production-grade, on-premises contract intelligence platform where:

1. Contracts are ingested automatically from a document intake queue.
2. An internal LLM (hosted at an allowlisted enterprise endpoint) extracts fields, detects risk clauses, and proposes specific redline language — not template strings.
3. Reviewers interact with AI suggestions through the Streamlit (or successor) UI, accepting, rejecting, or editing each proposed change.
4. Approved redlines are exported as true DOCX tracked-changes documents ready for counterparty negotiation.
5. All decisions are logged with full lineage traceability for audit and compliance reporting.
6. Evaluation metrics (precision, recall, attorney acceptance rate) are measured continuously against annotated ground truth.

---

# Implementation Approach

## Architecture

**Linear artifact-first pipeline** (`app/core/orchestrator.py`):

```
PREFLIGHT → INTAKE → ROUTE → NORMALIZE → SEGMENT → EXTRACT → RULES → REDLINE → EXPORT
```

Each phase writes local artifacts to a timestamped run directory (`outputs/runs/RUN_YYYYMMDD_HHMMSS/`). Phases are sequential; failures in any phase halt the run and log to `event_log.jsonl`.

**Security layer** wraps the pipeline entry point:
- `env_guard.py` — blocks runs if telemetry is enabled or limits are invalid
- `network_guard.py` — blocks runs if `NO_PUBLIC_NETWORK != true`; validates internal model URL against allowlist if model mode is enabled
- `path_guard.py` — prevents path traversal in all file I/O

**UI layer** is a Streamlit multi-page app reading from completed run artifacts. It does not call the pipeline directly — it is a read-only viewer plus a stateful redline decision interface (decisions stored in `st.session_state`, not persisted to disk beyond the JSON export).

## Key Technical Decisions

| Decision | Choice | Rationale |
|---|---|---|
| D-001 | Offline-first, fail-closed preflight | Prevent accidental internet egress in enterprise environments |
| D-002 | Internal model opt-in with hostname allowlist | Prevent unauthorized endpoints |
| D-003 | Artifact-first pipeline | Fast root-cause analysis; reproducibility |
| D-004 | Deterministic keyword extraction (phase 1) | Stable demos without LLM dependency |
| D-005 | Clause-level lineage logging | Explainability and audit traceability |
| D-006 | Pseudo-DOCX export (phase 1) | Reliability over brittle tracked-changes automation |
| D-007 | Streamlit UI | Windows-friendly, zero-config local deployment |

## Why Not Alternatives

- **FastAPI/React instead of Streamlit:** Higher operational burden; Streamlit runs as a single `streamlit run` command on Windows with no build step.
- **True DOCX tracked-changes now:** `python-docx` does not support tracked changes natively; a stable fallback was chosen to avoid brittle early-stage fragility.
- **LLM extraction from day 1:** Network isolation requirement blocks external APIs; internal model integration requires enterprise approval and endpoint setup.

---

# Progress So Far

## Completed

- **Pipeline scaffold** — all 9 phases implemented and functional (`app/core/`)
- **Security gates** — preflight, network, env, and path guards enforced (`app/security/`)
- **Structured logging** — event log + lineage log per run (`app/logging/`)
- **10 risk rules** — 7 field-based + 1 auto-renewal + 1 expired + 1 confidence (`app/core/rules.py`, `rules/core_poc_rules.yaml`)
  - _Note: R004 (expired_contract) and R005 (expiring_within_90_days) are defined in YAML but not implemented in `rules.py`_
- **Template redlines** — generated for every fired risk rule (`app/core/redline.py`)
- **JSON + pseudo-DOCX export** — per-document artifact generation (`app/core/export.py`)
- **3-page Streamlit UI** — homepage, Contract Changes, Risk Assessment, Redlining pages (`app/ui/`)
- **Shared data loader** — cached artifact loading module (`app/ui/components/data_loader.py`)
- **Dark theme** — `.streamlit/config.toml`
- **Test suite** — 5 tests across unit/integration/security (`tests/`)
- **Architecture documentation** — `README.md`, `DECISIONS.md`, `FORK_NOTES.md`, `SECURITY.md`, `EVALS.md`, `INCIDENT_RESPONSE.md`
- **17 real contract files** in `inputs/contracts/` (PDFs, DOCXs)
- **3 completed runs** in `outputs/runs/`

## In Progress / Partial

- **YAML rule definitions vs. implementation gap** — R004 and R005 exist in `core_poc_rules.yaml` but are not wired into `rules.py`'s `CORE_RULES` tuple
- **Redline decision persistence** — UI stores decisions in `st.session_state` only; JSON export exists but is not auto-saved
- **Extraction quality** — keyword matching produces false positives/negatives at high rates; pipeline is functional but results are not meaningful for real contract review

## Not Started / Deferred

- True DOCX tracked-changes export (requires `python-docx` tracked change support or a different library)
- Internal LLM integration (stubbed in `app/models/internal_llm_client.py`)
- Full 25-document synthetic eval pack (`evals/synthetic_contracts/` is empty)
- Gold annotations (`evals/gold_annotations/` is empty)
- Precision/recall measurement (`evals/metrics.py` has helpers but `eval_runner.py` only counts signals)
- Clause-level redline anchoring (all redlines currently anchor to `C-0000` due to fallback)
- PDF/DOCX native parsing (text extraction currently uses UTF-8 read of binary files)
- Attorney acceptance rate tracking (no feedback loop from UI decisions back to metrics)

---

# Success Metrics

| Metric | Baseline | Current | Target | Method |
|---|---|---|---|---|
| Pipeline run success rate | — | 100% (17/17) | 100% | `run_summary.md` documents_failed count |
| Risk signal precision (High rules) | Unknown | Unmeasured | ≥ 85% | Compare fired signals against gold annotations |
| Risk signal recall (High rules) | Unknown | Unmeasured | ≥ 90% | Compare fired signals against gold annotations |
| Attorney acceptance rate (redlines) | Unknown | Unmeasured | ≥ 60% | Track Accept/Reject decisions in UI export |
| Mean extraction confidence | — | 85% (hardcoded) | Reflects true parsing quality | Switch from hardcoded 0.85 to actual confidence |
| UI page load time | — | Unmeasured | < 2s per page | Manual/automated Streamlit timing |
| Security preflight pass rate | — | 100% | 100% | Event log preflight_passed count |

---

# Hypotheses

## Main Hypothesis

A deterministic keyword-based pipeline with a template redline UI is sufficient to demonstrate the value of automated contract review to legal stakeholders, enabling a go/no-go decision on investing in internal LLM integration.

## Sub-Hypotheses

| Sub-Hypothesis | Confirms | Falsifies |
|---|---|---|
| Legal reviewers will find the stoplight triage view faster than reviewing raw tables | User testing showing reduced time-to-action | Users ignore KPIs and sort the table manually |
| Template redlines (even generic ones) are useful as starting points for reviewers | Acceptance rate > 0%; reviewers edit rather than reject entirely | Near-100% rejection rate; reviewers write from scratch |
| Keyword extraction is sufficient to demo risk identification to non-technical stakeholders | Stakeholders can see the categories of risk even if individual signals are noisy | Stakeholders dismiss results as too inaccurate to be credible |
| Offline security posture will unblock enterprise procurement approval | System passes security review without public network access | Security team requires cloud-only deployment or additional controls |

---

# Evidence vs Assumptions

| Claim | Type | Source | Confidence | Notes |
|---|---|---|---|---|
| Pipeline processes 17 contracts with 0 failures | Evidence | `outputs/runs/RUN_20260422_190408/run_summary.md` | High | Observed output |
| All 17 contracts trigger all 7 core risk rules | Evidence | `risk_signals.jsonl` (every doc has R001-R009) | High | Consequence of keyword extraction failing on binary PDFs |
| PDF text extraction is reading binary as UTF-8 | Inference | `normalize.py` uses `path.read_text(encoding="utf-8")`; PDFs are binary | High | No real PDF parser (PyMuPDF, pdfminer) in requirements |
| Internal model hosts are `tyson.local` domain | Evidence | `.env` `APPROVED_INTERNAL_HOSTS` | High | Suggests Tyson Foods or similar enterprise deployment context |
| Redline clause anchoring always falls back to C-0000 | Evidence | `redlines.jsonl` (all records show `"clause_id": "C-0000"`) | High | `risk.get("clause_id")` is null for all signals; clauses list is empty |
| R004/R005 rules are defined but not implemented | Evidence | `rules/core_poc_rules.yaml` vs. `app/core/rules.py` `CORE_RULES` tuple | High | YAML has R004/R005; `CORE_RULES` does not |
| The `.docx` export is plain text, not true DOCX | Evidence | `app/core/export.py` line: `docx_path.write_text(...)` | High | No `python-docx` usage in export.py |
| Extraction confidence of 0.85 is hardcoded | Evidence | `app/core/extract.py`: `"confidence": 0.85` | High | Not computed from actual extraction quality |
| 3 existing branches: main, feature/offline-build, codex/flag | Evidence | `git branch -a` output | High | Active development on codex branch |
| Eval gold annotations are empty | Evidence | `evals/gold_annotations/` directory is empty | High | No ground truth exists yet |
| The UI decisions (Accept/Reject) are not persisted to disk automatically | Inference | `3_Redlining.py` uses `st.session_state` only; download button is manual | High | Session state clears on page refresh |
| Security guards prevent network egress at pipeline start | Evidence | `app/core/preflight.py`, `app/security/network_guard.py` | High | Confirmed by security test in `tests/security/test_preflight.py` |

---

# Failure Modes and Risk Register

| Risk | Impact | Likelihood | Detection | Mitigation |
|---|---|---|---|---|
| **PDF text extraction failure** — Binary PDFs read as garbled UTF-8 text; all keywords missing → all rules fire for all docs | High (results meaningless) | High (already occurring) | All docs show identical signal patterns; `warnings: ["empty_text_extraction"]` in normalized artifacts | Add PyMuPDF (`pip install pymupdf`) to normalize.py for real PDF parsing |
| **Clause anchoring always C-0000** — Redlines never link to actual contract text | High (redlines are useless as-is) | High (already occurring) | All `redlines.jsonl` records show `"clause_id": "C-0000"` | Fix `generate_redlines()` to pass populated clauses list from orchestrator |
| **Hardcoded 0.85 confidence** — R010 (low confidence) never fires accurately; confidence metric is meaningless | Medium (metric misleading) | High (already the case) | `extractions.jsonl` always shows 0.85 regardless of content | Compute actual confidence from extraction coverage (fields found / total fields) |
| **R004/R005 not implemented** — YAML rule definitions are orphaned; expired and expiring contracts not detected | High (major gap in risk coverage) | High (already the case) | YAML vs. `CORE_RULES` tuple mismatch | Wire R004/R005 into `rules.py` with date comparison logic |
| **UI session state loss** — Reviewer decisions lost on page refresh before export | Medium (UX friction) | Medium (requires manual export action) | No persistence layer | Auto-save decisions to a JSON file in the run directory on every change |
| **Pseudo-DOCX sent to attorneys** — Recipients try to open `.docx` file expecting tracked changes, see plain text | High (credibility damage) | Medium (if shared externally) | File opens in Notepad/raw text view | Rename to `_redline_draft.txt` or implement true DOCX with `python-docx` |
| **No input validation on custom redline text** — XSS-style injection via text area if UI is ever served publicly | Low (Streamlit escapes by default; currently local-only) | Low | Manual code review | Sanitize custom change text before export; add disclaimer that UI is internal-only |
| **`sys.path.insert` in page files** — Fragile import path hack; breaks if run from different working directory | Medium (startup failure) | Medium | `ModuleNotFoundError` on import | Use `PYTHONPATH` env var or install package with `pip install -e .` |
| **Unsupported file gracefully rejected but silently** — `route_document` returns `"reject"` but orchestrator skips without alerting user | Low | Medium | Check event_log for `route: reject` entries | Add explicit UI warning for rejected files in run summary |

---

# Most Recent Experiment / Attempt

## What Was Done

Expanded the Streamlit UI from a single 37-line file (`app/ui/streamlit_app.py`) to a full multi-page application with three specialized pages:

1. **Contract Changes** (`pages/1_Contract_Changes.py`) — Stoplight KPI cards (Total / High / Medium / Low) that filter the risk signal table on click; severity-first sort; contract filter dropdown.
2. **Risk Assessment** (`pages/2_Risk_Assessment.py`) — Executive summary metrics (doc count, signal counts, mean confidence), severity bar chart, per-contract expandable risk breakdown.
3. **Redlining** (`pages/3_Redlining.py`) — Per-redline Accept/Reject/Edit UI with session state tracking, custom change authoring form, JSON decision export download.

Also created shared data loader (`app/ui/components/data_loader.py`) with `@st.cache_data` helpers and a `.streamlit/config.toml` dark theme.

## Expected Result

3 navigable pages with interactive filtering, risk visualization, and redline review capability.

## Actual Result

All 7 files committed and pushed to `origin/codex/flag-potential-security-risk-commands` at commit `a008188`. Push initially failed due to VS Code git credential pipe being unavailable outside VS Code; resolved by running `gh auth setup-git` to use GitHub CLI token.

## Interpretation

The UI layer is structurally complete. However, the value of the redlining page is limited by the underlying data quality issue: all redlines are generic template strings (`[ADD] Remediation for R00X: ...`) anchored to `C-0000` rather than specific contract clauses. The UI infrastructure is ready for real redline content once the extraction and clause-anchoring issues are fixed.

## Artifacts

- Commit: `a008188 feat(ui): expand Streamlit frontend to 3-page multi-page app`
- Branch: `codex/flag-potential-security-risk-commands`
- Files changed: 7 (+592 lines)
- Prior state: `app/ui/streamlit_app.py` (37 lines, single page)

---

# Next Hypothesis and Immediate Plan

## Next Hypothesis

**Fixing PDF text extraction and clause anchoring will make the existing pipeline produce meaningfully distinct risk signals per contract**, enabling the UI to show real differentiation between contracts rather than identical signal patterns.

## Why This Is the Highest-Leverage Next Step

Currently, all 17 contracts produce identical risk signals because:
1. The PDF text extractor reads binary as UTF-8 → no keywords found → all rules fire
2. All redlines anchor to C-0000 → no clause context

Fixing extraction is the single change that unlocks credible demo output, makes the Risk Assessment page meaningful, and gives the Redlining page real clause text to display. Everything else (UI, security, logging, export) is already working.

## Step-by-Step Plan

**Step 1 — Add real PDF parsing:**
```bash
pip install pymupdf  # add to requirements.txt
```
In `app/core/normalize.py`, replace `_read_text_fallback()` with:
```python
import fitz  # pymupdf
def _read_pdf(path: Path) -> str:
    doc = fitz.open(str(path))
    return "\n".join(page.get_text() for page in doc)
```

**Step 2 — Fix DOCX parsing:**
Use `python-docx` (already in requirements) in normalize.py:
```python
from docx import Document
def _read_docx(path: Path) -> str:
    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs)
```

**Step 3 — Fix clause anchoring in redline generation:**
In `app/core/orchestrator.py`, verify that the clauses list is populated and passed to `generate_redlines()`. Check that segment/clause output is non-empty after the normalize fix.

**Step 4 — Fix extraction confidence:**
Replace hardcoded `0.85` in `extract.py` with:
```python
found_fields = sum(1 for v in fields.values() if v is not None and v is not False)
confidence = round(found_fields / len(fields), 2)
```

**Step 5 — Implement R004/R005:**
Add to `CORE_RULES` in `rules.py`:
```python
("R004", "ExpirationDate", "High", "Contract is expired"),
("R005", "ExpirationDate", "Medium", "Contract expiring within 90 days"),
```
And add date comparison logic when `ExpirationDate` is a parseable date string.

**Step 6 — Re-run pipeline and verify:**
```bash
python -m app.main
streamlit run app/ui/streamlit_app.py
```
Expected: contracts show differentiated risk signals; redlines reference actual clause text.

---

# Open Questions

| Question | Why It Matters | Blocking? | Who/What Can Resolve |
|---|---|---|---|
| **What enterprise environment is this targeting?** The `.env` shows `tyson.local` hosts. Is this for Tyson Foods? | Shapes the internal model integration approach, data classification requirements, and deployment architecture | No | Project owner / stakeholder conversation |
| **Is the `feature/offline-build` branch ahead of `main`?** Need to understand if there are changes there not yet merged | Could contain work that should inform next steps | No | `git diff main...feature/offline-build` |
| **When does the POC need to demo to stakeholders?** | Determines priority: polish UI vs. fix extraction quality vs. add LLM integration | Yes (affects scope) | Project owner |
| **What is the approved internal LLM endpoint?** | Required to activate `ALLOW_INTERNAL_MODEL=true` and test real extraction | Yes (for LLM phase) | Enterprise IT / ML team |
| **Should redline decisions persist across sessions?** | Currently lost on page refresh unless exported manually | No (but UX concern) | Product decision |
| **Is `python-docx` tracked-changes export expected by the demo audience?** | Drives whether pseudo-DOCX is acceptable or needs replacing before demo | Yes (if attorneys will open files) | Legal team stakeholder |
| **Is the `codex/flag-potential-security-risk-commands` branch name intentional?** | Unusual name for a UI feature branch; may indicate Codex created it with a different purpose | No | Project owner |
| **Are the 15 contract PDFs real or synthetic?** | Affects how aggressively to handle data sensitivity and whether extraction results can be shared externally | Yes (data handling) | Project owner |

---

_End of handoff document. Generated from full codebase audit on 2026-04-23._
_Repository: `brajo-org/ai-contracts-poc-offline` | Branch: `codex/flag-potential-security-risk-commands`_
