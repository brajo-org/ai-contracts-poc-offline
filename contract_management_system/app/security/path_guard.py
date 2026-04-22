from __future__ import annotations

from pathlib import Path


class PathGuardError(RuntimeError):
    pass


def ensure_within_root(root: Path, target: Path) -> Path:
    root_r = root.resolve()
    target_r = target.resolve()
    try:
        target_r.relative_to(root_r)
    except ValueError as exc:
        raise PathGuardError(f"Path traversal blocked for {target}") from exc
    return target_r
