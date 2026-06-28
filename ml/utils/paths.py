"""Project path helpers."""
from __future__ import annotations

from pathlib import Path

# ml/utils/paths.py -> parents[2] == repo root
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def resolve_path(path: str | Path) -> Path:
    """Resolve a possibly-relative path against the project root."""
    p = Path(path)
    return p if p.is_absolute() else (PROJECT_ROOT / p)
