from __future__ import annotations

from pathlib import Path

from .logger import append_jsonl
from .schemas import LineageRecord


def log_lineage(path: Path, record: LineageRecord) -> None:
    append_jsonl(path, record.to_dict())
