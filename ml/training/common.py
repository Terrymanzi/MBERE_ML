"""Shared training harness so baseline / RF / XGBoost are directly comparable.

Key guarantees:
  * Identical CV splits across models: one StratifiedKFold with a shared
    random_state (from config), reused for every model.
  * Leak-free resampling: SMOTE lives INSIDE an imblearn Pipeline, so it is
    applied only to each training fold during ``fit`` and never to the
    validation fold (samplers are no-ops at predict/transform time).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.base import clone
from sklearn.model_selection import StratifiedKFold

from ..evaluation.metrics import align_proba, compute_metrics
from ..preprocessing.encode import build_encoder, encode_target
from ..utils.artifacts import build_meta, save_model, write_json
from ..utils.config import DatasetConfig
from ..utils.logging import get_logger


def estimator_params(estimator) -> dict:
    """Classifier params for the meta sidecar (handles Pipeline or bare estimator)."""
    if hasattr(estimator, "named_steps") and "classifier" in estimator.named_steps:
        return estimator.named_steps["classifier"].get_params()
    return estimator.get_params()


def processed_path(config: DatasetConfig, split: str) -> Path:
    """Path to the processed CSV for 'train' or 'test'."""
    return Path(config.paths.processed_dir) / f"{config.name}_{split}.csv"


def selected_features(config: DatasetConfig) -> list[str]:
    """Feature names kept by feature selection (persisted in feature_contract.json)."""
    contract_path = Path(config.paths.artifacts_dir) / "feature_contract.json"
    return json.loads(contract_path.read_text(encoding="utf-8"))["feature_selection"]["selected"]


def load_processed(config: DatasetConfig, split: str) -> tuple[pd.DataFrame, np.ndarray, list[str]]:
    """Load engineered features + integer-coded target for 'train' or 'test'."""
    selected = selected_features(config)
    df = pd.read_csv(processed_path(config, split))
    X = df[selected].copy()
    y, classes = encode_target(df[config.target.column], config)
    return X, y, classes


def get_cv(config: DatasetConfig) -> StratifiedKFold:
    """Shared stratified K-fold; identical splits across models (fixed seed)."""
    return StratifiedKFold(
        n_splits=config.split.k_folds, shuffle=True, random_state=config.split.random_state
    )


def make_resampling_pipeline(config: DatasetConfig, classifier) -> ImbPipeline:
    """encoder -> SMOTE -> classifier. The encoder is fit per fold; SMOTE only
    resamples the training fold."""
    selected = selected_features(config)
    return ImbPipeline([
        ("encoder", build_encoder(config, subset=selected)),
        ("smote", SMOTE(random_state=config.random_state)),
        ("classifier", classifier),
    ])


def fmt4(x: float | None) -> str:
    return f"{x:.4f}" if x is not None else "n/a"


def cross_val_oof(
    estimator, X: pd.DataFrame, y: np.ndarray, cv: StratifiedKFold, n_classes: int
) -> tuple[np.ndarray, np.ndarray]:
    """Out-of-fold predictions/probabilities using a clone per fold."""
    oof_pred = np.empty(len(y), dtype=int)
    oof_proba = np.zeros((len(y), n_classes), dtype=float)
    for train_idx, val_idx in cv.split(X, y):
        fold = clone(estimator)
        fold.fit(X.iloc[train_idx], y[train_idx])
        oof_pred[val_idx] = fold.predict(X.iloc[val_idx])
        oof_proba[val_idx] = align_proba(
            fold.predict_proba(X.iloc[val_idx]), fold.classes_, n_classes
        )
    return oof_pred, oof_proba


def train_and_save(
    config: DatasetConfig,
    model_name: str,
    model_version: str,
    estimator,
    params: dict,
):
    """CV-evaluate (OOF), fit final model on all train, save .pkl + .meta.json."""
    logger = get_logger()
    X, y, classes = load_processed(config, "train")
    logger.info("train_%s: X=%s, class counts=%s", model_name, X.shape,
                dict(zip(*np.unique(y, return_counts=True))))

    cv = get_cv(config)
    oof_pred, oof_proba = cross_val_oof(estimator, X, y, cv, config.n_classes)
    cv_metrics = compute_metrics(y, oof_pred, oof_proba, classes)
    logger.info("train_%s: CV f1_macro=%.4f recall_macro=%.4f roc_auc_ovr=%.4f",
                model_name, cv_metrics["f1_macro"], cv_metrics["recall_macro"],
                cv_metrics["roc_auc_ovr_macro"] or float("nan"))

    final = clone(estimator).fit(X, y)

    artifacts_dir = config.paths.artifacts_dir
    model_path = save_model(final, artifacts_dir / f"{model_name}.pkl")
    meta = build_meta(model_name, model_version, config, len(X), config.features.all, cv_metrics, params)
    meta_path = write_json(meta, artifacts_dir / f"{model_name}.meta.json")
    logger.info("train_%s: wrote %s + %s", model_name, model_path.name, meta_path.name)

    return model_path, meta_path, cv_metrics
