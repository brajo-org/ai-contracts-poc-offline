# Offline Contract Management System — Fork Build Guide

**Purpose:** Replacement build guide for an **offline-first fork** of the current AI Contracts POC that is descriptive enough to hand to Codex for implementation.

**Primary goal:** Build a stakeholder-safe, Windows-first, offline contract review system that can:
- ingest PDF, DOCX, scanned PDFs with OCR fallback, and limited Excel inputs,
- segment contracts into section hierarchy and clauses,
- call an **internal hosted model only** (Tyson network/VPN),
- run deterministic core POC risk rules,
- generate explainable redlines,
- export a **redlined DOCX artifact** and **JSON diff artifact**,
- operate with **no public internet access**,
- leave durable, searchable logs and clause-level lineage for rapid patching.

This guide is designed as a **fork plan** from the current POC rather than a permanent final architecture. It intentionally prioritizes:
1. End-to-end workflow demo value
2. Redline usefulness
3. Extraction quality
4. Security defensibility
5. Explainability and traceability

It supersedes the hosted-model-centric v3 plan where needed and aligns with the user's offline testing goals, while preserving useful lessons from the current repo and the newer offline alternatives. See the current v3 guide and current repo context in `AI_Contracts_POC_Build_Guide_v3.md`, `CLAUDE.md`, and `HANDOFF.md`, along with the user's newer offline alternatives in `offline_testing_build_plan.md` and `option_a_build_plan_updated.md` fileciteturn0file7 fileciteturn0file2 fileciteturn0file6L1-L18 fileciteturn0file0L1-L16 fileciteturn0file1L1-L18.

---

## 1. What This Fork Is

This fork is a **sandbox-safe contract analysis system** for internal evaluation.

It is not intended to:
- connect to public APIs,
- call external OCR or LLM services,
- push data into Coupa or GCP,
- ingest real production contracts in phase 1,
- run as a permanent enterprise platform.

It **is** intended to:
- prove the end-to-end workflow,
- surface risks deterministically,
- produce reviewable redlines,
- capture enough evidence and logs to defend behavior in a stakeholder demo,
- make failure analysis fast.

---

## 2. Non-Negotiable Constraints

### Network and Security
- **No public internet access** during runtime.
- Internal hosted model access is allowed **only while on Tyson network or VPN**.
- Internal model endpoints must be **disabled by default** and only enabled via explicit environment configuration.
- No telemetry, analytics beacons, crash uploaders, update checks, or background sync.
- No package installs at app runtime.
- No outbound calls except the approved internal model endpoint.

### Platform
- Primary target: **Windows laptop**.
- Secondary target: local VM/container later, but not required for phase 1.
- User should not need Docker knowledge to run the system.

### Data Handling
- Synthetic documents only for phase 1 eval pack.
- Input documents mounted/read from a user-selected local folder.
- No persistence beyond session for contract data.
- Logs and run artifacts are allowed as local files because traceability is required.
- Excel is **input only** in phase 1, mainly for metadata or rule/reference inputs.

### Functional Scope
- Support:
  - native PDF
  - scanned/image PDF with OCR fallback
  - DOCX
  - selected Excel input workbooks
- Contract analysis must preserve:
  - contract-level view
  - section hierarchy
  - clause-level lineage
- Redline outputs must include:
  - JSON diff artifact
  - redlined DOCX artifact

### Failure Behavior
- **Fail closed** on security and environment violations.
- **Continue per document** on parsing/OCR/model issues where safe.
- Never silently downgrade behavior without logging the downgrade.

---

## 3. Forking Strategy

This should be treated as a **fork of the current POC**, not a rewrite from scratch and not a permanent architecture bet.

### What to keep from the current POC
Keep these design ideas from the current build because they are still useful:
- sequential pipeline structure,
- shared logger module,
- contract ID as a stable join key,
- clear output artifacts,
- rules-first risk decisions,
- human-review orientation,
- explicit progress and handoff docs,
- mock/synthetic document generation.

These strengths are already evident in the current repo guidance and session history fileciteturn0file2L1-L18 fileciteturn0file3L1-L22.

