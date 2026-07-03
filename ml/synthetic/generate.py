"""Synthetic Rwandan driver-risk dataset utilities.

Loads the Fabricate-generated CSV, validates every category against the real
feature vocabulary from feature_contract.json, and exposes helpers for
inference payloads and contextual sanity checks.

IMPORTANT: This module is for functionality/robustness/context validation ONLY.
Results are NEVER merged into metrics.json or used as performance ground truth.
The Addis held-out test set remains the sole source of performance metrics.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

LABEL_COL = "synthetic_severity_label"
# Ordered ascending severity — used for monotonicity check.
SEVERITY_ORDER = ["Slight", "Serious", "Fatal"]

# ---------------------------------------------------------------------------
# Fabricate CSV -> contract vocabulary normalization map.
# The Fabricate tool generated abbreviated category names that differ from the
# Addis contract vocabulary. This map canonicalizes them before validation.
# Keys are (feature_name, fabricate_value); values are contract_value.
# ---------------------------------------------------------------------------
_CATEGORY_NORMALIZATIONS: dict[tuple[str, str], str] = {
    # vehicle_type: Fabricate uses verbose public-transport labels
    ("vehicle_type", "Public (12 seats)"): "Public_transport",
    ("vehicle_type", "Public (>45 seats)"): "Public_transport",
    # road_surface: Fabricate uses short names
    ("road_surface", "Asphalt"): "Asphalt roads",
    ("road_surface", "Earth"): "Earth roads",
    ("road_surface", "Gravel"): "Gravel roads",
    # light_condition: Fabricate uses abbreviated names
    ("light_condition", "Darkness - lit"): "Darkness - lights lit",
    ("light_condition", "Darkness - unlit"): "Darkness - lights unlit",
    ("light_condition", "Unknown"): "Darkness - no lighting",
}


# ---------------------------------------------------------------------------
# Vocabulary helpers
# ---------------------------------------------------------------------------

def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    """Apply _CATEGORY_NORMALIZATIONS in-place (returns a copy)."""
    df = df.copy()
    for (feat, raw_val), canonical in _CATEGORY_NORMALIZATIONS.items():
        if feat in df.columns:
            df[feat] = df[feat].replace(raw_val, canonical)
    return df


def _load_contract(contract_path: str | Path) -> dict:
    return json.loads(Path(contract_path).read_text(encoding="utf-8"))


def _build_vocab(contract: dict) -> dict[str, set[str]]:
    """Map feature_name -> set of allowed category strings from the contract."""
    return {
        f["name"]: set(str(c) for c in f["categories"])
        for f in contract["input_features"]
        if f.get("categories")
    }


def _contract_feature_names(contract: dict) -> list[str]:
    return [f["name"] for f in contract["input_features"]]


# ---------------------------------------------------------------------------
# Load + validate
# ---------------------------------------------------------------------------

def load_and_validate(
    fabricate_csv: str | Path,
    contract_path: str | Path,
) -> pd.DataFrame:
    """Load the Fabricate CSV and validate every category against the contract vocab.

    Raises ValueError listing all unseen-category violations found.
    Returns the validated DataFrame (all 14 columns including synthetic_severity_label).
    """
    df = pd.read_csv(fabricate_csv)

    if LABEL_COL not in df.columns:
        raise ValueError(f"CSV missing required column '{LABEL_COL}'")

    # Normalize Fabricate-generated abbreviated category names to contract vocabulary.
    df = _normalize(df)

    contract = _load_contract(contract_path)
    vocab = _build_vocab(contract)
    contract_features = _contract_feature_names(contract)

    # Validate that all contract features are present in the CSV.
    missing_cols = [f for f in contract_features if f not in df.columns]
    if missing_cols:
        raise ValueError(f"CSV missing contract feature columns: {missing_cols}")

    # Validate every category value against the contract vocabulary.
    violations: list[str] = []
    for feat, allowed in vocab.items():
        if feat not in df.columns:
            continue
        seen = set(df[feat].dropna().astype(str).unique())
        unseen = seen - allowed
        if unseen:
            violations.append(f"  {feat}: unseen categories {sorted(unseen)}")

    if violations:
        raise ValueError(
            "Synthetic CSV contains categories not in the feature contract:\n"
            + "\n".join(violations)
        )

    logger.info(
        "load_and_validate: %d rows, %d features validated OK",
        len(df),
        len(contract_features),
    )
    return df


# ---------------------------------------------------------------------------
# Inference payload builder
# ---------------------------------------------------------------------------

def to_predict_payloads(
    df: pd.DataFrame,
    contract_path: str | Path,
) -> list[dict[str, Any]]:
    """Convert a validated synthetic DataFrame to /predict-compatible payloads.

    Returns list of {"features": {feature_name: value, ...}} dicts, one per row,
    using only the contract's input_features (drops synthetic_severity_label and
    any extra columns not in the contract).
    """
    contract = _load_contract(contract_path)
    feature_names = _contract_feature_names(contract)
    records = df[feature_names].to_dict(orient="records")
    return [{"features": r} for r in records]


# ---------------------------------------------------------------------------
# Sanity check
# ---------------------------------------------------------------------------

def sanity_check(
    df: pd.DataFrame,
    model_path: str | Path,
    encoder_path: str | Path,
    contract_path: str | Path,
) -> dict[str, Any]:
    """Run a contextual sanity check: mean P(Fatal) and P(Serious) grouped by
    synthetic_severity_label, asserting the expected monotonic trend.

    This is CONTEXT VALIDATION ONLY — results are never merged into metrics.json.

    Returns a summary dict with per-label mean probabilities and a
    'monotonic_fatal' / 'monotonic_serious' boolean.
    """
    import joblib

    contract = _load_contract(contract_path)
    feature_names = _contract_feature_names(contract)
    classes = contract["target"]["classes"]  # e.g. ["Slight Injury","Serious Injury","Fatal Injury"]

    # Map contract class names to severity labels used in the synthetic CSV.
    # Contract uses "Slight Injury" / "Serious Injury" / "Fatal Injury";
    # synthetic label uses "Slight" / "Serious" / "Fatal".
    fatal_idx = next((i for i, c in enumerate(classes) if "Fatal" in c), len(classes) - 1)
    serious_idx = next((i for i, c in enumerate(classes) if "Serious" in c), 1)

    model = joblib.load(model_path)
    X = df[feature_names].copy()
    proba = model.predict_proba(X)  # (n, n_classes)

    df = df.copy()
    df["_p_fatal"] = proba[:, fatal_idx]
    df["_p_serious"] = proba[:, serious_idx]

    present_labels = [lbl for lbl in SEVERITY_ORDER if lbl in df[LABEL_COL].values]
    grouped = (
        df.groupby(LABEL_COL)[["_p_fatal", "_p_serious"]]
        .mean()
        .reindex(present_labels)
    )

    p_fatal = grouped["_p_fatal"].tolist()
    p_serious = grouped["_p_serious"].tolist()

    monotonic_fatal = all(p_fatal[i] <= p_fatal[i + 1] for i in range(len(p_fatal) - 1))
    monotonic_serious = all(p_serious[i] <= p_serious[i + 1] for i in range(len(p_serious) - 1))

    result: dict[str, Any] = {
        "note": (
            "CONTEXTUAL SANITY CHECK — synthetic Rwandan dataset. "
            "NOT a performance metric. Never merged into metrics.json."
        ),
        "labels_evaluated": present_labels,
        "mean_p_fatal": dict(zip(present_labels, [round(v, 4) for v in p_fatal])),
        "mean_p_serious": dict(zip(present_labels, [round(v, 4) for v in p_serious])),
        "monotonic_fatal": monotonic_fatal,
        "monotonic_serious": monotonic_serious,
        "n_rows": len(df),
    }

    logger.info(
        "[SANITY CHECK] mean P(Fatal) by label: %s | monotonic=%s",
        result["mean_p_fatal"],
        monotonic_fatal,
    )
    return result
