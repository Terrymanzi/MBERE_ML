"""Feature selection at the engineered-feature level (computed on TRAIN only).

Scores each engineered feature against the target and keeps those scoring at or
above a config-driven ``threshold``. Working at the feature level (rather than on
expanded one-hot columns) keeps the result interpretable: a whole feature is
kept or dropped. A guard never drops every feature.
"""
from __future__ import annotations

import pandas as pd
from pandas.api.types import is_numeric_dtype
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import mutual_info_classif

from ..utils.config import DatasetConfig


def _as_numeric_codes(X: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    """Integer-encode each feature for scoring (categoricals -> factorized codes)."""
    out = {}
    for col in features:
        if is_numeric_dtype(X[col]):
            out[col] = pd.to_numeric(X[col], errors="coerce").fillna(-1).to_numpy()
        else:
            out[col] = pd.factorize(X[col].astype("string"))[0]
    return pd.DataFrame(out, index=X.index)


def compute_scores(X_train: pd.DataFrame, y_train, config: DatasetConfig) -> dict[str, float]:
    """Per-feature relevance scores on TRAIN (mutual information or RF importance).

    Zero-variance (constant) features score 0 by definition; this also avoids
    the continuous MI estimator returning spurious values on degenerate columns.
    """
    features = [c for c in config.features.all if c in X_train.columns]
    scores = {c: 0.0 for c in features}
    informative = [c for c in features if X_train[c].nunique(dropna=False) > 1]
    if not informative:
        return scores

    codes = _as_numeric_codes(X_train, informative)
    y = pd.factorize(pd.Series(y_train).astype("string"))[0]

    if config.feature_selection.method == "model_importance":
        model = RandomForestClassifier(
            n_estimators=200,
            random_state=config.random_state,
            class_weight="balanced",
            n_jobs=-1,
        )
        model.fit(codes.to_numpy(), y)
        raw = model.feature_importances_
    else:  # mutual_info
        discrete_mask = [col not in config.features.numeric for col in informative]
        raw = mutual_info_classif(
            codes.to_numpy(), y, discrete_features=discrete_mask, random_state=config.random_state
        )

    scores.update({feat: float(score) for feat, score in zip(informative, raw)})
    return scores


def select_features(X_train: pd.DataFrame, y_train, config: DatasetConfig) -> tuple[list[str], dict[str, float]]:
    """Return ``(selected_features, scores)``. Keeps features with score >= threshold."""
    features = [c for c in config.features.all if c in X_train.columns]
    if not config.feature_selection.enabled:
        return features, {}

    scores = compute_scores(X_train, y_train, config)
    threshold = config.feature_selection.threshold
    selected = [f for f in features if scores[f] >= threshold]
    if not selected:  # guard: never drop everything
        selected = features
    return selected, scores
