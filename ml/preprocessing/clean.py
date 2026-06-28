"""Deterministic, leakage-safe cleaning of the raw accident data.

Every operation here is row-wise and parameter-free (no statistic is learned
from the data), so it is safe to apply to the full dataset before splitting.
Learned transforms (one-hot categories, scaling) live in ``encode.py`` and are
fit on the TRAIN fold only.
"""
from __future__ import annotations

import logging

import pandas as pd
from pandas.api.types import is_numeric_dtype

from ..utils.config import DatasetConfig
from ..utils.logging import get_logger
from .load import load_raw


def _string_columns(df: pd.DataFrame, exclude: list[str]) -> list[str]:
    """Non-numeric columns (pandas 3 loads text as `str`/`string`, not `object`)."""
    return [c for c in df.columns if c not in exclude and not is_numeric_dtype(df[c])]


def parse_time(df: pd.DataFrame, time_column: str | None, derived: str | None) -> pd.DataFrame:
    """Derive an integer hour-of-day from an ``HH:MM:SS`` column; drop the raw column."""
    if not time_column or time_column not in df.columns:
        return df
    hours = df[time_column].astype("string").str.strip().str.split(":").str[0]
    df[derived] = pd.to_numeric(hours, errors="coerce")
    return df.drop(columns=[time_column])


def clean(df: pd.DataFrame, config: DatasetConfig, logger: logging.Logger | None = None) -> pd.DataFrame:
    """Clean raw data and return all surviving columns (feature engineering runs next).

    Steps: trim headers; drop leakage columns; derive hour-of-day; trim string
    cells and map missing tokens -> constant fill; canonicalize the target; drop
    malformed rows (missing/invalid target, unparseable hour). Logs row counts.
    """
    logger = logger or get_logger()
    cfg = config.clean
    n_start = len(df)

    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    # Drop post-accident outcome (casualty) columns to prevent target leakage.
    df = df.drop(columns=[c for c in cfg.leakage_columns if c in df.columns])

    # Time -> hour_of_day, drop the raw timestamp.
    df = parse_time(df, cfg.time_column, cfg.time_derived)

    target = config.target.column
    tokens = {str(t).strip().lower() for t in cfg.missing_tokens}

    # Trim + normalize missing tokens on every non-numeric column except the
    # target, then constant-fill (leakage-safe).
    for col in _string_columns(df, exclude=[target]):
        series = df[col].astype("string").str.strip()
        is_missing = series.isna() | series.str.lower().isin(tokens).fillna(False)
        df[col] = series.mask(is_missing, pd.NA).fillna(cfg.categorical_fill_value)

    # Canonicalize target labels; drop malformed-target rows (missing or not in classes).
    df[target] = df[target].astype("string").str.strip().replace(config.target.label_map)
    valid_target = df[target].notna() & df[target].isin(config.target.classes)
    dropped_target = int((~valid_target).sum())
    if dropped_target:
        bad = sorted(set(df.loc[~valid_target, target].dropna().unique()))
        logger.warning("Dropping %d rows with missing/invalid target %s", dropped_target, bad)
    df = df[valid_target].copy()

    # Drop rows whose hour-of-day could not be parsed (malformed time).
    derived = cfg.time_derived
    if derived and derived in df.columns:
        bad_hour = df[derived].isna()
        if int(bad_hour.sum()):
            logger.warning("Dropping %d rows with unparseable %s", int(bad_hour.sum()), derived)
            df = df[~bad_hour].copy()

    df = df.reset_index(drop=True)
    logger.info("clean: rows %d -> %d (dropped %d); cols=%d",
                n_start, len(df), n_start - len(df), df.shape[1])
    return df


def load_and_clean(config: DatasetConfig, logger: logging.Logger | None = None) -> pd.DataFrame:
    """Convenience: read the raw CSV from ``config.paths.raw`` and clean it."""
    return clean(load_raw(config.paths.raw), config, logger=logger)
