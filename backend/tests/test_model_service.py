"""Startup contract validation: the loaded model must match its feature contract."""
from __future__ import annotations

import json

import pytest

from backend.app.config import Settings
from backend.services.model_service import (
    ContractMismatchError,
    FeatureValidationError,
    ModelService,
)


def _settings_for(run_dir) -> Settings:
    return Settings(
        model_run_dir=str(run_dir),
        model_name="random_forest",
        database_url="sqlite:///./ignored_for_service_test.db",
        secret_key="test",
    )


def test_load_succeeds_on_matching_contract(tmp_path, build_artifact):
    run = tmp_path / "good"
    run.mkdir()
    build_artifact(run)
    svc = ModelService()
    svc.load(_settings_for(run))
    assert svc.loaded
    assert svc.feature_names == ["vehicle_type", "driver_age", "driver_experience"]


def test_load_fails_fast_on_contract_mismatch(tmp_path, build_artifact):
    run = tmp_path / "bad"
    run.mkdir()
    # contract advertises a feature the model was never trained on
    build_artifact(run, feature_names_override=["vehicle_type", "driver_age", "WRONG_NAME"])
    svc = ModelService()
    with pytest.raises(ContractMismatchError):
        svc.load(_settings_for(run))
    assert not svc.loaded


def test_validate_features_coerces_and_orders(tmp_path, build_artifact):
    run = tmp_path / "coerce"
    run.mkdir()
    build_artifact(run)
    svc = ModelService()
    svc.load(_settings_for(run))

    coerced = svc.validate_features(
        {"driver_experience": "2", "vehicle_type": "Lorry", "driver_age": 30}
    )
    assert list(coerced) == ["vehicle_type", "driver_age", "driver_experience"]  # contract order
    assert coerced["driver_age"] == 30.0 and isinstance(coerced["driver_age"], float)

    with pytest.raises(FeatureValidationError):
        svc.validate_features({"vehicle_type": "Lorry", "driver_age": 30})  # missing one