### What to change from the current POC
Replace or tighten these areas:
- remove any assumption that general outbound internet is allowed,
- make internal model access optional and environment-gated,
- add stronger environment/network preflight checks,
- expand parsing lineage from simple page maps to section + clause hierarchy,
- add structured event logs and lineage logs,
- add sandbox eval harness and acceptance gates,
- add incident/patch playbook,
- generate redlined DOCX plus JSON diff,
- explicitly document fork workflow and divergence from upstream.

---

## 4. Recommended Architecture

### High-Level Flow

```text
Input Folder
  ↓
Preflight & Security Gate
  ↓
Document Intake
  ↓
Format Router
  ├── PDF text extraction
  ├── OCR fallback for scanned PDFs
  ├── DOCX text extraction
  └── Excel metadata intake
  ↓
Document Normalizer
  ↓
Section + Clause Segmenter
  ↓
Internal Hosted Model Extraction Agent
  ↓
Deterministic Core POC Risk Rules Engine
  ↓
Redline Generator
  ├── JSON diff output
  └── Redlined DOCX output
  ↓
Local Review UI
  ↓
Run Report + Logs + Lineage Artifacts
```

### Architectural Principle
The system should be **modular but linear**. Each step writes a structured local artifact. Every downstream step must be reproducible from upstream artifacts.

That means if redlining is wrong, the user can inspect:
1. the normalized text,
2. the section hierarchy,
3. the clause segmentation,
4. extraction evidence,
5. rule firings,
6. redline instruction payload,
7. final output diff.

---

## 5. Project Structure

```text
contract_management_system/
│
├── README.md
├── PROGRESS.md
├── FORK_NOTES.md
├── SECURITY.md
├── INCIDENT_RESPONSE.md
├── EVALS.md
├── CODEX_BUILD_PROMPT.md
├── requirements.txt
├── config.py
├── .env.example
├── .gitignore
│
├── app/
│   ├── main.py
│   ├── ui/
│   │   ├── streamlit_app.py
│   │   └── components/
│   ├── core/
│   │   ├── preflight.py
│   │   ├── intake.py
│   │   ├── router.py
│   │   ├── normalize.py
│   │   ├── segment.py
│   │   ├── extract.py
│   │   ├── rules.py
│   │   ├── redline.py
│   │   ├── export.py
│   │   └── orchestrator.py
│   ├── models/
│   │   ├── internal_llm_client.py
│   │   └── prompts/
│   ├── logging/
│   │   ├── logger.py
│   │   ├── lineage.py
│   │   └── schemas.py
│   ├── security/
│   │   ├── network_guard.py
│   │   ├── env_guard.py
│   │   └── path_guard.py
│   └── utils/
│
├── rules/
│   ├── core_poc_rules.yaml
│   └── schemas/
│
├── evals/
│   ├── synthetic_contracts/
│   ├── gold_annotations/
│   ├── eval_runner.py
│   ├── metrics.py
│   └── test_cases/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── security/
│   ├── regression/
│   └── fixtures/
│
├── inputs/
│   ├── contracts/
│   └── metadata/
│
├── outputs/
│   ├── runs/
│   ├── latest/
│   └── exports/
│
└── docs/
    ├── architecture/
    ├── evals/
    └── troubleshooting/
```

---

## 6. Required Local Artifacts Per Run

Each run should create a timestamped folder:

```text
outputs/runs/RUN_YYYYMMDD_HHMMSS/
```

Inside it, write:
- `run_manifest.json`
- `environment_snapshot.json`
- `preflight_report.json`
- `intake_manifest.json`
- `normalized_documents.jsonl`
- `section_hierarchy.jsonl`
- `clauses.jsonl`
- `extractions.jsonl`
- `risk_signals.jsonl`
- `redlines.jsonl`
- `redline_exports/`
- `event_log.jsonl`
- `lineage_log.jsonl`
- `application.log`
- `eval_report.json` when eval mode is enabled
- `run_summary.md`

This is the minimum package needed for fast failure diagnosis.

---

## 7. Environment Model

### Approved Runtime Modes

#### Mode 1: Offline Sandbox Mode
- No internet
- No model calls
- Uses cached/sample outputs or deterministic fallback flows for parser/rules/redline smoke tests
- Used for security validation and non-model regression testing

