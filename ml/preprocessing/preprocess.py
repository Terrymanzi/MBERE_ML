"""Orchestrate clean -> feature engineering -> split -> select -> encode -> save.

Runtime order is clean -> SPLIT -> encode (fit on TRAIN only): encoders/scalers
must never see test data, so the split happens before any fitting. Feature
selection scores are also computed on TRAIN only.

Outputs (per config paths):
  data/processed/<name>_train.csv, <name>_test.csv   engineered selected features + target
  data/processed/<name>_train_encoded.npz, ..._test_encoded.npz   model-ready X, y
  <artifacts_dir>/encoders.joblib       fitted ColumnTransformer (TRAIN-fit)
  <artifacts_dir>/split_indices.json    reproducible train/test indices
  <artifacts_dir>/feature_contract.json ordered feature names + dtypes (backend validates this)

Usage:
    python -m ml.preprocessing.preprocess --config ml/configs/addis.yaml
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from ..features.feature_engineering import engineer_features
from ..features.feature_selection import select_features
from ..utils.config import DatasetConfig, load_config
from ..utils.logging import get_logger
from ..utils.paths import PROJECT_ROOT
from .clean import load_and_clean
from .encode import (
    build_encoder,
    encode_target,
    encoded_feature_names,
    fit_encoder,
    save_encoder,
    transform,
)
from .split import make_split

logger = get_logger()


@dataclass
class PreprocessResult:
    train_path: Path
    test_path: Path
    encoder_path: Path
    contract_path: Path
    split_path: Path
    n_train: int
    n_test: int
    selected_features: list[str]


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def build_feature_contract(
    config: DatasetConfig,
    encoder,
    selected: list[str],
    classes: list[str],
    scores: dict[str, float],
    n_train: int,
    n_test: int,
) -> dict:
    """Describe the model input contract: ordered features, dtypes, categories."""
    onehot_cols = [c for c in config.features.onehot if c in selected]
    onehot_categories = {}
    if onehot_cols:
        fitted = encoder.named_transformers_["onehot"]
        # .tolist() -> native Python (numeric categorical features yield numpy ints,
        # which are not JSON-serializable otherwise).
        onehot_categories = {col: np.asarray(cats).tolist()
                             for col, cats in zip(onehot_cols, fitted.categories_)}

    input_features = []
    for name in selected:
        if name in config.features.ordinal:
            input_features.append({
                "name": name, "kind": "categorical", "encoding": "ordinal",
                "dtype": "string", "categories": list(config.features.ordinal[name]),
            })
        elif name in config.features.onehot:
            input_features.append({
                "name": name, "kind": "categorical", "encoding": "onehot",
                "dtype": "string", "categories": onehot_categories.get(name, []),
            })
        else:
            input_features.append({
                "name": name, "kind": "numeric", "encoding": "numeric", "dtype": "float64",
            })

    return {
        "dataset": config.name,
        "kind": config.kind,
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "random_state": config.random_state,
        "target": {"column": config.target.column, "classes": list(classes)},
        "rows": {"train": n_train, "test": n_test, "total": n_train + n_test},
        "input_features": input_features,
        "encoded_feature_names": encoded_feature_names(encoder),
        "n_encoded_features": len(encoded_feature_names(encoder)),
        "feature_selection": {
            "method": config.feature_selection.method,
            "threshold": config.feature_selection.threshold,
            "scores": scores,
            "selected": list(selected),
        },
        "artifacts": {"encoder": "encoders.joblib"},
    }


def run(config: DatasetConfig) -> PreprocessResult:
    target = config.target.column
    processed_dir = Path(config.paths.processed_dir)
    artifacts_dir = Path(config.paths.artifacts_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # clean -> feature engineering (deterministic, full data)
    cleaned = load_and_clean(config, logger=logger)
    engineered = engineer_features(cleaned, config)

    # split BEFORE any fitting
    train_idx, test_idx = make_split(engineered, config)
    train_df = engineered.iloc[train_idx].reset_index(drop=True)
    test_df = engineered.iloc[test_idx].reset_index(drop=True)
    logger.info("split: train=%d test=%d (test_size=%.2f, stratified=%s)",
                len(train_df), len(test_df), config.split.test_size, config.split.stratify)

    # feature selection on TRAIN only
    selected, scores = select_features(train_df[config.features.all], train_df[target], config)
    logger.info("feature_selection (%s): scores=%s", config.feature_selection.method,
                {k: round(v, 4) for k, v in scores.items()})
    logger.info("selected %d/%d features: %s", len(selected), len(config.features.all), selected)

    # encode: FIT ON TRAIN ONLY, then apply to test
    encoder = fit_encoder(build_encoder(config, subset=selected), train_df[selected])
    X_train = transform(encoder, train_df[selected])
    X_test = transform(encoder, test_df[selected])
    y_train, classes = encode_target(train_df[target], config)
    y_test, _ = encode_target(test_df[target], config)

    # persist processed sets (readable engineered features + target)
    train_path = processed_dir / f"{config.name}_train.csv"
    test_path = processed_dir / f"{config.name}_test.csv"
    train_df[selected + [target]].to_csv(train_path, index=False)
    test_df[selected + [target]].to_csv(test_path, index=False)

    # persist model-ready encoded matrices
    np.savez(processed_dir / f"{config.name}_train_encoded.npz", X=X_train, y=y_train)
    np.savez(processed_dir / f"{config.name}_test_encoded.npz", X=X_test, y=y_test)

    # persist fitted encoder
    encoder_path = save_encoder(encoder, artifacts_dir / "encoders.joblib")

    # persist split indices (reproducibility)
    split_path = artifacts_dir / "split_indices.json"
    split_path.write_text(
        json.dumps({"train": train_idx.tolist(), "test": test_idx.tolist()}), encoding="utf-8"
    )

    # persist feature contract
    contract = build_feature_contract(
        config, encoder, selected, classes, scores, len(train_df), len(test_df)
    )
    contract_path = artifacts_dir / "feature_contract.json"
    contract_path.write_text(json.dumps(contract, indent=2), encoding="utf-8")

    logger.info("wrote: %s, %s, %s, %s, %s",
                train_path.name, test_path.name, encoder_path.name,
                split_path.name, contract_path.name)
    logger.info("encoded feature dim: %d", X_train.shape[1])

    return PreprocessResult(
        train_path=train_path, test_path=test_path, encoder_path=encoder_path,
        contract_path=contract_path, split_path=split_path,
        n_train=len(train_df), n_test=len(test_df), selected_features=selected,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Preprocess a dataset from a config.")
    parser.add_argument(
        "--config",
        default=str(PROJECT_ROOT / "ml" / "configs" / "addis.yaml"),
        help="Path to the dataset YAML config.",
    )
    args = parser.parse_args()
    run(load_config(args.config))


if __name__ == "__main__":
    main()
