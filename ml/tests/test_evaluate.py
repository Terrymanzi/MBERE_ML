"""REQUIRED: evaluation handles a 3-class target (metrics + end-to-end reports)."""
from __future__ import annotations

import numpy as np

from ml.evaluation.evaluate import evaluate_model
from ml.evaluation.metrics import compute_metrics
from ml.models.baseline import RuleBasedRiskClassifier
from ml.preprocessing.encode import encode_target
from ml.utils.artifacts import save_model
from ml.utils.config import load_config
from ml.utils.paths import PROJECT_ROOT

ADDIS_CONFIG = PROJECT_ROOT / "ml" / "configs" / "addis.yaml"


def test_compute_metrics_three_class():
    y_true = np.array([0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2])
    y_pred = np.array([0, 1, 2, 0, 2, 1, 0, 1, 2, 1, 1, 2])
    base = np.eye(3)[y_true] * 0.6 + 0.2          # higher mass on the true class
    proba = base / base.sum(axis=1, keepdims=True)  # valid simplex
    names = ["Slight", "Serious", "Fatal"]

    m = compute_metrics(y_true, y_pred, proba, names)

    assert m["labels"] == names
    assert set(m["per_class"]) == set(names)
    assert np.array(m["confusion_matrix"]).shape == (3, 3)
    for name in names:
        assert "roc_auc_ovr" in m["per_class"][name]
        assert {"precision", "recall", "f1", "support"} <= set(m["per_class"][name])
    assert 0.0 <= m["f1_macro"] <= 1.0
    assert m["roc_auc_ovr_macro"] is not None
    assert "accuracy" in m  # reported but not headline


def test_evaluate_model_end_to_end_3class(tmp_path, make_addis_frame):
    cfg = load_config(ADDIS_CONFIG)
    cfg.paths.processed_dir = tmp_path / "processed"
    cfg.paths.artifacts_dir = tmp_path / "artifacts"
    cfg.paths.processed_dir.mkdir(parents=True)

    df = make_addis_frame(n=180, seed=1)
    df.to_csv(cfg.paths.processed_dir / f"{cfg.name}_test.csv", index=False)

    X = df[cfg.features.all]
    y, _ = encode_target(df[cfg.target.column], cfg)
    model = RuleBasedRiskClassifier().fit(X, y)
    save_model(model, cfg.paths.artifacts_dir / "baseline.pkl")

    metrics = evaluate_model(cfg, "baseline")

    assert set(metrics["per_class"]) == set(cfg.target.classes)
    assert metrics["roc_auc_ovr_macro"] is not None
    out = cfg.paths.artifacts_dir / "reports" / "baseline"
    assert (out / "metrics.json").exists()
    assert (out / "confusion_matrix.png").exists()
    assert (out / "roc_curves.png").exists()
