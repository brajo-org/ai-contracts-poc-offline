from __future__ import annotations

from pathlib import Path


def _read_text_fallback(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def normalize_document(record: dict, parser_path: str) -> dict:
    path = Path(record["source_path"])
    text = _read_text_fallback(path)
    if parser_path == "excel":
        text = f"EXCEL_METADATA_ONLY::{record['source_filename']}"

    page = {"page_number": 1, "text": text[:10000]}
    return {
        "run_id": record["run_id"],
        "document_id": record["document_id"],
        "source_filename": record["source_filename"],
        "file_type": record["file_type"],
        "pages": [page],
        "normalized_text": text,
        "warnings": [] if text else ["empty_text_extraction"],
    }
