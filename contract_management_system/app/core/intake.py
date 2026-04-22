from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def intake_documents(run_id: str, contracts_dir: Path, metadata_dir: Path) -> list[dict]:
    records: list[dict] = []
    all_files = []
    if contracts_dir.exists():
        all_files.extend(sorted([p for p in contracts_dir.iterdir() if p.is_file()]))
    if metadata_dir.exists():
        all_files.extend(sorted([p for p in metadata_dir.iterdir() if p.is_file()]))

    for idx, file in enumerate(all_files, start=1):
        records.append(
            {
                "run_id": run_id,
                "document_id": f"DOC-{idx:04d}",
                "source_filename": file.name,
                "source_path": str(file),
                "source_sha256": _sha256(file),
                "file_type": file.suffix.lower().lstrip("."),
                "file_size_bytes": file.stat().st_size,
                "ingest_timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
    return records
