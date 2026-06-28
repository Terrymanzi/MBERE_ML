"""Feature/target encoding.

The encoder is built UNFITTED and fit on the TRAIN fold only, so categories and
scaling never leak from val/test. Strategy per feature comes from config:

  * ordinal -> OrdinalEncoder with explicit category order; unseen categories at
    transform time map to -1 (handle_unknown='use_encoded_value').
  * onehot  -> OneHotEncoder(handle_unknown='ignore'); unseen categories map to
    an all-zero block.

The fitted encoder is persisted to ml/artifacts/ so inference reuses it exactly.
"""
from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

from ..utils.config import DatasetConfig


def _partition(config: DatasetConfig, subset: list[str]) -> tuple[list[str], list[str], list[str]]:
    """Split a feature subset into (ordinal, onehot, numeric), preserving config order."""
    ordinal = [c for c in config.features.ordinal if c in subset]
    onehot = [c for c in config.features.onehot if c in subset]
    numeric = [c for c in config.features.numeric if c in subset]
    return ordinal, onehot, numeric


def build_encoder(config: DatasetConfig, subset: list[str] | None = None) -> ColumnTransformer:
    """Build an UNFITTED ColumnTransformer for the configured (or subset of) features."""
    subset = list(subset) if subset is not None else config.features.all
    ordinal, onehot, numeric = _partition(config, subset)

    transformers: list[tuple] = []
    if ordinal:
        categories = [config.features.ordinal[c] for c in ordinal]
        transformers.append((
            "ordinal",
            OrdinalEncoder(
                categories=categories,
                handle_unknown="use_encoded_value",
                unknown_value=-1,
            ),
            ordinal,
        ))
    if onehot:
        transformers.append((
            "onehot",
            OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            onehot,
        ))
    if numeric:
        num = StandardScaler() if config.encoding.scale_numeric else "passthrough"
        transformers.append(("numeric", num, numeric))

    return ColumnTransformer(transformers, remainder="drop")


def fit_encoder(encoder: ColumnTransformer, X_train: pd.DataFrame) -> ColumnTransformer:
    """Fit the encoder on TRAIN features only."""
    encoder.fit(X_train)
    return encoder


def transform(encoder: ColumnTransformer, X: pd.DataFrame) -> np.ndarray:
    return np.asarray(encoder.transform(X))


def encoded_feature_names(encoder: ColumnTransformer) -> list[str]:
    return list(encoder.get_feature_names_out())


def save_encoder(encoder: ColumnTransformer, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(encoder, path)
    return path


def load_encoder(path: str | Path) -> ColumnTransformer:
    return joblib.load(Path(path))


def encode_target(y, config: DatasetConfig) -> tuple[np.ndarray, list[str]]:
    """Map target labels to stable integer codes using the config class order.

    Returns ``(codes, classes)`` where ``classes[i]`` is the label for code ``i``.
    """
    classes = list(config.target.classes)
    mapping = {label: idx for idx, label in enumerate(classes)}

    series = pd.Series(y).astype("string").str.strip().replace(config.target.label_map)
    codes = series.map(mapping)
    if codes.isna().any():
        bad = sorted(set(series[codes.isna()].dropna().unique()))
        raise ValueError(f"Target labels not in configured classes {classes}: {bad}")
    return codes.to_numpy(dtype=int), classes
