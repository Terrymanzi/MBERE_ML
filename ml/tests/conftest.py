"""Shared fixtures: a tiny in-memory config + raw frame mirroring RTA quirks."""
from __future__ import annotations

import textwrap

import numpy as np
import pandas as pd
import pytest

from ml.utils.config import load_config

# Canonical Addis engineered feature vocabulary (matches ml/configs/addis.yaml).
# Includes all 13 yaml-declared features (ordinal + onehot), including the two
# pruned by threshold (driver_education, driver_sex) — needed for test frames.
ADDIS_FEATURE_VALUES = {
    "driver_age_band": ["Under 18", "18-30", "31-50", "Over 51", "Unknown"],
    "driver_experience": ["No Licence", "Below 1yr", "1-2yr", "2-5yr", "5-10yr", "Above 10yr", "Unknown"],
    "time_of_day": ["Night", "Morning", "Afternoon", "Evening"],
    "driver_education": ["Unknown", "Illiterate", "Writing & reading", "Elementary school",
                         "Junior high school", "High school", "Above high school"],
    "vehicle_service_year": ["Unknown", "Below 1yr", "1-2yr", "2-5yrs", "5-10yrs", "Above 10yr"],
    "vehicle_type": ["Automobile", "Motorcycle", "Lorry", "Public_transport", "Taxi",
                     "Pickup", "Bicycle", "Bajaj", "Unknown", "Other"],
    "weather": ["Normal", "Raining", "Cloudy", "Windy", "Snow", "Fog or mist",
                "Raining and Windy", "Other", "Unknown"],
    "road_surface": ["Asphalt roads", "Earth roads", "Gravel roads",
                     "Asphalt roads with some distress", "Other", "Unknown"],
    "light_condition": ["Daylight", "Darkness - lights lit", "Darkness - no lighting", "Darkness - lights unlit"],
    "driver_sex": ["Male", "Female", "Unknown"],
    "driver_vehicle_relation": ["Employee", "Other", "Owner", "Unknown"],
    "vehicle_owner": ["Governmental", "Organization", "Other", "Owner", "Unknown"],
    "vehicle_defect": ["5", "7", "No defect", "Unknown"],
}
ADDIS_CLASSES = ["Slight Injury", "Serious Injury", "Fatal Injury"]


@pytest.fixture
def make_addis_frame():
    """Factory for a synthetic Addis-shaped frame (engineered features + target)."""

    def _make(n: int = 150, seed: int = 0) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        data = {col: rng.choice(vals, size=n) for col, vals in ADDIS_FEATURE_VALUES.items()}
        y = rng.choice(ADDIS_CLASSES, size=n, p=[0.7, 0.25, 0.05]).astype(object)
        y[:3] = ADDIS_CLASSES  # guarantee all three classes present
        data["Accident_severity"] = y
        return pd.DataFrame(data)

    return _make

TINY_CONFIG_YAML = textwrap.dedent(
    """
    name: tiny
    kind: multiclass
    paths:
      raw: data/raw/tiny.csv
      processed_dir: data/processed
      artifacts_dir: ml/artifacts
    target:
      column: Severity
      classes: ["Slight", "Serious", "Fatal"]
      label_map:
        "fatal": "Fatal"
    clean:
      leakage_columns: ["Casualty_severity"]
      time_column: "Time"
      time_derived: "hour_of_day"
      missing_tokens: ["", "na", "nan", "unknown"]
      categorical_fill_value: "Unknown"
    feature_engineering:
      renames:
        driver_age_band: Age
        weather: Weather
      time_of_day:
        source: hour_of_day
        derived: time_of_day
        buckets:
          Night: [0, 5]
          Morning: [6, 11]
          Afternoon: [12, 17]
          Evening: [18, 23]
      vehicle_type:
        source: Vehicle
        derived: vehicle_type
        default_group: Other
        rules:
          - {keyword: "Unknown", group: "Unknown"}
          - {keyword: "Motorcycle", group: "Motorcycle"}
          - {keyword: "Lorry", group: "Lorry"}
    features:
      ordinal:
        driver_age_band: ["Unknown", "Under 18", "18-30", "31-50", "Over 51"]
        time_of_day: ["Night", "Morning", "Afternoon", "Evening"]
      onehot:
        - vehicle_type
        - weather
      numeric:
        - Num_vehicles
    encoding:
      scale_numeric: false
    split:
      test_size: 0.5
      random_state: 42
      stratify: true
      k_folds: 2
    feature_selection:
      enabled: true
      method: mutual_info
      threshold: 0.0
    random_state: 42
    """
)


@pytest.fixture
def tiny_config(tmp_path):
    path = tmp_path / "tiny.yaml"
    path.write_text(TINY_CONFIG_YAML, encoding="utf-8")
    return load_config(path)


@pytest.fixture
def tiny_raw_df():
    """Mirrors real quirks: leading/trailing whitespace, missing tokens, a
    legitimate 'Other'-style fallthrough, a leakage column, mixed target casing,
    and a row with a malformed (unknown) target to be dropped."""
    return pd.DataFrame(
        {
            "Time": ["17:02:00", "1:06:00", "23:59:00", "8:00:00", "10:00:00"],
            "Age": ["18-30", " 31-50", "unknown", "Over 51", "Under 18"],
            "Vehicle": ["Motorcycle", "Lorry (11?40Q)", "na", "Automobile", "Motorcycle"],
            "Weather": ["Normal", "Raining", "Normal ", "unknown", "Cloudy"],
            "Num_vehicles": [2, 1, 3, 2, 1],
            "Casualty_severity": ["3", "2", "1", "2", "3"],  # leakage -> dropped
            "Severity": ["Slight", "fatal", "Serious", "Slight", "Bogus"],  # last -> dropped
        }
    )


@pytest.fixture
def tiny_clean_df(tiny_raw_df, tiny_config):
    """Cleaned tiny frame (drops the malformed-target row -> 4 rows)."""
    from ml.preprocessing.clean import clean

    return clean(tiny_raw_df, tiny_config)
