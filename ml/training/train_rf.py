"""Train a Random Forest with SMOTE inside CV (encoder -> SMOTE -> RF).

Usage:
    python -m ml.training.train_rf --config ml/configs/addis.yaml
"""
from __future__ import annotations

import argparse

from sklearn.ensemble import RandomForestClassifier

from ..utils.config import load_config
from ..utils.paths import PROJECT_ROOT
from .common import make_resampling_pipeline, train_and_save

MODEL_NAME = "random_forest"
MODEL_VERSION = "0.1.0"


def build_estimator(config):
    classifier = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_leaf=2,
        random_state=config.random_state,
        # n_jobs=1 for bit-exact reproducibility: parallel trees sum probabilities
        # in a nondeterministic order, perturbing predict_proba (and thus ROC-AUC)
        # at ~1e-7. Single-threaded keeps runs identical.
        n_jobs=1,
    )
    return make_resampling_pipeline(config, classifier)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a Random Forest (SMOTE in CV).")
    parser.add_argument("--config", default=str(PROJECT_ROOT / "ml" / "configs" / "addis.yaml"))
    args = parser.parse_args()

    config = load_config(args.config)
    estimator = build_estimator(config)
    params = estimator.named_steps["classifier"].get_params()
    train_and_save(config, MODEL_NAME, MODEL_VERSION, estimator, params)


if __name__ == "__main__":
    main()
