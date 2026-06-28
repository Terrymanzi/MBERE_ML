"""Tests for the transparent rule-based baseline classifier."""
from __future__ import annotations

import numpy as np
import pandas as pd

from ml.models.baseline import RuleBasedRiskClassifier

LOW_RISK = {
    "driver_age_band": "31-50", "driver_experience": "Above 10yr",
    "time_of_day": "Morning", "vehicle_type": "Automobile", "weather": "Normal",
    "road_surface": "Asphalt roads", "light_condition": "Daylight",
}
HIGH_RISK = {
    "driver_age_band": "Under 18", "driver_experience": "No Licence",
    "time_of_day": "Night", "vehicle_type": "Motorcycle", "weather": "Raining",
    "road_surface": "Earth roads", "light_condition": "Darkness - no lighting",
}


def _frame(rows):
    return pd.DataFrame(rows)


def test_interface_shapes_and_proba_simplex():
    X = _frame([LOW_RISK, HIGH_RISK])
    model = RuleBasedRiskClassifier().fit(X, np.array([0, 2]))
    proba = model.predict_proba(X)
    pred = model.predict(X)

    assert proba.shape == (2, 3)
    np.testing.assert_allclose(proba.sum(axis=1), 1.0, atol=1e-9)
    assert (proba >= 0).all()
    assert pred.shape == (2,)
    assert set(np.unique(pred)).issubset({0, 1, 2})
    assert list(model.classes_) == [0, 1, 2]


def test_predict_is_argmax_of_proba():
    X = _frame([LOW_RISK, HIGH_RISK, {**HIGH_RISK, "weather": "Normal"}])
    model = RuleBasedRiskClassifier().fit(X, np.array([0, 2, 1]))
    np.testing.assert_array_equal(model.predict(X), model.predict_proba(X).argmax(axis=1))


def test_risk_ordering_low_below_high():
    X = _frame([LOW_RISK, HIGH_RISK])
    model = RuleBasedRiskClassifier().fit(X, np.array([0, 2]))
    pred = model.predict(X)
    proba = model.predict_proba(X)
    # low-risk -> Slight (0); high-risk -> elevated severity (>0)
    assert pred[0] == 0
    assert pred[1] >= 1
    # monotonic: high-risk has greater P(Fatal) than low-risk
    assert proba[1, 2] > proba[0, 2]


def test_not_a_constant_classifier():
    rng = np.random.default_rng(0)
    options = [LOW_RISK, HIGH_RISK]
    rows = [options[i] for i in rng.integers(0, 2, size=50)]
    X = _frame(rows)
    model = RuleBasedRiskClassifier().fit(X, np.zeros(len(X), dtype=int))
    assert len(np.unique(model.predict(X))) > 1  # predicts more than one class


def test_robust_to_missing_columns():
    # Only a subset of the engineered features present -> rules that reference
    # absent columns are simply skipped (no error).
    X = pd.DataFrame({"vehicle_type": ["Motorcycle", "Automobile"]})
    model = RuleBasedRiskClassifier().fit(X, np.array([1, 0]))
    proba = model.predict_proba(X)
    assert proba.shape == (2, 3)
    assert proba[0, 2] > proba[1, 2]  # motorcycle riskier
