"""Artifact deserialization helpers.

The backend only ever READS model artifacts produced by the `ml/` package. This
module deliberately exposes a load-only surface (no dump/fit) to keep that
boundary obvious.
"""
from __future__ import annotations

from pathlib import Path

import joblib


def load_pickle(path: str | Path):
    return joblib.load(Path(path))
