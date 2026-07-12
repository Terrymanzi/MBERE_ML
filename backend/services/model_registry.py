"""Multi-model catalog: lazily-loaded, cached ModelService instances.

The selectable catalog is the set of top-level `{name}.pkl` files under
`settings.model_catalog_dir` (default `ml/artifacts`) — today that's
baseline / random_forest / random_forest_tuned / xgboost / xgboost_tuned, all
sharing one feature_contract.json in that same directory. Listing the catalog
only reads meta.json / reports/<name>/metrics.json (cheap); a model's .pkl is
only deserialized the first time it's actually selected (activated or used as
a /predict override), then cached for the life of the process — some of these
artifacts are tens of MB, so eagerly loading all of them isn't worth it.
"""
from __future__ import annotations

import logging
import threading
from pathlib import Path

from ..app.config import PROJECT_ROOT, Settings, get_settings
from .model_service import ModelService

logger = logging.getLogger("backend.model_registry")


def resolve_path(path_str: str) -> Path:
    p = Path(path_str)
    return p if p.is_absolute() else (PROJECT_ROOT / p).resolve()


class ModelRegistry:
    def __init__(self) -> None:
        self._settings: Settings | None = None
        # Catalog-scoped instances only, keyed by catalog name — never holds a
        # legacy MODEL_RUN_DIR pin (see seed()), so a pinned artifact whose name
        # happens to match a real catalog entry can't shadow it.
        self._cache: dict[str, ModelService] = {}
        self._default: ModelService | None = None
        self._lock = threading.Lock()

    def configure(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._cache.clear()
        self._default = None

    def catalog_dir(self) -> Path:
        settings = self._settings or get_settings()
        return resolve_path(settings.model_catalog_dir)

    def available_names(self) -> list[str]:
        d = self.catalog_dir()
        return sorted(p.stem for p in d.glob("*.pkl")) if d.exists() else []

    def get(self, name: str) -> ModelService:
        """Lazily load + cache the named catalog model. Raises whatever
        ModelService.load() raises uncaught — ArtifactNotFoundError /
        ContractMismatchError, but also arbitrary deserialization errors
        (e.g. a pickle saved under an incompatible scikit-learn version)."""
        with self._lock:
            if name not in self._cache:
                settings = self._settings or get_settings()
                per_model_settings = settings.model_copy(
                    update={"model_name": name, "model_run_dir": str(self.catalog_dir())}
                )
                svc = ModelService()
                svc.load(per_model_settings)
                self._cache[name] = svc
            return self._cache[name]

    def try_get(self, name: str) -> ModelService | None:
        """Best-effort load: any failure (missing artifact, contract
        mismatch, a pickle that fails to deserialize in this environment,
        ...) makes this one model unavailable rather than fatal."""
        try:
            return self.get(name)
        except Exception as exc:
            logger.warning("catalog model '%s' failed to load: %s", name, exc)
            return None

    def seed(self, service: ModelService) -> None:
        """Adopt an already-loaded, out-of-catalog instance (legacy
        MODEL_RUN_DIR pin escape hatch — see app/main.py) as the current
        default WITHOUT entering the catalog cache: its name may coincide with
        a real catalog entry backed by a different run_dir, and get(name) must
        keep resolving that name to the actual catalog artifact."""
        self._default = service

    def set_default(self, name: str) -> None:
        self._default = self.get(name)

    def default(self) -> ModelService | None:
        return self._default


model_registry = ModelRegistry()
