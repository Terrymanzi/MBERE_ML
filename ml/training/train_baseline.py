"""Train the transparent rule-based baseline.

The baseline needs no encoding or resampling (it reads engineered categories
directly and its rules are fixed), but it runs through the SAME CV harness as
RF/XGBoost for a fair comparison.

Usage:
    python -m ml.training.train_baseline --config ml/configs/addis.yaml
"""
from __future__ import annotations

import argparse

from ..models import make_baseline
from ..utils.config import load_config
from ..utils.paths import PROJECT_ROOT
from .common import estimator_params, train_and_save

MODEL_NAME = "baseline"
MODEL_VERSION = "0.1.0"


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the config-selected baseline.")
    parser.add_argument("--config", default=str(PROJECT_ROOT / "ml" / "configs" / "addis.yaml"))
    args = parser.parse_args()

    config = load_config(args.config)
    estimator = make_baseline(config)
    train_and_save(config, MODEL_NAME, MODEL_VERSION, estimator, estimator_params(estimator))


if __name__ == "__main__":
    main()
