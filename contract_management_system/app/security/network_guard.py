from __future__ import annotations

from urllib.parse import urlparse

from config import Settings


class SecurityError(RuntimeError):
    pass


def validate_network_policy(settings: Settings) -> None:
    if not settings.no_public_network:
        raise SecurityError("NO_PUBLIC_NETWORK must be true.")

    if settings.allow_internal_model:
        if not settings.internal_model_base_url:
            raise SecurityError("INTERNAL_MODEL_BASE_URL is required when model mode is enabled.")
        parsed = urlparse(settings.internal_model_base_url)
        if parsed.scheme not in {"https", "http"}:
            raise SecurityError("Internal model URL must be http/https.")
        if not parsed.hostname:
            raise SecurityError("Internal model URL hostname is required.")
        if parsed.hostname not in settings.approved_internal_hosts:
            raise SecurityError(f"Host '{parsed.hostname}' is not allowlisted.")
        if not settings.internal_model_api_key:
            raise SecurityError("INTERNAL_MODEL_API_KEY missing for enabled model mode.")
    else:
        if settings.internal_model_base_url:
            return
