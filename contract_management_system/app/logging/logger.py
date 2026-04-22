from __future__ import annotations

import json
import logging
from pathlib import Path

from .schemas import EventRecord


def build_logger(log_path: Path, level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(f"contract_management.{log_path}")
    logger.setLevel(level.upper())
    logger.handlers.clear()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.propagate = False
    return logger


def append_jsonl(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


def log_event(path: Path, event: EventRecord) -> None:
    append_jsonl(path, event.to_dict())
