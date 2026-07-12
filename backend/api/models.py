"""Model registry, catalog, activation, and feature-contract endpoints."""
from __future__ import annotations

import json
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth.deps import get_current_user
from ..database.models import ModelVersion, User
from ..database.session import get_db
from ..schemas.prediction import (
    ContractFeature,
    FeatureContractResponse,
    ModelCatalogEntry,
    ModelCatalogResponse,
    ModelInfo,
    ModelPerformance,
    ModelVersionRead,
)
from ..services.model_registry import model_registry
from ..services.model_service import ArtifactNotFoundError, ContractMismatchError
from ..services.registry import activate_model_version

logger = logging.getLogger("backend.api.models")
router = APIRouter(prefix="/models", tags=["models"])


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


@router.get("", response_model=list[ModelVersionRead])
def list_models(db: Session = Depends(get_db)) -> list[ModelVersion]:
    return list(
        db.scalars(select(ModelVersion).order_by(ModelVersion.created_at.desc())).all()
    )


@router.get("/catalog", response_model=ModelCatalogResponse)
def model_catalog(db: Session = Depends(get_db)) -> ModelCatalogResponse:
    """All models found on disk under model_catalog_dir, merged with DB
    is_active status. Never deserializes a .pkl — only reads meta.json /
    reports/<name>/metrics.json, so listing stays cheap regardless of file size."""
    catalog_dir = model_registry.catalog_dir()
    entries: list[ModelCatalogEntry] = []
    for name in model_registry.available_names():
        meta = _read_json(catalog_dir / f"{name}.meta.json")
        test_metrics_raw = _read_json(catalog_dir / "reports" / name / "metrics.json")
        db_row = db.scalar(
            select(ModelVersion)
            .where(ModelVersion.name == name, ModelVersion.run_dir == str(catalog_dir))
            .order_by(ModelVersion.created_at.desc())
        )
        dataset = meta.get("dataset") or {}
        entries.append(
            ModelCatalogEntry(
                name=name,
                version=str(meta.get("model_version", "unknown")),
                dataset_name=dataset.get("name", ""),
                kind=dataset.get("kind", ""),
                target_classes=list(dataset.get("classes", [])),
                git_commit=meta.get("git_commit"),
                created_utc=meta.get("created_utc"),
                metrics_cv=meta.get("metrics_cv", {}) or {},
                metrics_test=ModelPerformance(**test_metrics_raw) if test_metrics_raw else None,
                is_active=bool(db_row.is_active) if db_row else False,
                model_version_id=db_row.id if db_row else None,
            )
        )
    return ModelCatalogResponse(catalog_dir=str(catalog_dir), models=entries)


@router.get("/contract", response_model=FeatureContractResponse)
def active_contract() -> FeatureContractResponse:
    svc = model_registry.default()
    if svc is None or not svc.loaded:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "no model loaded")
    return FeatureContractResponse(
        model=ModelInfo(**svc.model_info()),
        input_features=[ContractFeature(**f) for f in svc.contract.features],
    )


@router.post("/{name}/activate", response_model=ModelVersionRead)
def activate_model(
    name: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ModelVersion:
    if name not in model_registry.available_names():
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"unknown model '{name}'")
    try:
        svc = model_registry.get(name)
    except ArtifactNotFoundError:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, f"model '{name}' artifact is missing on disk"
        )
    except ContractMismatchError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc))
    except Exception:
        logger.exception("model '%s' failed to load", name)
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, f"model '{name}' failed to load; see server logs"
        )
    model_registry.set_default(name)
    return activate_model_version(db, svc)
