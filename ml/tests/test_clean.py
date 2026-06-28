"""Tests for ml.preprocessing.clean (incl. a missing-value case)."""
from __future__ import annotations

import logging

import pandas as pd

from ml.preprocessing.clean import clean


def test_clean_drops_leakage_columns(tiny_clean_df):
    assert "Casualty_severity" not in tiny_clean_df.columns


def test_clean_parses_time_to_hour(tiny_clean_df):
    assert "Time" not in tiny_clean_df.columns
    # 5 raw rows -> 4 after the malformed-target row is dropped
    assert tiny_clean_df["hour_of_day"].tolist() == [17, 1, 23, 8]


def test_clean_missing_value_case(tiny_clean_df):
    # 'unknown' / 'na' (case-insensitive) and empties -> constant fill 'Unknown';
    # leading/trailing whitespace trimmed.
    assert tiny_clean_df["Age"].tolist() == ["18-30", "31-50", "Unknown", "Over 51"]
    assert tiny_clean_df["Vehicle"].tolist() == ["Motorcycle", "Lorry (11?40Q)", "Unknown", "Automobile"]
    assert tiny_clean_df["Weather"].tolist() == ["Normal", "Raining", "Normal", "Unknown"]
    for col in ["Age", "Vehicle", "Weather"]:
        assert tiny_clean_df[col].isna().sum() == 0


def test_clean_drops_malformed_target_rows(tiny_raw_df, tiny_config):
    out = clean(tiny_raw_df, tiny_config)
    assert len(out) == 4  # 'Bogus' target row dropped
    assert set(out["Severity"]) <= set(tiny_config.target.classes)


def test_clean_canonicalizes_target_label(tiny_clean_df):
    assert tiny_clean_df["Severity"].tolist() == ["Slight", "Fatal", "Serious", "Slight"]


def test_clean_does_not_mutate_input(tiny_raw_df, tiny_config):
    before = tiny_raw_df.copy(deep=True)
    _ = clean(tiny_raw_df, tiny_config)
    pd.testing.assert_frame_equal(tiny_raw_df, before)


def test_clean_logs_row_counts(tiny_raw_df, tiny_config):
    messages: list[str] = []

    class _Capture(logging.Handler):
        def emit(self, record):
            messages.append(record.getMessage())

    logger = logging.getLogger("test-clean")
    logger.handlers = [_Capture()]
    logger.setLevel(logging.INFO)

    clean(tiny_raw_df, tiny_config, logger=logger)

    assert any("rows 5 -> 4" in m for m in messages)
    assert any("invalid target" in m for m in messages)
