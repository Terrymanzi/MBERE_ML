"""Tests for ml.preprocessing.encode (incl. an unseen-category case + persistence)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from sklearn.compose import ColumnTransformer
from sklearn.exceptions import NotFittedError

from ml.features.feature_engineering import engineer_features
from ml.preprocessing.encode import (
    build_encoder,
    encode_target,
    encoded_feature_names,
    fit_encoder,
    load_encoder,
    save_encoder,
    transform,
)


def _engineered(tiny_clean_df, tiny_config):
    return engineer_features(tiny_clean_df, tiny_config)


def test_build_encoder_is_unfitted(tiny_config):
    enc = build_encoder(tiny_config)
    assert isinstance(enc, ColumnTransformer)
    dummy = pd.DataFrame({
        "driver_age_band": ["18-30"], "time_of_day": ["Morning"],
        "vehicle_type": ["Motorcycle"], "weather": ["Normal"], "Num_vehicles": [2],
    })
    with pytest.raises(NotFittedError):
        enc.transform(dummy)


def test_fit_on_train_only_unseen_onehot_is_zero(tiny_clean_df, tiny_config):
    """Encoder fit on TRAIN only; a one-hot category seen only at test time maps
    to an all-zero block (handle_unknown='ignore') instead of raising."""
    eng = _engineered(tiny_clean_df, tiny_config)
    features = tiny_config.features.all
    train, test = eng.iloc[:2][features], eng.iloc[2:][features]
    # train vehicle_type = {Motorcycle, Lorry}; test vehicle_type = {Unknown, Other} (unseen)

    enc = fit_encoder(build_encoder(tiny_config), train)
    X_test = transform(enc, test)
    names = encoded_feature_names(enc)

    veh_cols = [i for i, n in enumerate(names) if n.startswith("onehot__vehicle_type_")]
    assert veh_cols, "expected vehicle_type one-hot columns"
    assert X_test[:, veh_cols].sum() == 0  # every unseen category -> all zeros


def test_ordinal_unseen_maps_to_minus_one(tiny_clean_df, tiny_config):
    eng = _engineered(tiny_clean_df, tiny_config)
    enc = fit_encoder(build_encoder(tiny_config), eng[tiny_config.features.all])

    oov = pd.DataFrame({
        "driver_age_band": ["Mars"],  # not in the ordinal category list
        "time_of_day": ["Morning"], "vehicle_type": ["Motorcycle"],
        "weather": ["Normal"], "Num_vehicles": [2],
    })
    X = transform(enc, oov)
    names = encoded_feature_names(enc)
    idx = names.index("ordinal__driver_age_band")
    assert X[0, idx] == -1


def test_encoder_persistence_roundtrip(tiny_clean_df, tiny_config, tmp_path):
    eng = _engineered(tiny_clean_df, tiny_config)
    X = eng[tiny_config.features.all]
    enc = fit_encoder(build_encoder(tiny_config), X)
    expected = transform(enc, X)

    path = save_encoder(enc, tmp_path / "art" / "encoders.joblib")
    assert path.exists()
    reloaded = load_encoder(path)
    np.testing.assert_array_equal(transform(reloaded, X), expected)


def test_encode_target_uses_config_order(tiny_config):
    codes, classes = encode_target(["Fatal", "Slight", "Serious"], tiny_config)
    assert classes == ["Slight", "Serious", "Fatal"]
    assert codes.tolist() == [2, 0, 1]  # not alphabetical


def test_encode_target_applies_label_map(tiny_config):
    codes, _ = encode_target(["fatal"], tiny_config)
    assert codes.tolist() == [2]


def test_encode_target_raises_on_unknown(tiny_config):
    with pytest.raises(ValueError, match="not in configured classes"):
        encode_target(["Bogus"], tiny_config)
