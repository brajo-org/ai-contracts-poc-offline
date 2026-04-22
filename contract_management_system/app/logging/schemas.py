from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class EventRecord:
    run_id: str
    event_type: str
    level: str
    details: dict[str, Any] = field(default_factory=dict)
    document_id: str | None = None
    ts: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LineageRecord:
    run_id: str
    document_id: str
    step: str
    input_artifact: str
    output_artifact: str
    section_id: str | None = None
    clause_id: str | None = None
    rule_id: str | None = None
    reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
