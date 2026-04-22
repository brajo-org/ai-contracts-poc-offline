# Architecture & Implementation Decisions

_Last updated: 2026-04-21_

This file records build decisions for the offline fork so behavior is auditable and easy to patch.

## D-001: Offline-first runtime with fail-closed preflight
- **Decision:** `NO_PUBLIC_NETWORK=true` and `ENABLE_TELEMETRY=false` are mandatory; runs fail before processing if violated.
- **Why:** Avoid accidental internet egress and enforce sandbox-safe execution.
- **Implemented in:** `app/security/network_guard.py`, `app/security/env_guard.py`, `app/core/preflight.py`.

## D-002: Internal model access is opt-in and allowlisted
- **Decision:** Internal model calls are disabled by default and require explicit env + hostname allowlist + API key.
- **Why:** Prevent unauthorized endpoints and accidental data leakage.
- **Implemented in:** `app/security/network_guard.py`, `.env.example`.

## D-003: Artifact-first linear pipeline
- **Decision:** Every major phase writes local artifacts to `outputs/runs/RUN_...`.
- **Why:** Fast root-cause analysis and reproducibility.
- **Implemented in:** `app/core/orchestrator.py`.

## D-004: Deterministic extraction/rules baseline for offline mode
- **Decision:** Use deterministic extraction + rules for phase-1 baseline; internal model integration remains a controlled extension path.
- **Why:** Stable demos and repeatable behavior in no-network conditions.
- **Implemented in:** `app/core/extract.py`, `app/core/rules.py`.

## D-005: Clause-level lineage for explainability
- **Decision:** Rule firings include clause/section anchors and are logged to `lineage_log.jsonl`.
- **Why:** Support rapid debugging and traceability requirements.
- **Implemented in:** `app/logging/lineage.py`, `app/core/orchestrator.py`.

## D-006: Redline export fallback
- **Decision:** Provide JSON diff + pseudo-redline DOCX-formatted artifact in phase 1.
- **Why:** Prioritize reliability over brittle tracked-changes automation early.
- **Implemented in:** `app/core/export.py`.

## D-007: Streamlit local review UI
- **Decision:** Use a simple local UI for run summaries/artifact inspection.
- **Why:** Windows-friendly, low operational burden.
- **Implemented in:** `app/ui/streamlit_app.py`.

## Open follow-ups
1. Replace pseudo-DOCX with true tracked changes once a stable writer path is validated.
2. Expand fixture pack to full 25 synthetic contracts + gold annotations.
3. Add stronger parser backends for native PDF/DOCX/XLSX extraction quality.
