# Security Controls

- `NO_PUBLIC_NETWORK` must be true.
- Internal model disabled by default.
- Internal model can run only when `ALLOW_INTERNAL_MODEL=true` and hostname is allowlisted.
- Telemetry must be disabled (`ENABLE_TELEMETRY=false`).
- Unsupported files are rejected.
- Output artifacts stay local under `outputs/`.