#### Mode 2: Internal Model Mode
- No public internet
- Internal hosted model allowed only on Tyson VPN/network
- Main extraction and redline mode for realistic POC evaluation

### Environment Variables

```env
APP_ENV=local
ALLOW_INTERNAL_MODEL=false
INTERNAL_MODEL_BASE_URL=
INTERNAL_MODEL_API_KEY=
INTERNAL_MODEL_NAME=
NO_PUBLIC_NETWORK=true
LOG_LEVEL=INFO
ENABLE_TELEMETRY=false
INPUT_ROOT=./inputs
OUTPUT_ROOT=./outputs
RULES_PATH=./rules/core_poc_rules.yaml
OCR_ENABLED=true
MAX_DOC_PAGES=250
MAX_DOC_CHARS=500000
```

### Preflight Checks
Before any run, the app must verify:
- required directories exist,
- only approved file types are present,
- `NO_PUBLIC_NETWORK=true`,
- telemetry is disabled,
- internal model settings are complete if model mode is enabled,
- internal model endpoint hostname belongs to approved internal allowlist,
- Tesseract is installed if OCR is enabled,
- output directory is writable,
- input directory is readable,
- temp artifacts are written only under app-controlled temp paths.

If any security preflight fails, the run must **fail closed** before document processing starts.

---

## 8. Supported Inputs

### Phase 1 Supported File Types
- `.pdf`
- `.docx`
- `.xlsx`
- `.xlsm` only if macros are ignored and workbook is read in safe mode

### Excel Scope in Phase 1
Excel is input-only and limited to:
- synthetic metadata lookup tables,
- optional rule reference sheets,
- synthetic contract index/worklist.

The system should **not** attempt to treat Excel as a contract body in phase 1.

### Rejected Inputs
Reject with clear error and log:
- password-protected files,
- encrypted PDFs,
- unsupported file extensions,
- corrupted workbooks,
- files larger than configured max size,
- macro execution requests.

---

## 9. Document Processing Design

### 9.1 Intake
For each file, assign:
- `run_id`
- `document_id`
- `source_filename`
- `source_sha256`
- `file_type`
- `file_size_bytes`
- `ingest_timestamp`

### 9.2 Normalization
Produce normalized text plus page/section references.

Minimum normalized document schema:

```json
{
  "run_id": "RUN_20260421_101500",
  "document_id": "DOC-001",
  "source_filename": "synth_msa_01.pdf",
  "file_type": "pdf",
  "pages": [
    {"page_number": 1, "text": "..."}
  ],
  "normalized_text": "...",
  "warnings": []
}
```

### 9.3 Section Hierarchy and Clause Segmentation
The segmenter must output both:
- **section hierarchy**
- **clause objects**

Minimum section hierarchy schema:

```json
{
  "document_id": "DOC-001",
  "sections": [
    {
      "section_id": "S1",
      "heading": "Term and Termination",
      "level": 1,
      "parent_section_id": null,
      "page_start": 3,
      "page_end": 4
    }
  ]
}
```

Minimum clause schema:

```json
{
  "document_id": "DOC-001",
  "clause_id": "C-0012",
  "section_id": "S1",
  "clause_label": "Termination for Convenience",
  "clause_text": "Either party may terminate...",
  "page_start": 4,
  "page_end": 4,
  "char_start": 10452,
  "char_end": 10890,
  "source_method": "parser|ocr|docx",
  "confidence": 0.94
}
```

### Why this matters
The user explicitly wants logging and documentation that makes patching fast. Clause hierarchy is the difference between:
- “The model was wrong somewhere,” and
- “Rule R007 fired on clause C-0012 under section S1 because the extraction payload contained `LiabilityCap=NOT_FOUND` with evidence on page 4.”

---

## 10. Internal Hosted Model Design

### Policy
- Internal model access is allowed only in **Mode 2**.
- Model client must refuse to run if:
  - the endpoint is not allowlisted,
  - the API key is missing,
  - the hostname is external/public,
  - `ALLOW_INTERNAL_MODEL` is not explicitly true.

### Required Client Behavior
- timeout control,
- retry with capped attempts,
- request and response logging with payload redaction,
- deterministic prompt templates stored in repo,
- model response validation against strict JSON schemas,
- fallback to document-level failure artifact on repeated bad response.

