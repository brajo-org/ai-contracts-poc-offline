# Fork Notes

## Upstream
- Repo: AI Contracts POC (offline fork context)
- Forked on: 2026-04-21

## Purpose of This Fork
Offline-first Windows-safe contract management sandbox with internal-model-only allowlisted access.

## Major Differences from Upstream
- Public internet blocked by preflight policy
- Internal hosted model gate via explicit env vars
- Clause hierarchy + lineage log artifacts
- JSON diff + pseudo-redlined DOCX export
- Deterministic fallback extraction and rule evaluation

## Sync Strategy
- Review upstream manually before merges into this fork.
- Security-sensitive modules (preflight/network) receive explicit review on sync.
