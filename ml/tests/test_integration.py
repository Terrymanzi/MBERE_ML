"""Config sanity + end-to-end preprocess on the real Addis dataset."""
from __future__ import annotations

import json

import numpy as np
import pytest

from ml.preprocessing.preprocess import run
from ml.preprocessing.split import make_split
from ml.utils.config import load_config
from ml.utils.paths import PROJECT_ROOT

ADDIS_CONFIG = PROJECT_ROOT / "ml" / "configs" / "addis.yaml"


def test_addis_config_structure():
    cfg = load_config(ADDIS_CONFIG)
    assert cfg.kind == "multiclass"
    assert cfg.target.classes == ["Slight Injury", "Serious Injury", "Fatal Injury"]
    assert "Casualty_severity" in cfg.clean.leakage_columns
    assert "Number_of_casualties" in cfg.clean.leakage_columns
    assert list(cfg.features.ordinal) == [
        "driver_age_band", "driver_experience", "time_of_day",
        "driver_education", "vehicle_service_year",
    ]
    assert cfg.features.onehot == [
        "vehicle_type", "weather", "road_surface", "light_condition",
        "driver_sex", "driver_vehicle_relation", "vehicle_owner", "vehicle_defect",
    ]
    assert cfg.split.k_folds == 5


def test_split_is_stratified_and_reproducible():
    cfg = load_config(ADDIS_CONFIG)
    if not cfg.paths.raw.exists():
        pytest.skip("raw dataset not found")
    from ml.preprocessing.clean import load_and_clean
    from ml.features.feature_engineering import engineer_features

    eng = engineer_features(load_and_clean(cfg), cfg)
    a_train, a_test = make_split(eng, cfg)
    b_train, b_test = make_split(eng, cfg)
    np.testing.assert_array_equal(a_train, b_train)  # reproducible
    np.testing.assert_array_equal(a_test, b_test)
    # disjoint + complete
    assert set(a_train).isdisjoint(set(a_test))
    assert len(a_train) + len(a_test) == len(eng)


@pytest.mark.parametrize("name", ["addis"])
def test_preprocess_end_to_end(tmp_path, name):
    cfg = load_config(ADDIS_CONFIG)
    if not cfg.paths.raw.exists():
        pytest.skip("raw dataset not found")
    cfg.paths.processed_dir = tmp_path / "processed"
    cfg.paths.artifacts_dir = tmp_path / "artifacts"

    result = run(cfg)

    # DoD artifacts exist
    for path in (result.train_path, result.test_path, result.encoder_path,
                 result.contract_path, result.split_path):
        assert path.exists(), f"missing {path}"
    assert (cfg.paths.processed_dir / f"{name}_train_encoded.npz").exists()
    assert (cfg.paths.processed_dir / f"{name}_test_encoded.npz").exists()

    # feature contract is well-formed and leakage-free
    contract = json.loads(result.contract_path.read_text(encoding="utf-8"))
    assert contract["dataset"] == name
    assert contract["target"]["classes"] == cfg.target.classes
    assert len(contract["input_features"]) == len(result.selected_features)
    assert contract["n_encoded_features"] == len(contract["encoded_feature_names"])
    assert contract["rows"]["train"] + contract["rows"]["test"] == contract["rows"]["total"]
    feature_names = {f["name"] for f in contract["input_features"]}
    assert feature_names.isdisjoint(set(cfg.clean.leakage_columns))

    # encoded matrices: train-fit dims applied to test
    train_npz = np.load(cfg.paths.processed_dir / f"{name}_train_encoded.npz")
    test_npz = np.load(cfg.paths.processed_dir / f"{name}_test_encoded.npz")
    assert train_npz["X"].shape[1] == test_npz["X"].shape[1] == contract["n_encoded_features"]
    assert train_npz["X"].shape[0] == result.n_train
    assert set(np.unique(train_npz["y"])).issubset({0, 1, 2})