### Strict Output Requirements
For every extracted field or redline suggestion, capture:
- value,
- evidence snippet,
- evidence page,
- clause_id,
- section_id,
- extraction confidence,
- model request ID if available,
- prompt version.

---

## 11. Core POC Rules to Preserve

Keep only the core POC risk rules already implied by the existing POC materials.

Minimum phase 1 rules:
- missing expiration date
- missing contract value
- missing supplier
- expired contract
- expiring within 90 days
- auto-renewal present
- liability cap missing
- business entity missing
- governing law missing
- low confidence extraction

These rule concepts already exist in the current POC guide and should be preserved, just moved into a stricter offline-first runtime and stronger lineage model fileciteturn0file7L295-L307.

### Rule Output Schema

```json
{
  "run_id": "RUN_20260421_101500",
  "document_id": "DOC-001",
  "rule_id": "R007",
  "severity": "High",
  "field_triggered": "LiabilityCap",
  "message": "No liability cap clause found — legal review recommended",
  "evidence": "NOT_FOUND",
  "section_id": "S1",
  "clause_id": "C-0012",
  "rule_inputs": {
    "field_value": "NOT_FOUND",
    "confidence": 0.91
  },
  "fired_at": "2026-04-21T10:15:42"
}
```

---

## 12. Redline Design

### Outputs Required
1. **JSON diff artifact**
2. **Redlined DOCX artifact**

### Redline JSON Schema

```json
{
  "document_id": "DOC-001",
  "clause_id": "C-0012",
  "section_id": "S1",
  "risk_id": "R007",
  "original_text": "Supplier shall be liable for all damages...",
  "proposed_text": "Except for fraud... Supplier's aggregate liability shall not exceed...",
  "rationale": "Introduces a liability cap while preserving core allocation intent.",
  "change_type": "replace",
  "source": "internal_model+template",
  "confidence": 0.82
}
```

### Redlined DOCX Rules
- Each changed clause must be written into a DOCX export.
- The export does not need true Microsoft Word tracked changes in phase 1 if that becomes unstable.
- Acceptable fallback for phase 1:
  - original clause,
  - proposed clause,
  - visible inline insert/delete markers,
  - redline legend,
  - clause/page references.
- If true tracked-changes support is feasible and stable, use it. If not, prefer robust pseudo-redline over brittle automation.

### Important implementation note
The system should not overwrite the source document. Always create a new exported redline artifact.

---

## 13. Local Review UI

Use Streamlit or similarly simple local UI.

### Required Screens
1. **Run Dashboard**
   - run summary
   - document counts
   - failure counts
   - security status
2. **Document Detail**
   - source metadata
   - extracted fields
   - section hierarchy
   - clause browser
   - rule firings
3. **Redline Review**
   - clause-by-clause original vs proposed
   - export buttons
4. **Logs & Traceability**
   - event log filters
   - lineage lookup by document, clause, or rule
   - artifact links

### UI Must Show
- if model mode was enabled,
- whether OCR was used,
- whether any fallbacks occurred,
- which rule fired where,
- which export files were generated.

---

## 14. Logging and Traceability Requirements

The user explicitly wants strong log capture and fast patchability. That means plain app logs are not enough.

### Required Log Layers

#### A. Human-readable application log
- timestamp
- level
- module
- message

#### B. Structured event log (`event_log.jsonl`)
One event per line.

Example:
```json
{"ts":"2026-04-21T10:15:40","run_id":"RUN_...","document_id":"DOC-001","event_type":"ocr_fallback_used","level":"WARNING","details":{"page_count":12}}
```

#### C. Clause-level lineage log (`lineage_log.jsonl`)
One lineage record per major transformation.

Example:
```json
{"run_id":"RUN_...","document_id":"DOC-001","section_id":"S1","clause_id":"C-0012","step":"rule_eval","input_artifact":"extractions.jsonl","output_artifact":"risk_signals.jsonl","rule_id":"R007","reason":"LiabilityCap=NOT_FOUND"}
```

#### D. Run summary report (`run_summary.md`)
Human-readable recap with:
- files processed,
- files failed,
- rules fired,
- exports created,
- warnings/errors,
- recommended follow-up.

