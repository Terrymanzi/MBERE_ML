"""Tests for ml.features (feature engineering + selection)."""
from __future__ import annotations

import pandas as pd

from ml.features.feature_engineering import engineer_features
from ml.features.feature_selection import compute_scores, select_features


# --------------------------------------------------------------------------- #
# feature engineering
# --------------------------------------------------------------------------- #
def test_engineer_features_schema(tiny_clean_df, tiny_config):
    eng = engineer_features(tiny_clean_df, tiny_config)
    assert list(eng.columns) == tiny_config.features.all + [tiny_config.target.column]


def test_vehicle_grouping_motorcycle_first_class(tiny_clean_df, tiny_config):
    eng = engineer_features(tiny_clean_df, tiny_config)
    # Motorcycle kept distinct; 'Lorry (11?40Q)' -> Lorry by keyword; 'Unknown'
    # preserved; 'Automobile' (no rule) -> default Other.
    assert eng["vehicle_type"].tolist() == ["Motorcycle", "Lorry", "Unknown", "Other"]


def test_time_of_day_buckets(tiny_clean_df, tiny_config):
    eng = engineer_features(tiny_clean_df, tiny_config)
    assert eng["time_of_day"].tolist() == ["Afternoon", "Night", "Evening", "Morning"]


def test_renames_applied(tiny_clean_df, tiny_config):
    eng = engineer_features(tiny_clean_df, tiny_config)
    assert eng["driver_age_band"].tolist() == ["18-30", "31-50", "Unknown", "Over 51"]
    assert eng["weather"].tolist() == ["Normal", "Raining", "Normal", "Unknown"]


# --------------------------------------------------------------------------- #
# feature selection
# --------------------------------------------------------------------------- #
def test_selection_disabled_returns_all(tiny_clean_df, tiny_config):
    tiny_config.feature_selection.enabled = False
    eng = engineer_features(tiny_clean_df, tiny_config)
    selected, scores = select_features(eng[tiny_config.features.all], eng["Severity"], tiny_config)
    assert selected == tiny_config.features.all
    assert scores == {}


def test_selection_scores_cover_all_features(tiny_clean_df, tiny_config):
    eng = engineer_features(tiny_clean_df, tiny_config)
    selected, scores = select_features(eng[tiny_config.features.all], eng["Severity"], tiny_config)
    assert set(scores) == set(tiny_config.features.all)
    assert selected == tiny_config.features.all  # threshold 0.0 keeps all


def test_selection_threshold_prunes_uninformative(tiny_config):
    # weather perfectly determines y; everything else constant (zero MI).
    y = ["Slight", "Serious", "Fatal"] * 4
    weather_map = {"Slight": "Normal", "Serious": "Raining", "Fatal": "Cloudy"}
    df = pd.DataFrame({
        "driver_age_band": ["18-30"] * 12,
        "time_of_day": ["Morning"] * 12,
        "vehicle_type": ["Motorcycle"] * 12,
        "weather": [weather_map[v] for v in y],
        "Num_vehicles": [2] * 12,
    })
    scores = compute_scores(df, y, tiny_config)
    assert scores["weather"] > 0
    assert scores["Num_vehicles"] == 0

    tiny_config.feature_selection.threshold = scores["weather"] / 2
    selected, _ = select_features(df, y, tiny_config)
    assert "weather" in selected
    assert "Num_vehicles" not in selected
