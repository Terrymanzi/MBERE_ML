"""POST /predict — inference + persisted audit trail."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth.deps import get_current_user
from ..database.models import Driver, FeatureRecord, Prediction, RiskAssessment, User
from ..database.session import get_db
from ..schemas.prediction import (
    Explanation,
    ModelInfo,
    PredictRequest,
    PredictResponse,
)
from ..services.model_registry import model_registry
from ..services.model_service import ArtifactNotFoundError, FeatureValidationError
from ..services.registry import ensure_model_version_row

logger = logging.getLogger("backend.api.predict")
router = APIRouter(tags=["prediction"])


@router.post("/predict", response_model=PredictResponse)
def predict(
    payload: PredictRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PredictResponse:
    if payload.model_name is not None:
        if payload.model_name not in model_registry.available_names():
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, f"unknown model '{payload.model_name}'"
            )
        try:
            svc = model_registry.get(payload.model_name)
        except Exception:
            logger.exception("model '%s' failed to load", payload.model_name)
            raise HTTPException(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                f"model '{payload.model_name}' is unavailable",
            )
    else:
        svc = model_registry.default()

    if svc is None or not svc.loaded:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "no model loaded")

    # optional driver linkage
    if payload.driver_id is not None and db.get(Driver, payload.driver_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "driver not found")

    # inference (bad features -> 422)
    try:
        result = svc.predict(payload.features)
    except FeatureValidationError as exc:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            {"message": "feature validation failed", "errors": exc.errors},
        )
    except ArtifactNotFoundError:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "no model loaded")

    # register-only: never flips the org-wide active flag, so a one-off
    # override doesn't redefine the default model.
    model_version = ensure_model_version_row(db, svc)

    # persist audit trail: features -> assessment -> prediction
    feature_record = FeatureRecord(driver_id=payload.driver_id, payload=payload.features)
    db.add(feature_record)
    db.flush()

    assessment = RiskAssessment(
        driver_id=payload.driver_id,
        feature_record_id=feature_record.id,
        model_version_id=model_version.id,
        created_by_user_id=user.id,
        status="completed",
    )
    db.add(assessment)
    db.flush()

    prediction = Prediction(
        risk_assessment_id=assessment.id,
        model_version_id=model_version.id,
        predicted_class=result.predicted_class,
        risk_band=result.risk_band,
        risk_score=result.risk_score,
        probabilities=result.probabilities,
        explanation=result.explanation,
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return PredictResponse(
        risk_assessment_id=assessment.id,
        prediction_id=prediction.id,
        driver_id=payload.driver_id,
        model=ModelInfo(**svc.model_info()),
        predicted_class=result.predicted_class,
        risk_band=result.risk_band,
        risk_score=result.risk_score,
        probabilities=result.probabilities,
        explanation=Explanation(**result.explanation),
        created_at=prediction.created_at,
    )