### Required Event Types
At minimum:
- `preflight_started`
- `preflight_passed`
- `preflight_failed`
- `document_ingested`
- `document_rejected`
- `pdf_text_extracted`
- `ocr_fallback_used`
- `docx_extracted`
- `excel_metadata_loaded`
- `document_normalized`
- `sections_built`
- `clauses_built`
- `model_extraction_started`
- `model_extraction_succeeded`
- `model_extraction_failed`
- `rule_fired`
- `rule_skipped`
- `redline_generated`
- `redline_exported`
- `document_completed`
- `document_failed`
- `run_completed`

### What to log but redact
- API keys
- full auth headers
- raw secrets
- raw path segments that expose sensitive usernames if avoidable

### What must remain visible
- endpoint hostname category (internal/blocked)
- prompt version
- model name
- clause ids
- section ids
- file hashes
- rule ids
- exception types
- stack traces for local debugging files

---

## 15. Failure Handling Policy

### Fail Closed Immediately On
- public network endpoint detected,
- disallowed environment config,
- telemetry enabled,
- path traversal attempt,
- unsafe output directory,
- unknown model host,
- missing security preflight requirements.

### Continue Per Document On
- OCR failure for a single file,
- unsupported page in one file,
- model extraction failure for one file,
- schema validation failure for one model response,
- DOCX export failure for one file.

### Document Failure Artifact
If a document fails, create a `document_failure.json` entry containing:
- document id
- source filename
- failed step
- exception type
- exception message
- retry count
- suggested remediation

---

## 16. Synthetic Eval Pack Design

The user requested **25 synthetic contracts**.

### Eval Pack Composition
Create 25 synthetic documents across formats:
- 10 text PDFs
- 7 DOCX
- 5 scanned/degraded PDFs
- 3 Excel-linked metadata scenarios

### Core Scenario Coverage
Each scenario should appear at least twice where practical:
- clean contract
- missing liability cap
- auto-renewal present
- missing expiration date
- expired contract
- expiring within 90 days
- governing law missing
- supplier missing
- contract value missing
- business entity missing
- low-confidence extraction wording
- OCR noise / skew / blur
- malformed section numbering
- duplicate clause headings
- exhibit-heavy contract
- appendix with conflicting dates
- short NDA
- long MSA
- SOW with tables
- purchase agreement with renewal language

### Gold Annotation Files
For each synthetic contract, maintain a gold file containing:
- contract-level expected fields
- expected section hierarchy
- expected clause boundaries for key clauses
- expected rule firings
- expected evidence snippets or anchors
- expected redline target clauses

---

## 17. Eval Metrics

### A. Ingestion and Security Metrics
- `% files accepted correctly`
- `% unsupported files rejected correctly`
- `% preflight violations blocked correctly`
- `0 public internet calls allowed`

### B. Parsing Metrics
- section hierarchy accuracy
- clause segmentation accuracy
- page anchor correctness
- OCR fallback trigger correctness

### C. Extraction Metrics
- exact match / normalized match by field
- evidence-page correctness
- clause-id correctness
- null-handling correctness

### D. Rule Metrics
- precision/recall per rule
- expected rule firing coverage
- false-positive count
- false-negative count

### E. Redline Metrics
- `% required redlines produced`
- clause-target correctness
- export success rate for JSON diff
- export success rate for redlined DOCX

### F. Operational Metrics
- run success rate
- mean documents processed before first critical failure
- mean time to identify failure cause from logs
- artifact completeness score

---

## 18. Acceptance Criteria for Sandbox Readiness

The offline fork is ready for stakeholder-safe sandbox review only if all of the following pass.

### Security Gates
- No public internet traffic observed in sandbox.
- Internal model calls only occur when `ALLOW_INTERNAL_MODEL=true` and endpoint is allowlisted.
- Telemetry remains disabled.
- Preflight blocks misconfigured runs.

### Functional Gates
- 25/25 synthetic contracts ingest or fail with expected documented reason.
- At least 95% of supported files route to the correct parser path.
- OCR fallback triggers on degraded scans when expected.
- Clause hierarchy artifacts are generated for at least 90% of documents.
- Core rule engine fires expected rules on at least 90% of gold scenarios.
- JSON diff export success rate ≥ 95%.
- Redlined DOCX export success rate ≥ 90%.

