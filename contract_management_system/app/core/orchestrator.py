from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from config import load_settings
from app.core.extract import extract_fields_offline
from app.core.export import export_redlines
from app.core.intake import intake_documents
from app.core.normalize import normalize_document
from app.core.preflight import run_preflight
from app.core.redline import generate_redlines
from app.core.router import route_document
from app.core.rules import evaluate_rules
from app.core.segment import build_sections_and_clauses
from app.logging.lineage import log_lineage
from app.logging.logger import append_jsonl, build_logger, log_event
from app.logging.schemas import EventRecord, LineageRecord


def _run_id() -> str:
    return f"RUN_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"


def run_pipeline() -> Path:
    settings = load_settings()
    run_id = _run_id()
    run_dir = settings.output_root / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    logger = build_logger(run_dir / "application.log", settings.log_level)

    event_log = run_dir / "event_log.jsonl"
    lineage_log = run_dir / "lineage_log.jsonl"

    log_event(event_log, EventRecord(run_id=run_id, event_type="preflight_started", level="INFO"))
    preflight = run_preflight(settings)
    (run_dir / "preflight_report.json").write_text(json.dumps(preflight, indent=2), encoding="utf-8")
    log_event(event_log, EventRecord(run_id=run_id, event_type="preflight_passed", level="INFO"))

    intake = intake_documents(run_id, settings.input_root / "contracts", settings.input_root / "metadata")
    (run_dir / "intake_manifest.json").write_text(json.dumps(intake, indent=2), encoding="utf-8")

    artifacts = {
        "normalized_documents.jsonl": [],
        "section_hierarchy.jsonl": [],
        "clauses.jsonl": [],
        "extractions.jsonl": [],
        "risk_signals.jsonl": [],
        "redlines.jsonl": [],
    }

    summary = {"processed": 0, "failed": 0, "exports": []}
    for record in intake:
        try:
            parser_path = route_document(record["file_type"])
            if parser_path == "reject":
                log_event(event_log, EventRecord(run_id=run_id, document_id=record["document_id"], event_type="document_rejected", level="ERROR"))
                summary["failed"] += 1
                continue
            log_event(event_log, EventRecord(run_id=run_id, document_id=record["document_id"], event_type="document_ingested", level="INFO"))

            normalized = normalize_document(record, parser_path)
            artifacts["normalized_documents.jsonl"].append(normalized)
            sections, clauses = build_sections_and_clauses(normalized)
            artifacts["section_hierarchy.jsonl"].append(sections)
            artifacts["clauses.jsonl"].extend(clauses)

            extraction = extract_fields_offline(normalized, clauses)
            artifacts["extractions.jsonl"].append(extraction)

            first_clause = clauses[0]["clause_id"] if clauses else None
            first_section = clauses[0]["section_id"] if clauses else None
            risks = evaluate_rules(extraction, first_clause, first_section)
            artifacts["risk_signals.jsonl"].extend(risks)

            redlines = generate_redlines(risks, clauses)
            artifacts["redlines.jsonl"].extend(redlines)
            exports = export_redlines(record["document_id"], redlines, run_dir / "redline_exports")
            summary["exports"].append(exports)

            for risk in risks:
                log_lineage(
                    lineage_log,
                    LineageRecord(
                        run_id=run_id,
                        document_id=record["document_id"],
                        step="rule_eval",
                        input_artifact="extractions.jsonl",
                        output_artifact="risk_signals.jsonl",
                        section_id=risk.get("section_id"),
                        clause_id=risk.get("clause_id"),
                        rule_id=risk.get("rule_id"),
                        reason=risk.get("message"),
                    ),
                )
            summary["processed"] += 1
            log_event(event_log, EventRecord(run_id=run_id, document_id=record["document_id"], event_type="document_completed", level="INFO"))
        except Exception as exc:
            summary["failed"] += 1
            logger.exception("document_failed")
            failure = {
                "document id": record["document_id"],
                "source filename": record["source_filename"],
                "failed step": "pipeline",
                "exception type": type(exc).__name__,
                "exception message": str(exc),
                "retry count": 0,
                "suggested remediation": "Inspect event_log and upstream artifacts.",
            }
            append_jsonl(run_dir / "document_failure.json", failure)
            log_event(event_log, EventRecord(run_id=run_id, document_id=record["document_id"], event_type="document_failed", level="ERROR", details=failure))

    for name, rows in artifacts.items():
        p = run_dir / name
        with p.open("w", encoding="utf-8") as fh:
            for row in rows:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    run_manifest = {"run_id": run_id, "artifact_dir": str(run_dir)}
    (run_dir / "run_manifest.json").write_text(json.dumps(run_manifest, indent=2), encoding="utf-8")
    env_snapshot = {"app_env": settings.app_env, "allow_internal_model": settings.allow_internal_model, "no_public_network": settings.no_public_network}
    (run_dir / "environment_snapshot.json").write_text(json.dumps(env_snapshot, indent=2), encoding="utf-8")

    summary_md = [
        f"# Run Summary ({run_id})",
        f"- Documents processed: {summary['processed']}",
        f"- Documents failed: {summary['failed']}",
        f"- Exports created: {len(summary['exports'])}",
    ]
    (run_dir / "run_summary.md").write_text("\n".join(summary_md), encoding="utf-8")
    log_event(event_log, EventRecord(run_id=run_id, event_type="run_completed", level="INFO", details=summary))
    return run_dir
