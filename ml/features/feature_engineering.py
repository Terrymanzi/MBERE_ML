"""Derive the proposal's interpretable features from cleaned columns.

All transforms are deterministic and row-wise (no fitting), so this runs on the
full dataset before the train/test split without leaking anything.

Engineered features: driver age band, driver experience, vehicle type
(motorcycle is a first-class category), weather, road surface, time-of-day
bucket, and light condition.
"""
from __future__ import annotations

import pandas as pd

from ..utils.config import DatasetConfig, TimeOfDayConfig, VehicleGroupConfig


def bucket_time_of_day(hours: pd.Series, cfg: TimeOfDayConfig, fill: str = "Unknown") -> pd.Series:
    """Map an integer hour-of-day to a named bucket (inclusive ranges)."""
    result = pd.Series([fill] * len(hours), index=hours.index, dtype="object")
    numeric = pd.to_numeric(hours, errors="coerce")
    for name, (start, end) in cfg.buckets.items():
        mask = numeric.between(start, end, inclusive="both")
        result[mask.fillna(False)] = name
    return result.astype("string")


def group_vehicle_type(values: pd.Series, cfg: VehicleGroupConfig) -> pd.Series:
    """Group raw vehicle labels via ordered case-insensitive keyword rules."""
    lowered = values.astype("string").str.lower()

    def assign(val: str | None) -> str:
        if val is None or pd.isna(val):
            return cfg.default_group
        for rule in cfg.rules:
            if rule.keyword.lower() in val:
                return rule.group
        return cfg.default_group

    return lowered.map(assign).astype("string")


def engineer_features(df: pd.DataFrame, config: DatasetConfig) -> pd.DataFrame:
    """Return a frame of the configured modeling features + target."""
    fe = config.feature_engineering
    out = df.copy()

    # 1:1 renames (engineered_name <- source_column).
    for new_name, source in fe.renames.items():
        if source in out.columns:
            out[new_name] = out[source]

    # Time-of-day bucket.
    if fe.time_of_day and fe.time_of_day.source in out.columns:
        out[fe.time_of_day.derived] = bucket_time_of_day(
            out[fe.time_of_day.source], fe.time_of_day, config.clean.categorical_fill_value
        )

    # Vehicle-type grouping (motorcycle first-class).
    if fe.vehicle_type and fe.vehicle_type.source in out.columns:
        out[fe.vehicle_type.derived] = group_vehicle_type(
            out[fe.vehicle_type.source], fe.vehicle_type
        )

    keep = [c for c in config.features.all if c in out.columns] + [config.target.column]
    missing = [c for c in config.features.all if c not in out.columns]
    if missing:
        raise KeyError(f"Engineered features missing after feature engineering: {missing}")
    return out[keep].reset_index(drop=True)