### Traceability Gates
- Every rule firing can be traced to document, section, clause, and evidence.
- Every model extraction output includes evidence reference or explicit null reason.
- Every failed document has a failure artifact.
- Every run writes a run summary and event log.

### Demo Gates
- One clean end-to-end walkthrough completes locally on Windows.
- One noisy/OCR contract walkthrough completes with visible fallback logging.
- One redline export opens successfully in Word.

---

## 19. Sandbox Test Plan

### Test Group 1: Environment and Security
1. Run with `ALLOW_INTERNAL_MODEL=false`.
   - Expected: no model calls.
2. Run with public URL in model config.
   - Expected: preflight fail closed.
3. Run with missing API key while model mode enabled.
   - Expected: preflight fail closed.
4. Run with telemetry flag enabled.
   - Expected: preflight fail closed.
5. Run with unsupported file extension in input folder.
   - Expected: file rejected and logged.

### Test Group 2: Parsing and OCR
6. Native PDF with clear text.
   - Expected: pdf parser path, no OCR.
7. Scanned PDF with low text yield.
   - Expected: OCR fallback event.
8. DOCX with headings and tables.
   - Expected: docx path, hierarchy preserved where possible.
9. Corrupted PDF.
   - Expected: document-level failure artifact, run continues.
10. Excel metadata workbook.
   - Expected: metadata intake only, no contract-body analysis.

### Test Group 3: Extraction and Rules
11. Missing expiration date.
   - Expected: R001 fires.
12. Expired contract.
   - Expected: R004 fires.
13. Expiring within 90 days.
   - Expected: R005 fires.
14. Auto-renewal present.
   - Expected: R006 fires.
15. Liability cap missing.
   - Expected: R007 fires.
16. Missing business entity.
   - Expected: R008 fires.
17. Low-confidence extraction.
   - Expected: R010 fires.

### Test Group 4: Redline and Export
18. Liability cap missing scenario.
   - Expected: JSON diff and DOCX redline both created.
19. Multiple risky clauses in one document.
   - Expected: each risky clause exported with separate references.
20. Export with special characters and numbering.
   - Expected: output readable, references preserved.

### Test Group 5: Logging and Recoverability
21. Force model timeout on one document.
   - Expected: timeout logged, document failure artifact produced, run continues.
22. Force schema-invalid model response.
   - Expected: retry then document failure or fallback, both logged.
23. Force DOCX export failure.
   - Expected: JSON diff still persists if possible, export failure logged.
24. Verify lineage lookup.
   - Expected: can trace one rule firing back to clause and evidence.
25. Re-run same eval pack.
   - Expected: artifact set comparable, failures reproducible.

---

## 20. Testing Criteria Table

| Area | Test | Pass Criteria |
|---|---|---|
| Security | Public endpoint configured | Run blocked before processing |
| Security | Internal endpoint allowlisted | Run allowed only with explicit model flag |
| Intake | Unsupported file present | File rejected, event logged |
| Parsing | Text PDF | Text extracted without OCR |
| Parsing | Degraded scan PDF | OCR fallback triggered and logged |
| Segmentation | Structured MSA | Section + clause outputs created |
| Extraction | Missing expiration | Null captured or rule-ready missing signal |
| Rules | Liability cap missing | R007 fires with evidence anchor |
| Redline | Risky clause | JSON diff and DOCX export created |
| Logging | Failed document | Failure artifact + event log + summary entry |
| Traceability | Rule lookup | Can trace rule to clause/page/snippet |
| Demo | End-to-end run | One local walkthrough completes without manual patching |

---

## 21. Required Automated Tests

### Unit Tests
- file routing
- text normalization
- section parsing
- clause segmentation
- rule evaluation
- JSON schema validation
- path guarding
- environment validation
- lineage record generation

### Integration Tests
- intake → normalize → segment
- segment → extract → rules
- rules → redline → export
- OCR fallback path
- end-to-end run on small fixture pack

### Security Tests
- public endpoint rejection
- missing env rejection
- blocked telemetry flag
- path traversal rejection
- temp file containment

