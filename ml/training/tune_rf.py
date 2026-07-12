"""Hyperparameter tuning for Random Forest (notebook Section 12.4, round 1).

Random Forest has a native ``class_weight``, so tuning stacks it (``balanced``
/ ``balanced_subsample``) on top of the existing in-pipeline SMOTE, alongside
depth / ``max_features`` variants. Every candidate (plus the Section-12.2
default) is scored through the same shared-CV / OOF harness used everywhere
else in ``ml.training``, so results are directly comparable to the baseline
and ordinary ``random_forest`` CV metrics. The winner (by ``f1_macro``) is
refit on all training data and persisted as ``random_forest_tuned`` -- the
ordinary ``random_forest`` artifact is left untouched.

Usage:
    python -m ml.training.tune_rf --config ml/configs/addis.yaml
"""
from __future__ import annotations

import argparse

from sklearn.ensemble import RandomForestClassifier

from ..evaluation.metrics import compute_metrics
from ..utils.config import DatasetConfig, load_config
from ..utils.paths import PROJECT_ROOT
from .common import cross_val_oof, estimator_params, fmt4, get_cv, load_processed, make_resampling_pipeline, train_and_save
from .train_rf import build_estimator as build_rf_estimator

MODEL_NAME = "random_forest_tuned"
MODEL_VERSION = "0.2.0-tuned"


def candidates(config: DatasetConfig) -> dict[str, RandomForestClassifier]:
    """Round-1 hyperparameter variants: class_weight + depth/max_features."""
    return {
        "rf_balanced_deep (600, depth=16, balanced_subsample)": RandomForestClassifier(
            n_estimators=600, max_depth=16, min_samples_leaf=1, max_features="sqrt",
            class_weight="balanced_subsample", random_state=config.random_state, n_jobs=1,
        ),
        "rf_balanced_shallow (500, depth=8, balanced)": RandomForestClassifier(
            n_estimators=500, max_depth=8, min_samples_leaf=4, max_features="sqrt",
            class_weight="balanced", random_state=config.random_state, n_jobs=1,
        ),
        "rf_entropy_wide (800, depth=None, balanced_subsample)": RandomForestClassifier(
            n_estimators=800, max_depth=None, min_samples_leaf=1, max_features=0.5,
            criterion="entropy", class_weight="balanced_subsample",
            random_state=config.random_state, n_jobs=1,
        ),
    }


def tune(config: DatasetConfig):
    """Run the RF tuning search; return the winning (fitted-ready) estimator."""
    X, y, classes = load_processed(config, "train")
    cv = get_cv(config)

    def _score(name: str, estimator) -> dict:
        oof_pred, oof_proba = cross_val_oof(estimator, X, y, cv, config.n_classes)
        metrics = compute_metrics(y, oof_pred, oof_proba, classes)
        print(f"  {name:60s} f1_macro={metrics['f1_macro']:.4f}  recall_macro={metrics['recall_macro']:.4f}  "
              f"roc_auc_ovr_macro={fmt4(metrics['roc_auc_ovr_macro'])}  accuracy={metrics['accuracy']:.4f}")
        return metrics

    results: dict[str, dict] = {}
    default_estimator = build_rf_estimator(config)
    results["rf_default (300, leaf=2) [Section 12.2]"] = {
        "metrics": _score("rf_default (300, leaf=2) [Section 12.2]", default_estimator),
        "estimator": default_estimator,
    }
    for name, classifier in candidates(config).items():
        estimator = make_resampling_pipeline(config, classifier)
        results[name] = {"metrics": _score(name, estimator), "estimator": estimator}

    best_name = max(results, key=lambda n: results[n]["metrics"]["f1_macro"])
    print(f"\nBest Random Forest config: '{best_name}' "
          f"(f1_macro={results[best_name]['metrics']['f1_macro']:.4f})")
    return results[best_name]["estimator"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Tune Random Forest; save the winner as random_forest_tuned.")
    parser.add_argument("--config", default=str(PROJECT_ROOT / "ml" / "configs" / "addis.yaml"))
    args = parser.parse_args()

    config = load_config(args.config)
    winner = tune(config)
    train_and_save(config, MODEL_NAME, MODEL_VERSION, winner, estimator_params(winner))


if __name__ == "__main__":
    main()
