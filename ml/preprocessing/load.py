"""Load raw source data. Immutable raw input -> in-memory DataFrame."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..utils.config import DatasetConfig


def load_raw(source: str | Path | DatasetConfig) -> pd.DataFrame:
    """Read the raw CSV.

    Accepts a path or a :class:`DatasetConfig` (uses ``config.paths.raw``).
    Strips leading whitespace after delimiters and trims column names; further
    cell-level cleaning is handled by :func:`ml.preprocessing.clean.clean`.
    """
    path = source.paths.raw if isinstance(source, DatasetConfig) else Path(source)
    df = pd.read_csv(path, skipinitialspace=True)
    df.columns = [str(c).strip() for c in df.columns]
    return df