### Regression Tests
- known synthetic contracts from eval pack
- fixed bugs become locked regression tests

---

## 22. Incident Response and Patch Workflow

When something goes wrong, the user wants to identify and patch it fast.

### Triage Order
1. Open `run_summary.md`
2. Check `preflight_report.json`
3. Filter `event_log.jsonl` for `level=ERROR` and target `document_id`
4. Inspect `document_failure.json` if present
5. Trace the affected `clause_id` in `lineage_log.jsonl`
6. Open the upstream artifact referenced there
7. Patch the narrowest responsible layer

### Patch Categories
- parser bug
- OCR bug
- segmentation bug
- prompt bug
- schema validation bug
- rule bug
- export bug
- environment/config bug

### Required Patch Documentation
Every fix should append an entry to `PROGRESS.md` and, if it changes behavior, update:
- `FORK_NOTES.md`
- regression tests
- `EVALS.md` if acceptance logic changed

---

## 23. Git Fork Workflow for a Beginner

The user asked for beginner-friendly fork documentation with exact commands.

### Recommended Branch Strategy
- `main` = your fork's stable demo branch
- `feature/offline-build` = the main build branch for this work
- optional short-lived bugfix branches later

### A. Fork the Repo on GitHub
1. Open the upstream repo in GitHub.
2. Click **Fork**.
3. Create the fork under your own GitHub account.

### B. Clone Your Fork Locally
Replace placeholders with your repo values.

```bash
git clone https://github.com/YOUR_USERNAME/ai-contracts-poc-offline.git
cd ai-contracts-poc-offline
```

### C. Add the Original Repo as `upstream`

```bash
git remote add upstream https://github.com/ORIGINAL_OWNER/ORIGINAL_REPO.git
git remote -v
```

Expected result:
- `origin` points to your fork
- `upstream` points to the original repo

### D. Create the Main Offline Work Branch

```bash
git checkout -b feature/offline-build
```

### E. First Commit Structure

```bash
git add .
git commit -m "Initialize offline fork scaffolding"
git push -u origin feature/offline-build
```

### F. Sync Your Fork with Upstream Later
First fetch upstream changes:

```bash
git fetch upstream
```

Update your local `main` branch:

```bash
git checkout main
git merge upstream/main
```

Push updated `main` to your fork:

```bash
git push origin main
```

If your work branch needs those changes too:

```bash
git checkout feature/offline-build
git merge main
```

### G. Create a PR from Your Branch into Your Fork's Main

```bash
git checkout feature/offline-build
git push origin feature/offline-build
```

Then open GitHub and create a pull request from:
- `feature/offline-build` → `main`

### H. Recommended Beginner Safety Checks
Before every push:

```bash
git status
git diff --stat
git branch
git remote -v
```

### I. How to Document the Fork Divergence
Create `FORK_NOTES.md` with these sections:
- original upstream repo
- date of fork
- purpose of fork
- differences from upstream
- what is temporary vs strategic
- how to sync upstream safely

### J. Suggested `FORK_NOTES.md` Starter Template

```md
# Fork Notes

## Upstream
- Repo: ORIGINAL_OWNER/ORIGINAL_REPO
- Forked on: YYYY-MM-DD

## Purpose of This Fork
Offline-first Windows-safe contract management sandbox with internal-model-only access.

## Major Differences from Upstream
- Public internet blocked
- Internal hosted model allowlisted only
- Stronger preflight checks
- Clause hierarchy + lineage logs
- JSON diff + redlined DOCX export
- Synthetic eval harness

## Sync Strategy
- Upstream changes reviewed manually before merge into this fork
- Security-sensitive files reviewed before accepting upstream updates
```

---

## 24. Suggested Build Sequence for Codex

### Phase 1 — Scaffold and Security Gate
Build:
- repo structure
- config
- env handling
- preflight checks
- network guard
- path guard
- logger skeleton

### Phase 2 — Intake and Parsing
Build:
- intake
- router
- PDF/DOCX parsing
- OCR fallback
- Excel metadata intake
- normalization artifacts

### Phase 3 — Section and Clause Hierarchy
Build:
- heading detection
- hierarchy builder
- clause segmenter
- clause artifact schemas

