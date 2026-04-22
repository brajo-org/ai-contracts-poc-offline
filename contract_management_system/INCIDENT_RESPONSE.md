# Incident Response

## Triage
1. Open `outputs/runs/<run_id>/run_summary.md`.
2. Review `preflight_report.json`.
3. Filter `event_log.jsonl` for errors.
4. Read `document_failure.json` entries.
5. Use `lineage_log.jsonl` to trace rule-to-clause lineage.

## Patch Workflow
- Patch smallest responsible module.
- Add/extend regression tests.
- Update `PROGRESS.md` and `FORK_NOTES.md` when behavior changes.
