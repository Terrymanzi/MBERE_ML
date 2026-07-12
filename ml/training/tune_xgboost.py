"""Hyperparameter tuning for XGBoost (notebook Section 12.4, rounds 1 & 2).

XGBoost has no native multiclass ``class_weight``, so round 1 only tunes
regularization (``min_child_weight``, ``gamma``, ``reg_alpha``/``reg_lambda``),
learning-rate/depth trade-offs, and SMOTE's ``k_neighbors``. Round 2 holds the
best round-1 classifier hyperparameters fixed and instead swaps the resampler
feeding it (plain SMOTE -> BorderlineSMOTE / SMOTEENN / no resampling), since
XGBoost depends entirely on the resampler -- not ``class_weight`` -- to see
the minority classes. Every candidate (plus the Section-12.3 default) is
scored through the same shared-CV / OOF harness used everywhere else in
``ml.training``. The winner (by ``f1_macro``) is refit on all training data
and persisted as ``xgboost_tuned`` -- the ordinary ``xgboost`` artifact is
left untouched.

Usage:
    python -m ml.training.tune_xgboost --config ml/configs/addis.yaml
"""
from __future__ import annotations

import argparse

from imblearn.combine import SMOTEENN
from imblearn.over_sampling import SMOTE, BorderlineSMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.pipeline import Pipeline as SkPipeline
from xgboost import XGBClassifier

from ..evaluation.metrics import compute_metrics
from ..preprocessing.encode import build_encoder
from ..utils.config import DatasetConfig, load_config
from ..utils.paths import PROJECT_ROOT
from .common import cross_val_oof, estimator_params, fmt4, get_cv, load_processed, selected_features, train_and_save
from .train_xgboost import build_estimator as build_xgb_estimator

MODEL_NAME = "xgboost_tuned"
MODEL_VERSION = "0.2.0-tuned"


def _make_pipeline(config: DatasetConfig, classifier, sampler=None, smote_kwargs: dict | None = None) -> ImbPipeline:
    """encoder -> sampler -> classifier. Defaults to vanilla SMOTE (matching
    ml.training.common.make_resampling_pipeline) unless a sampler instance is
    passed explicitly, or smote_kwargs overrides SMOTE's own hyperparameters."""
    if sampler is None:
        sampler = SMOTE(random_state=config.random_state, **(smote_kwargs or {}))
    return ImbPipeline([
        ("encoder", build_encoder(config, subset=selected_features(config))),
        ("sampler", sampler),
        ("classifier", classifier),
    ])


def _make_pipeline_no_resample(config: DatasetConfig, classifier) -> SkPipeline:
    """encoder -> classifier, no resampling at all (control)."""
    return SkPipeline([
        ("encoder", build_encoder(config, subset=selected_features(config))),
        ("classifier", classifier),
    ])


def candidates(config: DatasetConfig) -> dict:
    objective = (
        {"objective": "binary:logistic", "eval_metric": "logloss"}
        if config.kind == "binary"
        else {"objective": "multi:softprob", "num_class": config.n_classes, "eval_metric": "mlogloss"}
    )
    # Round 1's winner; round 2 holds these fixed and only swaps the resampler.
    deep_lowlr_params = dict(
        n_estimators=800, max_depth=8, learning_rate=0.03, subsample=0.85, colsample_bytree=0.85,
        min_child_weight=1, gamma=0.1,
        tree_method="hist", random_state=config.random_state, n_jobs=-1, **objective,
    )

    return {
        # --- round 1: hyperparameter-only variants ---
        "xgb_shallow_reg (300, depth=4, lr=0.05, reg)": _make_pipeline(config, XGBClassifier(
            n_estimators=300, max_depth=4, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8,
            min_child_weight=3, reg_alpha=0.1, reg_lambda=1.5,
            tree_method="hist", random_state=config.random_state, n_jobs=-1, **objective,
        )),
        "xgb_deep_lowlr (800, depth=8, lr=0.03, min_child_weight=1)": _make_pipeline(
            config, XGBClassifier(**deep_lowlr_params)
        ),
        "xgb_smote_k3 (500, depth=6, lr=0.07, k_neighbors=3)": _make_pipeline(config, XGBClassifier(
            n_estimators=500, max_depth=6, learning_rate=0.07, subsample=0.9, colsample_bytree=0.7,
            min_child_weight=1, gamma=0.05,
            tree_method="hist", random_state=config.random_state, n_jobs=-1, **objective,
        ), smote_kwargs={"k_neighbors": 3}),
        # --- round 2: same deep_lowlr classifier hyperparameters, different resampling ---
        "xgb_deep_lowlr + BorderlineSMOTE": _make_pipeline(
            config, XGBClassifier(**deep_lowlr_params), sampler=BorderlineSMOTE(random_state=config.random_state)
        ),
        "xgb_deep_lowlr + SMOTEENN": _make_pipeline(
            config, XGBClassifier(**deep_lowlr_params), sampler=SMOTEENN(random_state=config.random_state)
        ),
        "xgb_deep_lowlr + no resampling (control)": _make_pipeline_no_resample(
            config, XGBClassifier(**deep_lowlr_params)
        ),
    }


def tune(config: DatasetConfig):
    """Run the XGBoost tuning search; return the winning (fitted-ready) estimator."""
    X, y, classes = load_processed(config, "train")
    cv = get_cv(config)

    def _score(name: str, estimator) -> dict:
        oof_pred, oof_proba = cross_val_oof(estimator, X, y, cv, config.n_classes)
        metrics = compute_metrics(y, oof_pred, oof_proba, classes)
        print(f"  {name:60s} f1_macro={metrics['f1_macro']:.4f}  recall_macro={metrics['recall_macro']:.4f}  "
              f"roc_auc_ovr_macro={fmt4(metrics['roc_auc_ovr_macro'])}  accuracy={metrics['accuracy']:.4f}")
        return metrics

    results: dict[str, dict] = {}
    default_estimator = build_xgb_estimator(config)
    results["xgb_default (400, depth=6, lr=0.1) [Section 12.3]"] = {
        "metrics": _score("xgb_default (400, depth=6, lr=0.1) [Section 12.3]", default_estimator),
        "estimator": default_estimator,
    }
    for name, estimator in candidates(config).items():
        results[name] = {"metrics": _score(name, estimator), "estimator": estimator}

    best_name = max(results, key=lambda n: results[n]["metrics"]["f1_macro"])
    print(f"\nBest XGBoost config: '{best_name}' "
          f"(f1_macro={results[best_name]['metrics']['f1_macro']:.4f})")
    return results[best_name]["estimator"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Tune XGBoost; save the winner as xgboost_tuned.")
    parser.add_argument("--config", default=str(PROJECT_ROOT / "ml" / "configs" / "addis.yaml"))
    args = parser.parse_args()

    config = load_config(args.config)
    winner = tune(config)
    train_and_save(config, MODEL_NAME, MODEL_VERSION, winner, estimator_params(winner))


if __name__ == "__main__":
    main()
