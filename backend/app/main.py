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
from ..services.model_registry import model_registry, resolve_path
from ..services.model_service import ArtifactNotFoundError, ModelService
from ..services.registry import activate_model_version, get_active_model_version
from .config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend.app")


def _load_pin(settings) -> ModelService | None:
    """Load the legacy MODEL_RUN_DIR-pinned artifact and adopt it as default.
    Fails fast on a bad artifact, matching historical startup behavior for an
    explicit pin."""
    pinned = ModelService()
    try:
        pinned.load(settings)
    except ArtifactNotFoundError as exc:
        logger.warning("MODEL_RUN_DIR pin failed to load: %s", exc)
        return None
    model_registry.seed(pinned)
    return pinned


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    settings = get_settings()
    model_registry.configure(settings)
    catalog_dir = str(model_registry.catalog_dir())
    pin_dir = str(resolve_path(settings.model_run_dir)) if settings.model_run_dir else None

    with SessionLocal() as db:
        active_row = get_active_model_version(db)
        default_svc: ModelService | None = None

        if active_row is not None and active_row.run_dir == catalog_dir:
            # Previously activated via the catalog (the normal UI flow) —
            # rehydrate the same artifact regardless of what .env says.
            default_svc = model_registry.try_get(active_row.name)
            if default_svc is not None:
                model_registry.set_default(active_row.name)
        elif active_row is not None and pin_dir is not None and active_row.run_dir == pin_dir:
            # Previously activated via the legacy MODEL_RUN_DIR pin, and the
            # pin still points at the same place — reload it the same way.
            default_svc = _load_pin(settings)
        elif active_row is None:
            # Fresh DB: seed from configuration.
            if settings.model_run_dir:
                default_svc = _load_pin(settings)
            else:
                names = model_registry.available_names()
                seed_name = (
                    settings.model_name
                    if settings.model_name in names
                    else (names[0] if names else None)
                )
                if seed_name:
                    # try_get: one bad catalog artifact shouldn't crash the app.
                    default_svc = model_registry.try_get(seed_name)
                    if default_svc is not None:
                        model_registry.set_default(seed_name)
            if default_svc is not None:
                mv = activate_model_version(db, default_svc)
                logger.info("active model version: id=%s %s v%s", mv.id, mv.name, mv.version)
        else:
            # active_row points somewhere we can't currently resolve (e.g. an
            # archived runs/ snapshot that moved, or MODEL_RUN_DIR changed) —
            # don't guess which artifact to serve under that name; stay degraded.
            logger.warning(
                "active model version (name=%s run_dir=%s) is not resolvable via "
                "catalog_dir=%s or MODEL_RUN_DIR=%s; leaving unloaded",
                active_row.name, active_row.run_dir, catalog_dir, settings.model_run_dir,
            )

        if default_svc is None:
            # No servable artifact -> start DEGRADED (health reports it, /predict 503).
            logger.warning("starting without a model: no active DB row and nothing loadable")
        else:
            logger.info(
                "active model: %s v%s (run_dir=%s)",
                default_svc.name, default_svc.version, default_svc.run_dir,
            )
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
