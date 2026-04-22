from __future__ import annotations

from datetime import datetime, timezone


CORE_RULES = [
    ("R001", "ExpirationDate", "High", "Missing expiration date"),
    ("R002", "ContractValue", "Medium", "Missing contract value"),
    ("R003", "Supplier", "High", "Missing supplier"),
    ("R006", "AutoRenewal", "Medium", "Auto-renewal present"),
    ("R007", "LiabilityCap", "High", "No liability cap clause found — legal review recommended"),
    ("R008", "BusinessEntity", "Medium", "Business entity missing"),
    ("R009", "GoverningLaw", "Low", "Governing law missing"),
]


def evaluate_rules(extraction: dict, first_clause: str | None = None, first_section: str | None = None) -> list[dict]:
    fields = extraction["fields"]
    out = []
    for rule_id, field, severity, message in CORE_RULES:
        value = fields.get(field)
        fire = (value is None) or (field == "AutoRenewal" and value is True)
        if not fire:
            continue
        out.append(
            {
                "run_id": extraction["run_id"],
                "document_id": extraction["document_id"],
                "rule_id": rule_id,
                "severity": severity,
                "field_triggered": field,
                "message": message,
                "evidence": "NOT_FOUND" if value is None else str(value),
                "section_id": first_section,
                "clause_id": first_clause,
                "rule_inputs": {"field_value": value, "confidence": extraction["confidence"]},
                "fired_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    if extraction["confidence"] < 0.9:
        out.append(
            {
                "run_id": extraction["run_id"],
                "document_id": extraction["document_id"],
                "rule_id": "R010",
                "severity": "Low",
                "field_triggered": "ExtractionConfidence",
                "message": "Low confidence extraction",
                "evidence": extraction["confidence"],
                "section_id": first_section,
                "clause_id": first_clause,
                "rule_inputs": {"field_value": extraction["confidence"], "confidence": extraction["confidence"]},
                "fired_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    return out
