"""Reproducible, stratified train/test splitting on the severity target."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, train_test_split

from ..utils.config import DatasetConfig


def make_split(df: pd.DataFrame, config: DatasetConfig) -> tuple[np.ndarray, np.ndarray]:
    """Return reproducible ``(train_idx, test_idx)`` positional index arrays.

    Stratified on the target so class proportions (esp. the rare Fatal class)
    are preserved in both folds. Returning indices makes the split reproducible
    and auditable.
    """
    indices = np.arange(len(df))
    stratify = df[config.target.column] if config.split.stratify else None
    train_idx, test_idx = train_test_split(
        indices,
        test_size=config.split.test_size,
        random_state=config.split.random_state,
        stratify=stratify,
    )
    return np.sort(train_idx), np.sort(test_idx)


def make_kfold(config: DatasetConfig) -> StratifiedKFold:
    """Stratified K-fold splitter for later cross-validation (uses k_folds)."""
    return StratifiedKFold(
        n_splits=config.split.k_folds,
        shuffle=True,
        random_state=config.split.random_state,
    )
