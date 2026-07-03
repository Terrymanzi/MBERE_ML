"""Tests for ml.synthetic.generate.

Covers:
  - Schema / columns match feature_contract input_features + synthetic_severity_label
  - Every category is in-vocabulary
  - Determinism on fixed seed (to_predict_payloads output is stable)
  - Class-conditional guard: two classes with different real marginals produce
    different synthetic marginals
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ml.synthetic.generate import (
    LABEL_COL,
    SEVERITY_ORDER,
    _build_vocab,
    _contract_feature_names,
    _load_contract,
    load_and_validate,
    to_predict_payloads,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FABRICATE_CSV = Path("data/external/synthetic/rwanda_driver_risk_profiles_synthetic.csv")
# Use the latest run's contract (11-feature, threshold=0.0003).
CONTRACT_PATH = Path("ml/artifacts/runs/20260703_212032_8044df6/feature_contract.json")


@pytest.fixture(scope="module")
def contract() -> dict:
    if not CONTRACT_PATH.exists():
        pytest.skip(f"Contract not found: {CONTRACT_PATH}")
    return _load_contract(CONTRACT_PATH)


@pytest.fixture(scope="module")
def synthetic_df(contract) -> pd.DataFrame:
    if not FABRICATE_CSV.exists():
        pytest.skip(f"Fabricate CSV not found: {FABRICATE_CSV}")
    return load_and_validate(FABRICATE_CSV, CONTRACT_PATH)


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------

def test_columns_match_contract_plus_label(synthetic_df, contract):
    """All contract input_features + synthetic_severity_label must be present."""
    expected = set(_contract_feature_names(contract)) | {LABEL_COL}
    assert expected.issubset(set(synthetic_df.columns)), (
        f"Missing columns: {expected - set(synthetic_df.columns)}"
    )


def test_label_column_values(synthetic_df):
    """synthetic_severity_label must only contain known severity values."""
    assert set(synthetic_df[LABEL_COL].unique()).issubset(set(SEVERITY_ORDER))


# ---------------------------------------------------------------------------
# Vocabulary tests
# ---------------------------------------------------------------------------

def test_all_categories_in_vocabulary(synthetic_df, contract):
    """No unseen categories — load_and_validate already enforces this, but we
    assert it explicitly so a test failure gives a clear diagnostic."""
    vocab = _build_vocab(contract)
    for feat, allowed in vocab.items():
        if feat not in synthetic_df.columns:
            continue
        seen = set(synthetic_df[feat].dropna().astype(str).unique())
        unseen = seen - allowed
        assert not unseen, f"{feat}: unseen categories {sorted(unseen)}"


# ---------------------------------------------------------------------------
# Determinism test
# ---------------------------------------------------------------------------

def test_to_predict_payloads_determinism(synthetic_df, contract):
    """Same DataFrame -> same payloads on two calls (no randomness)."""
    p1 = to_predict_payloads(synthetic_df.head(10), CONTRACT_PATH)
    p2 = to_predict_payloads(synthetic_df.head(10), CONTRACT_PATH)
    assert p1 == p2


def test_to_predict_payloads_structure(synthetic_df, contract):
    """Each payload has exactly the contract feature names under 'features'."""
    feature_names = set(_contract_feature_names(contract))
    payloads = to_predict_payloads(synthetic_df.head(5), CONTRACT_PATH)
    assert len(payloads) == 5
    for p in payloads:
        assert set(p["features"].keys()) == feature_names


# ---------------------------------------------------------------------------
# Class-conditional marginal guard
# ---------------------------------------------------------------------------

def test_class_conditional_marginals_differ(synthetic_df):
    """Two classes with different real marginals (Slight vs Fatal) must produce
    different synthetic marginals for at least one feature.

    This guards against a degenerate generator that ignores the class label and
    samples from the pooled distribution for all classes.
    """
    slight = synthetic_df[synthetic_df[LABEL_COL] == "Slight"]
    fatal = synthetic_df[synthetic_df[LABEL_COL] == "Fatal"]

    if slight.empty or fatal.empty:
        pytest.skip("Both 'Slight' and 'Fatal' classes required for this test.")

    # Check vehicle_type distribution — the manifest specifies motorcycle_heavy
    # for high-severity classes, so Fatal should have more Motorcycles than Slight.
    feat = "vehicle_type"
    if feat not in synthetic_df.columns:
        pytest.skip(f"'{feat}' not in synthetic CSV.")

    slight_moto = (slight[feat] == "Motorcycle").mean()
    fatal_moto = (fatal[feat] == "Motorcycle").mean()

    # They must differ by at least 1 percentage point — a degenerate pooled
    # generator would produce identical marginals.
    assert abs(slight_moto - fatal_moto) > 0.01, (
        f"Motorcycle marginals are suspiciously identical: "
        f"Slight={slight_moto:.3f}, Fatal={fatal_moto:.3f}. "
        "Generator may not be class-conditional."
    )
