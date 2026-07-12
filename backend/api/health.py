"""Liveness/readiness endpoint (no auth)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..database.session import get_db
from ..schemas.prediction import HealthResponse, ModelInfo
from ..services.model_registry import model_registry

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)) -> HealthResponse:
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    svc = model_registry.default()
    loaded = svc is not None and svc.loaded
    model = ModelInfo(**svc.model_info()) if loaded else None
    n_features = len(svc.feature_names) if loaded else None
    status = "ok" if (db_ok and loaded) else "degraded"
    return HealthResponse(
        status=status,
        db_ok=db_ok,
        model_loaded=loaded,
        model=model,
        n_input_features=n_features,
    )
