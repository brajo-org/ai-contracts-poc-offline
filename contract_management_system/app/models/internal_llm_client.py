from __future__ import annotations

from config import Settings


class InternalLLMClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    def extract(self, payload: dict) -> dict:
        if not self.settings.allow_internal_model:
            raise RuntimeError("Internal model mode is disabled.")
        # Stubbed for offline fork scaffold.
        return {"status": "stub", "payload_keys": sorted(payload.keys())}
