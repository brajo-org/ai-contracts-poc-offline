from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

SEVERITY_ORDER = {"High": 1, "Medium": 2, "Low": 3}


@st.cache_data
def get_all_runs(base_path: str = "outputs/runs") -> list[Path]:
    base = Path(base_path)
    if not base.exists():
        return []
    return sorted([p for p in base.glob("RUN_*") if p.is_dir()], reverse=True)


@st.cache_data
def load_risk_signals(run_dir: str) -> pd.DataFrame:
    path = Path(run_dir) / "risk_signals.jsonl"
    if not path.exists():
        return pd.DataFrame()
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["severity_order"] = df["severity"].map(SEVERITY_ORDER).fillna(99)
    return df.sort_values(["severity_order", "document_id"]).reset_index(drop=True)


@st.cache_data
def load_redlines(run_dir: str) -> pd.DataFrame:
    path = Path(run_dir) / "redlines.jsonl"
    if not path.exists():
        return pd.DataFrame()
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


@st.cache_data
def load_run_summary(run_dir: str) -> str:
    path = Path(run_dir) / "run_summary.md"
    if not path.exists():
        return "No run summary available."
    return path.read_text(encoding="utf-8")


@st.cache_data
def load_intake_manifest(run_dir: str) -> pd.DataFrame:
    path = Path(run_dir) / "intake_manifest.json"
    if not path.exists():
        return pd.DataFrame()
    data = json.loads(path.read_text(encoding="utf-8"))
    records = data if isinstance(data, list) else [data]
    return pd.DataFrame(records)


@st.cache_data
def load_extractions(run_dir: str) -> pd.DataFrame:
    path = Path(run_dir) / "extractions.jsonl"
    if not path.exists():
        return pd.DataFrame()
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def get_doc_label_map(run_dir: str) -> dict[str, str]:
    manifest = load_intake_manifest(run_dir)
    if manifest.empty or "document_id" not in manifest.columns:
        return {}
    if "source_filename" in manifest.columns:
        return dict(zip(manifest["document_id"], manifest["source_filename"]))
    return {d: d for d in manifest["document_id"]}
