from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_env: str
    allow_internal_model: bool
    internal_model_base_url: str
    internal_model_api_key: str
    internal_model_name: str
    no_public_network: bool
    log_level: str
    enable_telemetry: bool
    input_root: Path
    output_root: Path
    rules_path: Path
    ocr_enabled: bool
    max_doc_pages: int
    max_doc_chars: int
    approved_internal_hosts: tuple[str, ...]


def load_settings() -> Settings:
    approved_hosts = tuple(
        h.strip() for h in os.getenv("APPROVED_INTERNAL_HOSTS", "").split(",") if h.strip()
    )
    return Settings(
        app_env=os.getenv("APP_ENV", "local"),
        allow_internal_model=_get_bool("ALLOW_INTERNAL_MODEL", False),
        internal_model_base_url=os.getenv("INTERNAL_MODEL_BASE_URL", ""),
        internal_model_api_key=os.getenv("INTERNAL_MODEL_API_KEY", ""),
        internal_model_name=os.getenv("INTERNAL_MODEL_NAME", ""),
        no_public_network=_get_bool("NO_PUBLIC_NETWORK", True),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        enable_telemetry=_get_bool("ENABLE_TELEMETRY", False),
        input_root=Path(os.getenv("INPUT_ROOT", "./inputs")),
        output_root=Path(os.getenv("OUTPUT_ROOT", "./outputs")),
        rules_path=Path(os.getenv("RULES_PATH", "./rules/core_poc_rules.yaml")),
        ocr_enabled=_get_bool("OCR_ENABLED", True),
        max_doc_pages=int(os.getenv("MAX_DOC_PAGES", "250")),
        max_doc_chars=int(os.getenv("MAX_DOC_CHARS", "500000")),
        approved_internal_hosts=approved_hosts,
    )
