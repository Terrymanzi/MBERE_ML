"""Binary-target (Porto) generalization: metrics, baseline factory, XGB objective, config."""
from __future__ import annotations

import numpy as np
from sklearn.linear_model import LogisticRegression

from ml.evaluation.metrics import compute_metrics
from ml.models import RuleBasedRiskClassifier, make_baseline
from ml.training.train_xgboost import build_estimator as build_xgb
from ml.utils.config import load_config
from ml.utils.paths import PROJECT_ROOT

PORTO_CONFIG = PROJECT_ROOT / "ml" / "configs" / "porto_seguro.yaml"
ADDIS_CONFIG = PROJECT_ROOT / "ml" / "configs" / "addis.yaml"


def test_compute_metrics_binary():
    y_true = np.array([0, 1, 0, 1, 0, 1, 0, 0, 1, 0])
    y_pred = np.array([0, 1, 0, 0, 0, 1, 0, 1, 1, 0])
    pos = np.array([0.2, 0.8, 0.3, 0.45, 0.1, 0.9, 0.25, 0.6, 0.7, 0.2])
    proba = np.column_stack([1 - pos, pos])
    names = ["No claim", "Claim"]

    m = compute_metrics(y_true, y_pred, proba, names)
    assert set(m["per_class"]) == set(names)
    assert np.array(m["confusion_matrix"]).shape == (2, 2)
    assert m["roc_auc_ovr_macro"] is not None  # binary AUC computed
    assert 0.0 <= m["f1_macro"] <= 1.0


def test_porto_config_is_binary():
    cfg = load_config(PORTO_CONFIG)
    assert cfg.kind == "binary"
    assert cfg.n_classes == 2
    assert cfg.target.column == "target"
    assert cfg.baseline.kind == "logistic"
    assert cfg.feature_engineering.time_of_day is None  # no domain FE for anonymized features


def test_make_baseline_is_config_selected():
    addis = load_config(ADDIS_CONFIG)
    porto = load_config(PORTO_CONFIG)

    assert isinstance(make_baseline(addis), RuleBasedRiskClassifier)

    porto_baseline = make_baseline(porto)  # encoder -> LogisticRegression pipeline
    assert hasattr(porto_baseline, "named_steps")
    assert isinstance(porto_baseline.named_steps["classifier"], LogisticRegression)


def test_xgboost_objective_is_kind_aware():
    porto = load_config(PORTO_CONFIG)
    addis = load_config(ADDIS_CONFIG)
    porto_clf = build_xgb(porto).named_steps["classifier"]
    addis_clf = build_xgb(addis).named_steps["classifier"]
    assert porto_clf.get_params()["objective"] == "binary:logistic"
    assert addis_clf.get_params()["objective"] == "multi:softprob"
