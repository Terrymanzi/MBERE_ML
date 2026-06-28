"""Smoke test: the shared training harness produces a versioned artifact + meta."""
from __future__ import annotations

import json

from ml.models.baseline import RuleBasedRiskClassifier
from ml.training.common import get_cv, train_and_save
from ml.utils.config import load_config
from ml.utils.paths import PROJECT_ROOT

ADDIS_CONFIG = PROJECT_ROOT / "ml" / "configs" / "addis.yaml"


def test_shared_cv_is_identical_across_calls():
    cfg = load_config(ADDIS_CONFIG)
    cfg.split.k_folds = 3
    # Same seed + n_splits -> identical splitter config -> identical splits across models.
    a, b = get_cv(cfg), get_cv(cfg)
    assert a.n_splits == b.n_splits == 3
    assert a.random_state == b.random_state == cfg.split.random_state


def test_train_and_save_baseline_smoke(tmp_path, make_addis_frame):
    cfg = load_config(ADDIS_CONFIG)
    cfg.paths.processed_dir = tmp_path / "processed"
    cfg.paths.artifacts_dir = tmp_path / "artifacts"
    cfg.paths.processed_dir.mkdir(parents=True)
    cfg.split.k_folds = 3

    df = make_addis_frame(n=210, seed=2)
    df.to_csv(cfg.paths.processed_dir / f"{cfg.name}_train.csv", index=False)

    estimator = RuleBasedRiskClassifier()
    model_path, meta_path, cv_metrics = train_and_save(
        cfg, "baseline", "0.1.0", estimator, estimator.get_params()
    )

    assert model_path.exists() and meta_path.exists()
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta["model"] == "baseline"
    assert meta["model_version"] == "0.1.0"
    assert meta["dataset"]["name"] == cfg.name
    assert meta["features"] == cfg.features.all
    assert meta["random_state"] == cfg.random_state
    assert "git_commit" in meta
    # CV metrics are multiclass-aware and recorded in the sidecar.
    assert "f1_macro" in cv_metrics and "roc_auc_ovr_macro" in cv_metrics
    assert set(meta["metrics_cv"]["per_class"]) == set(cfg.target.classes)