### Phase 4 — Internal Model Extraction
Build:
- allowlisted model client
- strict prompt templates
- response schema validation
- retry/failure behavior

### Phase 5 — Rules Engine
Build:
- core POC rules
- risk signal artifacts
- lineage records

### Phase 6 — Redline Engine and Exports
Build:
- redline generator
- JSON diff export
- DOCX redline export

### Phase 7 — UI, Evals, and Incident Docs
Build:
- local UI
- eval harness
- run summary
- incident playbook
- docs

---

## 25. Codex-Ready Build Prompt

Save this as `CODEX_BUILD_PROMPT.md` and give it to Codex.

```md
Build an offline-first Windows-compatible contract management sandbox as a fork of the current AI Contracts POC.

Requirements:
- No public internet access.
- Internal hosted model calls allowed only when explicitly enabled and only to an allowlisted Tyson/VPN endpoint.
- Primary platform is Windows laptop. Do not require Docker.
- Support PDF, scanned PDF with OCR fallback, DOCX, and limited Excel metadata inputs.
- Build a linear modular pipeline with local artifacts at every stage.
- Preserve both section hierarchy and clause-level segmentation.
- Generate deterministic core POC risk rules only:
  - missing expiration date
  - missing contract value
  - missing supplier
  - expired contract
  - expiring within 90 days
  - auto-renewal present
  - liability cap missing
  - missing business entity
  - missing governing law
  - low confidence extraction
- Generate both:
  1. redline JSON diff artifacts
  2. redlined DOCX exports
- Add strong logging:
  - application.log
  - event_log.jsonl
  - lineage_log.jsonl
  - run_summary.md
  - document_failure.json entries when applicable
- Every rule firing must be traceable to document_id, section_id, clause_id, page anchor, and evidence snippet.
- Every model extraction must include evidence or explicit null reason.
- Fail closed on security misconfiguration; continue per document on safe document-level failures.
- Include a Streamlit UI for local review.
- Include a 25-document synthetic eval pack, gold annotations, eval runner, metrics, unit tests, integration tests, security tests, and regression tests.
- Include beginner-friendly Git fork documentation and FORK_NOTES.md.

Deliverables:
- runnable local repo
- README.md
- SECURITY.md
- INCIDENT_RESPONSE.md
- EVALS.md
- FORK_NOTES.md
- CODEX_BUILD_PROMPT.md
- tests and eval fixtures

Implementation notes:
- use strict JSON schemas for internal model outputs
- validate model responses before downstream use
- never overwrite source files
- create timestamped run artifact folders
- keep prompts versioned in the repo
- optimize for debuggability over elegance
```

---

## 26. Why This Is Better Than the Current v3 Plan for the Offline Fork

The current v3 guide is good for getting a local demo moving, but it still assumes a more open model-access pattern, Excel artifact flow, and simpler lineage. It was built for fast POC execution rather than security-validated offline testing. That is clear in the existing build guide, handoff, and progress notes fileciteturn0file7L1-L18 fileciteturn0file6L1-L18 fileciteturn0file3L1-L22.

Your newer alternative plans move in the right direction by emphasizing offline execution, determinism, traceability, and a composable stack, but they are still too high-level to hand directly to Codex as a build spec. They outline the shape of the solution, not the implementation contract. That gap is visible in both alternative plan docs fileciteturn0file0L1-L16 fileciteturn0file1L1-L18.

This replacement guide closes that gap by specifying:
- runtime modes,
- preflight logic,
- fork strategy,
- exact artifacts,
- logging layers,
- clause-level lineage,
- eval pack design,
- acceptance gates,
- sandbox tests,
- patch workflow,
- Codex-ready build instructions.

---

## 27. Final Recommendation

Build this as a **security-aware forked sandbox**, not as the final platform.

That gives you the right balance:
- enough end-to-end functionality to impress stakeholders,
- enough offline discipline to reduce security concerns,
- enough logging to patch quickly,
- enough modularity to throw away or evolve parts later.

If this fork performs well in sandbox testing, then you can decide whether to:
1. merge concepts back into the main POC,
2. keep it as a hardened demo branch,
3. or treat it as the seed of a more formal product.
