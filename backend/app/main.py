"""FastAPI application entry point.

This service LOADS a versioned ML artifact and serves inference; it never trains.
On startup it: (1) creates tables, (2) loads the selected artifact and validates
it against its feature contract (fail fast on mismatch), (3) records the served
artifact in the ModelVersion registry.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..api import drivers, health, models, predict, synthetic_validation
from ..auth import router as auth_router
from ..database.session import SessionLocal, init_db
from ..services.model_service import ArtifactNotFoundError, model_service
from ..services.registry import ensure_model_version
from .config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend.app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    try:
        model_service.load()
    except ArtifactNotFoundError as exc:
        # No servable artifact yet -> start DEGRADED (health reports it, /predict 503).
        logger.warning("starting without a model: %s", exc)
    # NOTE: ContractMismatchError is intentionally NOT caught -> fail fast.

    if model_service.loaded:
        with SessionLocal() as db:
            mv = ensure_model_version(db, model_service)
            logger.info("active model version: id=%s %s v%s", mv.id, mv.name, mv.version)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="mbere-ml Inference API",
        version="0.1.0",
        description=(
            "Driver road-accident risk inference. Loads a versioned ML artifact "
            "(model + feature contract) and serves predictions with SHAP explanations."
        ),
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(auth_router.router)
    app.include_router(predict.router)
    app.include_router(drivers.router)
    app.include_router(models.router)
    app.include_router(synthetic_validation.router)

    @app.get("/", tags=["system"])
    def root() -> dict:
        return {"service": settings.app_name, "docs": "/docs", "health": "/health"}

    return app


app = create_app()
