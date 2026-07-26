"""Deployment decision gate: candidates must beat baseline on all headline metrics."""
from __future__ import annotations

import json

from ml.evaluation.gate import evaluate_gate
from ml.utils.paths import PROJECT_ROOT

CATALOG_DIR = PROJECT_ROOT / "ml" / "artifacts"


def _metrics(name: str) -> dict:
    path = CATALOG_DIR / "reports" / name / "metrics.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_candidate_beats_baseline_on_all_metrics_passes():
    baseline = {"f1_macro": 0.30, "recall_macro": 0.30, "roc_auc_ovr_macro": 0.50}
    candidate = {"f1_macro": 0.35, "recall_macro": 0.31, "roc_auc_ovr_macro": 0.55}

    result = evaluate_gate(candidate, baseline)

    assert result.passed
    assert result.reasons == []


def test_candidate_below_baseline_on_any_metric_fails():
    baseline = {"f1_macro": 0.30, "recall_macro": 0.30, "roc_auc_ovr_macro": 0.50}
    candidate = {"f1_macro": 0.29, "recall_macro": 0.31, "roc_auc_ovr_macro": 0.55}

    result = evaluate_gate(candidate, baseline)

    assert not result.passed
    assert any("f1_macro" in r for r in result.reasons)


def test_missing_metric_fails_closed():
    baseline = {"f1_macro": 0.30, "recall_macro": 0.30, "roc_auc_ovr_macro": 0.50}
    candidate = {"f1_macro": 0.35, "recall_macro": 0.31}  # no roc_auc_ovr_macro

    result = evaluate_gate(candidate, baseline)

    assert not result.passed
    assert any("roc_auc_ovr_macro" in r for r in result.reasons)


def test_selected_model_xgboost_tuned_passes_gate_against_committed_catalog():
    """Regression guard for the canonical model documented in the README/report:
    xgboost_tuned must keep beating the baseline on held-out test metrics."""
    result = evaluate_gate(_metrics("xgboost_tuned"), _metrics("baseline"))

    assert result.passed, result.reasons


def test_untuned_random_forest_fails_gate_against_committed_catalog():
    """Regression guard for the exact issue this gate exists to catch: the plain
    random_forest catalog entry underperforms baseline and must not be servable
    as the operational default without an explicit override."""
    result = evaluate_gate(_metrics("random_forest"), _metrics("baseline"))

    assert not result.passed
    assert len(result.reasons) >= 2  # fails both f1_macro and recall_macro
