"""ModelRegistry: catalog listing + lazy-load/cache semantics."""
from __future__ import annotations

import pytest

from backend.app.config import Settings
from backend.services.model_registry import ModelRegistry
from backend.services.model_service import ArtifactNotFoundError


def _settings_for(catalog_dir) -> Settings:
    return Settings(
        model_catalog_dir=str(catalog_dir),
        database_url="sqlite:///./ignored_for_registry_test.db",
        secret_key="test",
    )


def test_available_names_lists_catalog_pkls(catalog_dir):
    registry = ModelRegistry()
    registry.configure(_settings_for(catalog_dir))
    assert registry.available_names() == ["baseline", "random_forest"]


def test_get_caches_by_identity(catalog_dir):
    registry = ModelRegistry()
    registry.configure(_settings_for(catalog_dir))
    first = registry.get("baseline")
    second = registry.get("baseline")
    assert first is second


def test_get_unknown_name_raises(catalog_dir):
    registry = ModelRegistry()
    registry.configure(_settings_for(catalog_dir))
    with pytest.raises(ArtifactNotFoundError):
        registry.get("nope")


def test_try_get_unknown_name_returns_none(catalog_dir):
    registry = ModelRegistry()
    registry.configure(_settings_for(catalog_dir))
    assert registry.try_get("nope") is None


def test_default_is_none_before_set(catalog_dir):
    registry = ModelRegistry()
    registry.configure(_settings_for(catalog_dir))
    assert registry.default() is None
    svc = registry.get("baseline")
    registry.set_default("baseline")
    assert registry.default() is svc
