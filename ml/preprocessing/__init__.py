"""Preprocessing: load, clean (deterministic/leakage-safe), split, encode, orchestrate."""
from __future__ import annotations

from .clean import clean, load_and_clean, parse_time
from .encode import (
    build_encoder,
    encode_target,
    encoded_feature_names,
    fit_encoder,
    load_encoder,
    save_encoder,
    transform,
)
from .load import load_raw
from .split import make_kfold, make_split

# NOTE: the orchestrator (preprocess.run) is intentionally NOT imported here.
# Importing it eagerly makes `python -m ml.preprocessing.preprocess` emit a
# double-import RuntimeWarning. Import it directly:
#     from ml.preprocessing.preprocess import run

__all__ = [
    "load_raw",
    "clean",
    "load_and_clean",
    "parse_time",
    "make_split",
    "make_kfold",
    "build_encoder",
    "fit_encoder",
    "transform",
    "encoded_feature_names",
    "save_encoder",
    "load_encoder",
    "encode_target",
]
