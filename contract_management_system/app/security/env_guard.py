from __future__ import annotations

from config import Settings

from .network_guard import SecurityError


def validate_env(settings: Settings) -> None:
    if settings.enable_telemetry:
        raise SecurityError("ENABLE_TELEMETRY must be false.")
    if settings.max_doc_pages <= 0 or settings.max_doc_chars <= 0:
        raise SecurityError("MAX_DOC_PAGES and MAX_DOC_CHARS must be positive integers.")
