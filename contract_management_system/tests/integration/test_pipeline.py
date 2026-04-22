from pathlib import Path

from app.core.orchestrator import run_pipeline


def test_pipeline_creates_run(monkeypatch, tmp_path: Path):
    input_root = tmp_path / "inputs"
    output_root = tmp_path / "outputs"
    (input_root / "contracts").mkdir(parents=True)
    (input_root / "metadata").mkdir(parents=True)
    output_root.mkdir(parents=True)
    (input_root / "contracts" / "doc.pdf").write_text("1 Header\nSupplier shall provide services.", encoding="utf-8")

    monkeypatch.setenv("INPUT_ROOT", str(input_root))
    monkeypatch.setenv("OUTPUT_ROOT", str(output_root))
    monkeypatch.setenv("NO_PUBLIC_NETWORK", "true")
    monkeypatch.setenv("ENABLE_TELEMETRY", "false")
    monkeypatch.setenv("ALLOW_INTERNAL_MODEL", "false")

    run_dir = run_pipeline()
    assert (run_dir / "run_manifest.json").exists()
    assert (run_dir / "risk_signals.jsonl").exists()
