from __future__ import annotations


def route_document(file_type: str) -> str:
    if file_type == "pdf":
        return "pdf"
    if file_type == "docx":
        return "docx"
    if file_type in {"xlsx", "xlsm"}:
        return "excel"
    return "reject"
