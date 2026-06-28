"""Model registry + feature-contract endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database.models import ModelVersion
from ..database.session import get_db
from ..schemas.prediction import (
    ContractFeature,
    FeatureContractResponse,
    ModelInfo,
    ModelVersionRead,
)
from ..services.model_service import ArtifactNotFoundError, model_service

router = APIRouter(prefix="/models", tags=["models"])


@router.get("", response_model=list[ModelVersionRead])
def list_models(db: Session = Depends(get_db)) -> list[ModelVersion]:
    return list(
        db.scalars(select(ModelVersion).order_by(ModelVersion.created_at.desc())).all()
    )


@router.get("/contract", response_model=FeatureContractResponse)
def active_contract() -> FeatureContractResponse:
    if not model_service.loaded:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "no model loaded")
    try:
        contract = model_service.contract
    except ArtifactNotFoundError:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "no model loaded")
    return FeatureContractResponse(
        model=ModelInfo(**model_service.model_info()),
        input_features=[ContractFeature(**f) for f in contract.features],
    )
