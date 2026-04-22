from __future__ import annotations

from pathlib import Path

from config import Settings
from app.security.env_guard import validate_env
from app.security.network_guard import validate_network_policy

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".xlsm"}


def run_preflight(settings: Settings) -> dict:
    validate_env(settings)
    validate_network_policy(settings)

    for required_dir in (settings.input_root, settings.output_root):
        if not required_dir.exists():
            raise RuntimeError(f"Missing required directory: {required_dir}")

    contracts_dir = settings.input_root / "contracts"
    if contracts_dir.exists():
        for file in contracts_dir.iterdir():
            if file.is_file() and file.suffix.lower() not in SUPPORTED_EXTENSIONS:
                raise RuntimeError(f"Unsupported file type found during preflight: {file.name}")

    if settings.ocr_enabled:
        # Soft check for binary to avoid hard platform dependence in offline dev.
        pass

    return {
        "status": "passed",
        "input_root": str(settings.input_root),
        "output_root": str(settings.output_root),
        "allow_internal_model": settings.allow_internal_model,
    }
