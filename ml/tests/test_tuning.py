"""Smoke tests for the RF/XGBoost hyperparameter-search modules (mirrors the
Colab notebook's Section 12.4): candidate pipelines are well-formed, the
search picks a winner via the shared CV harness, and the winner persists
under its "_tuned" artifact name without touching the ordinary model."""
from __future__ import annotations

import json

from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline as SkPipeline
from xgboost import XGBClassifier

from ml.training import tune_rf, tune_xgboost
from ml.training.common import estimator_params, train_and_save
from ml.utils.config import load_config
from ml.utils.paths import PROJECT_ROOT

ADDIS_CONFIG = PROJECT_ROOT / "ml" / "configs" / "addis.yaml"


def _prepare(tmp_path, make_addis_frame, n=450, seed=7, k_folds=2):
    """A cfg + processed train CSV + feature_contract.json large enough for
    SMOTE (and its BorderlineSMOTE/SMOTEENN variants) to find minority-class
    neighbors within every CV fold."""
    cfg = load_config(ADDIS_CONFIG)
    cfg.paths.processed_dir = tmp_path / "processed"
    cfg.paths.artifacts_dir = tmp_path / "artifacts"
    cfg.paths.processed_dir.mkdir(parents=True)
    cfg.paths.artifacts_dir.mkdir(parents=True)
    cfg.split.k_folds = k_folds

    df = make_addis_frame(n=n, seed=seed)
    df.to_csv(cfg.paths.processed_dir / f"{cfg.name}_train.csv", index=False)

    contract = {"feature_selection": {"selected": list(cfg.features.all)}}
    (cfg.paths.artifacts_dir / "feature_contract.json").write_text(
        json.dumps(contract), encoding="utf-8"
    )
    return cfg


def test_rf_candidates_are_well_formed():
    cfg = load_config(ADDIS_CONFIG)
    cands = tune_rf.candidates(cfg)
    assert len(cands) == 3
    for classifier in cands.values():
        assert isinstance(classifier, RandomForestClassifier)
        assert classifier.random_state == cfg.random_state


def test_xgb_candidates_are_well_formed():
    cfg = load_config(ADDIS_CONFIG)
    cands = tune_xgboost.candidates(cfg)
    assert len(cands) == 6
    # round-1 + resampler variants are imblearn pipelines; the control is a plain sklearn Pipeline.
    resampled = {k: v for k, v in cands.items() if "no resampling" not in k}
    control = cands["xgb_deep_lowlr + no resampling (control)"]
    assert all(isinstance(p, ImbPipeline) for p in resampled.values())
    assert isinstance(control, SkPipeline) and not isinstance(control, ImbPipeline)
    for pipe in cands.values():
        assert isinstance(pipe.named_steps["classifier"], XGBClassifier)


def test_tune_rf_smoke_and_persist(tmp_path, make_addis_frame):
    cfg = _prepare(tmp_path, make_addis_frame)

    winner = tune_rf.tune(cfg)
    assert isinstance(winner.named_steps["classifier"], RandomForestClassifier)

    params = estimator_params(winner)
    assert params  # non-empty classifier params for the meta sidecar

    model_path, meta_path, cv_metrics = train_and_save(
        cfg, tune_rf.MODEL_NAME, tune_rf.MODEL_VERSION, winner, params
    )
    assert model_path.name == "random_forest_tuned.pkl"
    assert not (cfg.paths.artifacts_dir / "random_forest.pkl").exists()  # ordinary model untouched
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta["model"] == "random_forest_tuned"
    assert meta["model_version"] == tune_rf.MODEL_VERSION
    assert "f1_macro" in cv_metrics


def test_tune_xgboost_smoke_and_persist(tmp_path, make_addis_frame):
    cfg = _prepare(tmp_path, make_addis_frame)

    winner = tune_xgboost.tune(cfg)
    assert isinstance(winner.named_steps["classifier"], XGBClassifier)

    params = estimator_params(winner)
    assert params

    model_path, meta_path, cv_metrics = train_and_save(
        cfg, tune_xgboost.MODEL_NAME, tune_xgboost.MODEL_VERSION, winner, params
    )
    assert model_path.name == "xgboost_tuned.pkl"
    assert not (cfg.paths.artifacts_dir / "xgboost.pkl").exists()  # ordinary model untouched
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta["model"] == "xgboost_tuned"
    assert meta["model_version"] == tune_xgboost.MODEL_VERSION
    assert "f1_macro" in cv_metrics
