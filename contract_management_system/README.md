# Offline Contract Management System (Fork Scaffold)

Offline-first fork scaffold for contract analysis with deterministic risk checks, redline artifacts, and local traceability logs.

## What is implemented
- Modular pipeline: preflight → intake → route → normalize → segment → extract → rules → redline → export.
- Security guards for network/env policy and fail-closed preflight.
- Required run artifacts in timestamped folders under `outputs/runs/`.
- Structured logs: `application.log`, `event_log.jsonl`, `lineage_log.jsonl`.
- Local review UI via Streamlit.
- Starter test suite (unit + integration + security).

## Design decisions
See `DECISIONS.md` for decisions and rationale, including security posture and phase-1 redline/export strategy.

## Quickstart
1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env`.
4. Put test files in:
   - `inputs/contracts`
   - `inputs/metadata`
5. Run pipeline:
   ```bash
   python -m app.main
   ```
6. Launch local UI:
   ```bash
   streamlit run app/ui/streamlit_app.py
   ```

## Artifacts per run
Each run writes to `outputs/runs/RUN_YYYYMMDD_HHMMSS/`:
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
- `run_summary.md`

## Security posture
- Public internet access is blocked by policy (`NO_PUBLIC_NETWORK=true`).
- Internal model calls are disabled by default and require explicit allowlisted configuration.
- Telemetry must remain disabled.
- Unsupported file types are rejected during preflight.

## Current limitations (phase 1 scaffold)
- Parser quality is intentionally minimal in this scaffold.
- Redline DOCX is a stable fallback export (pseudo-redline content).
- Eval pack is starter-level and not yet full 25-document coverage.
