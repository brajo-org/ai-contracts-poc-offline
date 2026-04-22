import os
from pathlib import Path

from app.core.preflight import run_preflight
from config import load_settings


def test_preflight_blocks_telemetry(tmp_path: Path, monkeypatch):
    (tmp_path / "inputs" / "contracts").mkdir(parents=True)
    (tmp_path / "outputs").mkdir(parents=True)
    monkeypatch.setenv("INPUT_ROOT", str(tmp_path / "inputs"))
    monkeypatch.setenv("OUTPUT_ROOT", str(tmp_path / "outputs"))
    monkeypatch.setenv("ENABLE_TELEMETRY", "true")
    settings = load_settings()
    try:
        run_preflight(settings)
        assert False, "Expected preflight failure"
    except RuntimeError:
        pass
