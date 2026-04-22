from __future__ import annotations


def generate_redlines(risks: list[dict], clauses: list[dict]) -> list[dict]:
    clause_map = {c["clause_id"]: c for c in clauses}
    redlines = []
    for risk in risks:
        cid = risk.get("clause_id") or (clauses[0]["clause_id"] if clauses else "C-0000")
        clause = clause_map.get(cid, {"clause_text": ""})
        redlines.append(
            {
                "document_id": risk["document_id"],
                "clause_id": cid,
                "section_id": risk.get("section_id"),
                "risk_id": risk["rule_id"],
                "original_text": clause.get("clause_text", ""),
                "proposed_text": f"[ADD] Remediation for {risk['rule_id']}: {risk['message']}",
                "rationale": "Template redline produced from deterministic risk signal.",
                "change_type": "replace",
                "source": "internal_model+template" if False else "template",
                "confidence": 0.8,
            }
        )
    return redlines
