"""Binary-target generalization: metrics and XGBoost objective awareness.

Porto Seguro has been removed from scope. Tests that required porto_seguro.yaml
have been removed. Generic binary-metric and XGBoost objective tests are kept.
"""
from __future__ import annotations

import numpy as np

from ml.evaluation.metrics import compute_metrics
from ml.models import RuleBasedRiskClassifier, make_baseline
from ml.training.train_xgboost import build_estimator as build_xgb
from ml.utils.config import load_config
from ml.utils.paths import PROJECT_ROOT

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


def test_make_baseline_addis_is_rule_based():
    addis = load_config(ADDIS_CONFIG)
    assert isinstance(make_baseline(addis), RuleBasedRiskClassifier)


def test_xgboost_objective_multiclass_for_addis():
    addis = load_config(ADDIS_CONFIG)
    addis_clf = build_xgb(addis).named_steps["classifier"]
    assert addis_clf.get_params()["objective"] == "multi:softprob"
