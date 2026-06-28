"""Train an XGBoost classifier with SMOTE inside CV (encoder -> SMOTE -> XGB).

Usage:
    python -m ml.training.train_xgboost --config ml/configs/addis.yaml
"""
from __future__ import annotations

import argparse

from xgboost import XGBClassifier

from ..utils.config import load_config
from ..utils.paths import PROJECT_ROOT
from .common import make_resampling_pipeline, train_and_save

MODEL_NAME = "xgboost"
MODEL_VERSION = "0.1.0"


def build_estimator(config):
    # kind-aware objective so binary configs work with no code changes.
    if config.kind == "binary":
        objective = {"objective": "binary:logistic", "eval_metric": "logloss"}
    else:
        objective = {"objective": "multi:softprob", "num_class": config.n_classes,
                     "eval_metric": "mlogloss"}
    classifier = XGBClassifier(
        n_estimators=400,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.9,
        colsample_bytree=0.9,
        tree_method="hist",
        random_state=config.random_state,
        n_jobs=-1,
        **objective,
    )
    return make_resampling_pipeline(config, classifier)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train XGBoost (SMOTE in CV).")
    parser.add_argument("--config", default=str(PROJECT_ROOT / "ml" / "configs" / "addis.yaml"))
    args = parser.parse_args()

    config = load_config(args.config)
    estimator = build_estimator(config)
    params = estimator.named_steps["classifier"].get_params()
    train_and_save(config, MODEL_NAME, MODEL_VERSION, estimator, params)


if __name__ == "__main__":
    main()
