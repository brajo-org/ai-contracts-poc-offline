from __future__ import annotations

import json
from pathlib import Path


def run_eval(run_dir: Path) -> dict:
    risk_file = run_dir / "risk_signals.jsonl"
    count = 0
    if risk_file.exists():
        count = len([l for l in risk_file.read_text(encoding="utf-8").splitlines() if l.strip()])
    report = {"risk_signal_count": count, "status": "ok"}
    (run_dir / "eval_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
