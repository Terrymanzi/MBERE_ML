"""POST /predict — inference + persisted audit trail."""
from __future__ import annotations

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
from ..services.model_service import (
    ArtifactNotFoundError,
    FeatureValidationError,
    model_service,
)
from ..services.registry import get_active_model_version

router = APIRouter(tags=["prediction"])


@router.post("/predict", response_model=PredictResponse)
def predict(
    payload: PredictRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PredictResponse:
    if not model_service.loaded:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "no model loaded")

    # optional driver linkage
    if payload.driver_id is not None and db.get(Driver, payload.driver_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "driver not found")

    # inference (bad features -> 422)
    try:
        result = model_service.predict(payload.features)
    except FeatureValidationError as exc:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            {"message": "feature validation failed", "errors": exc.errors},
        )
    except ArtifactNotFoundError:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "no model loaded")

    model_version = get_active_model_version(db, model_service)

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
        model=ModelInfo(**model_service.model_info()),
        predicted_class=result.predicted_class,
        risk_band=result.risk_band,
        risk_score=result.risk_score,
        probabilities=result.probabilities,
        explanation=Explanation(**result.explanation),
        created_at=prediction.created_at,
    )
