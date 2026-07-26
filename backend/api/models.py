"""Model registry, catalog, activation, and feature-contract endpoints."""
from __future__ import annotations

import json
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth.deps import require_role
from ..database.models import ModelVersion, User, UserRole
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
from ..services.audit import log_action
from ..services.model_registry import model_registry
from ..services.model_service import ArtifactNotFoundError, ContractMismatchError
from ..services.registry import activate_model_version

from ml.evaluation.gate import evaluate_gate

logger = logging.getLogger("backend.api.models")
router = APIRouter(prefix="/models", tags=["models"])

BASELINE_NAME = "baseline"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _gate_status(catalog_dir: Path, name: str) -> tuple[bool | None, list[str]]:
    """None (no reasons) when there's nothing to compare against (missing metrics,
    or `name` IS the baseline -- the baseline is the reference, not a candidate)."""
    if name == BASELINE_NAME:
        return None, []
    candidate = _read_json(catalog_dir / "reports" / name / "metrics.json")
    baseline = _read_json(catalog_dir / "reports" / BASELINE_NAME / "metrics.json")
    if not candidate or not baseline:
        return None, []
    result = evaluate_gate(candidate, baseline)
    return result.passed, result.reasons


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
        gate_passed, gate_reasons = _gate_status(catalog_dir, name)
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
                gate_passed=gate_passed,
                gate_reasons=gate_reasons,
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
    force: bool = False,
    db: Session = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN)),
) -> ModelVersion:
    """Set `name` as the served default. Blocked (409) for a candidate that fails
    the deployment decision gate -- it underperforms the rule-based baseline on a
    held-out-test headline metric -- unless `force=true` is passed as a deliberate,
    human-reviewed override (never done silently by the platform itself)."""
    if name not in model_registry.available_names():
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"unknown model '{name}'")

    if not force:
        gate_passed, gate_reasons = _gate_status(model_registry.catalog_dir(), name)
        if gate_passed is False:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                {
                    "message": (
                        f"model '{name}' fails the deployment decision gate: it "
                        "underperforms the rule-based baseline on held-out test "
                        "metrics. Retry with ?force=true to override deliberately."
                    ),
                    "reasons": gate_reasons,
                },
            )
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
    row = activate_model_version(db, svc)
    log_action(db, user, "activate", "model_version", row.id)
    return row
