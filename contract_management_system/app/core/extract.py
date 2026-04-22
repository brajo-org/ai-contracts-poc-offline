from __future__ import annotations

from datetime import datetime, timezone


def extract_fields_offline(normalized_doc: dict, clauses: list[dict]) -> dict:
    text = normalized_doc["normalized_text"].lower()

    def has(term: str) -> bool:
        return term.lower() in text

    return {
        "run_id": normalized_doc["run_id"],
        "document_id": normalized_doc["document_id"],
        "fields": {
            "ExpirationDate": None if "expiration" not in text else "FOUND",
            "ContractValue": None if "value" not in text and "$" not in text else "FOUND",
            "Supplier": None if "supplier" not in text else "FOUND",
            "AutoRenewal": has("auto-renew") or has("automatically renew"),
            "LiabilityCap": None if "liability cap" not in text else "FOUND",
            "BusinessEntity": None if "llc" not in text and "inc" not in text else "FOUND",
            "GoverningLaw": None if "governing law" not in text else "FOUND",
        },
        "confidence": 0.85,
        "ts": datetime.now(timezone.utc).isoformat(),
        "evidence": clauses[:3],
        "prompt_version": "offline-deterministic-v1",
    }
