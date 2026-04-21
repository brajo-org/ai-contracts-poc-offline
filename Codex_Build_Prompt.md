Codex_Build_Prompt.md

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
