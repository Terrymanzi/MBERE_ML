"""Transparent, rule-based risk classifier (the baseline RF/XGBoost must beat).

This is NOT a dummy/most-frequent classifier. It encodes interpretable,
literature- and EDA-informed risk rules on the engineered features and exposes
the scikit-learn fit/predict/predict_proba interface so it slots into the same
cross-validation and evaluation harness as the tree models.

Risk-elevating factors (each adds to an additive risk score):
  * young / inexperienced drivers
  * night driving on unlit/poorly-lit roads
  * adverse weather (rain, snow, fog)
  * vulnerable vehicles (motorcycle, bicycle, bajaj)
  * poor road surface (earth / gravel)

The additive score is mapped to a 3-class severity via an ordinal,
cumulative-probability formulation, so predict_proba is monotonic in risk and
predict == argmax(predict_proba). Severity codes: 0=Slight, 1=Serious, 2=Fatal.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin

N_CLASSES = 3


class RuleBasedRiskClassifier(ClassifierMixin, BaseEstimator):
    """Additive interpretable risk rules -> ordinal 3-class severity.

    Parameters
    ----------
    serious_center, fatal_center : float
        Risk-score centers (logistic midpoints) for the at-least-Serious and
        Fatal cumulative probabilities. Higher = stricter.
    scale : float
        Logistic temperature; smaller = sharper transitions.
    """

    def __init__(self, serious_center: float = 2.0, fatal_center: float = 4.0, scale: float = 1.0):
        self.serious_center = serious_center
        self.fatal_center = fatal_center
        self.scale = scale

    # --- the transparent rules ------------------------------------------- #
    def _risk_score(self, X: pd.DataFrame) -> np.ndarray:
        score = np.zeros(len(X), dtype=float)

        def isin(col: str, values: list[str]) -> np.ndarray:
            if col not in X.columns:
                return np.zeros(len(X), dtype=float)
            return X[col].astype("string").isin(values).fillna(False).to_numpy().astype(float)

        # young / inexperienced driver
        score += 2.0 * isin("driver_age_band", ["Under 18"])
        score += 1.0 * isin("driver_age_band", ["18-30"])
        score += 2.0 * isin("driver_experience", ["No Licence", "Below 1yr"])
        score += 1.0 * isin("driver_experience", ["1-2yr"])

        # night driving + poor lighting
        night = isin("time_of_day", ["Night", "Evening"])
        dark = isin("light_condition", ["Darkness - no lighting", "Darkness - lights unlit"])
        score += 2.0 * (night * dark)        # both
        score += 1.0 * (dark * (1.0 - night))  # dark but not night-bucketed

        # adverse weather
        score += 1.0 * isin("weather", ["Raining", "Raining and Windy", "Snow", "Fog or mist"])

        # vulnerable vehicle
        score += 2.0 * isin("vehicle_type", ["Motorcycle", "Bicycle", "Bajaj"])

        # poor road surface
        score += 1.0 * isin("road_surface", ["Earth roads", "Gravel roads"])

        return score

    def fit(self, X, y=None):
        # Rules are fixed (transparent); fit only records sklearn metadata.
        self.classes_ = np.arange(N_CLASSES)
        self.n_features_in_ = X.shape[1]
        if hasattr(X, "columns"):
            self.feature_names_in_ = np.asarray(X.columns)
        self.is_fitted_ = True
        return self

    def predict_proba(self, X) -> np.ndarray:
        X = X if isinstance(X, pd.DataFrame) else pd.DataFrame(X)
        score = self._risk_score(X)
        # Ordinal cumulative probabilities:
        #   P(>=Serious) = sigmoid((score - serious_center)/scale)
        #   P(=Fatal)    = sigmoid((score - fatal_center)/scale)
        p_ge_serious = _sigmoid((score - self.serious_center) / self.scale)
        p_fatal = _sigmoid((score - self.fatal_center) / self.scale)
        proba = np.column_stack([
            1.0 - p_ge_serious,          # Slight
            p_ge_serious - p_fatal,      # Serious  (>=0 since fatal_center > serious_center)
            p_fatal,                     # Fatal
        ])
        return np.clip(proba, 0.0, 1.0)

    def predict(self, X) -> np.ndarray:
        return self.predict_proba(X).argmax(axis=1).astype(int)


def _sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-z))
