from __future__ import annotations

import json
from pathlib import Path


def export_redlines(document_id: str, redlines: list[dict], export_dir: Path) -> dict:
    export_dir.mkdir(parents=True, exist_ok=True)
    json_path = export_dir / f"{document_id}_redlines.json"
    docx_path = export_dir / f"{document_id}_redline.docx"

    json_path.write_text(json.dumps(redlines, indent=2), encoding="utf-8")
    # phase-1 pseudo-redline in docx extension for stability
    lines = ["REDLINE LEGEND", "[DEL]=removed [ADD]=added", ""]
    for r in redlines:
        lines.append(f"Clause: {r['clause_id']} Risk: {r['risk_id']}")
        lines.append(f"ORIGINAL: {r['original_text']}")
        lines.append(f"PROPOSED: {r['proposed_text']}")
        lines.append("")
    docx_path.write_text("\n".join(lines), encoding="utf-8")

    return {"json_diff": str(json_path), "redlined_docx": str(docx_path)}
