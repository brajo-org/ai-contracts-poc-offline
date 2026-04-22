# Evals and Coverage Status

## Current status
- ✅ Baseline automated tests exist for routing, rule firing, preflight security checks, and end-to-end pipeline artifact creation.
- ⚠️ Full 25-document synthetic evaluation pack is not complete yet.

## Implemented tests
- Unit: router and rules behavior.
- Integration: end-to-end run writes expected artifacts.
- Security: telemetry policy rejection in preflight.

## Next expansion tasks
1. Add full 25 synthetic contracts split by format (PDF, DOCX, scanned PDF, Excel metadata scenarios).
2. Add gold annotations per document for expected fields, clause anchors, and rule firings.
3. Add metric computations for parsing, extraction, rules, and redline quality.
4. Add regression fixtures for every fixed bug category (parser, segmentation, export, security).
