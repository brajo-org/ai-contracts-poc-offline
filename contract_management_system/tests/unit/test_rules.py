from app.core.rules import evaluate_rules


def test_rules_fire_for_missing_fields():
    extraction = {
        "run_id": "RUN_X",
        "document_id": "DOC-1",
        "fields": {
            "ExpirationDate": None,
            "ContractValue": None,
            "Supplier": None,
            "AutoRenewal": True,
            "LiabilityCap": None,
            "BusinessEntity": None,
            "GoverningLaw": None,
        },
        "confidence": 0.8,
    }
    out = evaluate_rules(extraction, "C-1", "S1")
    ids = {o["rule_id"] for o in out}
    assert "R001" in ids
    assert "R007" in ids
    assert "R010" in ids
