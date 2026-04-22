from __future__ import annotations

import re


HEADING_PATTERN = re.compile(r"^(\d+(?:\.\d+)*)\s+(.+)$")


def build_sections_and_clauses(normalized_doc: dict) -> tuple[dict, list[dict]]:
    text = normalized_doc["normalized_text"]
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    sections = []
    clauses = []
    current_section_id = "S0"
    sections.append(
        {
            "section_id": current_section_id,
            "heading": "Preamble",
            "level": 1,
            "parent_section_id": None,
            "page_start": 1,
            "page_end": 1,
        }
    )

    clause_idx = 1
    section_idx = 1
    for line in lines:
        match = HEADING_PATTERN.match(line)
        if match:
            current_section_id = f"S{section_idx}"
            section_idx += 1
            sections.append(
                {
                    "section_id": current_section_id,
                    "heading": match.group(2),
                    "level": match.group(1).count(".") + 1,
                    "parent_section_id": None,
                    "page_start": 1,
                    "page_end": 1,
                }
            )
            continue

        clauses.append(
            {
                "document_id": normalized_doc["document_id"],
                "clause_id": f"C-{clause_idx:04d}",
                "section_id": current_section_id,
                "clause_label": line[:64],
                "clause_text": line,
                "page_start": 1,
                "page_end": 1,
                "char_start": text.find(line),
                "char_end": text.find(line) + len(line),
                "source_method": "parser",
                "confidence": 0.9,
            }
        )
        clause_idx += 1

    return {"document_id": normalized_doc["document_id"], "sections": sections}, clauses
