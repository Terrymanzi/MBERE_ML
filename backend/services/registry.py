"""Sync loaded artifacts into the ModelVersion registry table."""
from __future__ import annotations

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from ..database.models import ModelVersion
from .model_service import ModelService


def ensure_model_version_row(db: Session, service: ModelService) -> ModelVersion:
    """Upsert the ModelVersion row for `service`'s identity WITHOUT touching any
    is_active flags. Used for both the default model and one-off /predict
    overrides, so an override never redefines the org-wide active model."""
    identity = service.identity()
    row = db.scalar(
        select(ModelVersion).where(
            ModelVersion.name == identity["name"],
            ModelVersion.version == identity["version"],
            ModelVersion.run_dir == identity["run_dir"],
        )
    )
    if row is None:
        row = ModelVersion(**identity, is_active=False)
        db.add(row)
    else:
        row.dataset_name = identity["dataset_name"]
        row.kind = identity["kind"]
        row.target_classes = identity["target_classes"]
        row.git_commit = identity["git_commit"]
        row.metrics = identity["metrics"]
    db.commit()
    db.refresh(row)
    return row


def activate_model_version(db: Session, service: ModelService) -> ModelVersion:
    """Upsert + mark this identity as the ONE globally active ModelVersion.
    Idempotent across restarts."""
    identity = service.identity()
    row = db.scalar(
        select(ModelVersion).where(
            ModelVersion.name == identity["name"],
            ModelVersion.version == identity["version"],
            ModelVersion.run_dir == identity["run_dir"],
        )
    )
    # only one active version at a time
    db.execute(update(ModelVersion).values(is_active=False))
    if row is None:
        row = ModelVersion(**identity, is_active=True)
        db.add(row)
    else:
        row.dataset_name = identity["dataset_name"]
        row.kind = identity["kind"]
        row.target_classes = identity["target_classes"]
        row.git_commit = identity["git_commit"]
        row.metrics = identity["metrics"]
        row.is_active = True
    db.commit()
    db.refresh(row)
    return row


def get_active_model_version(db: Session) -> ModelVersion | None:
    """Pure DB lookup for the currently active ModelVersion, if any."""
    return db.scalar(select(ModelVersion).where(ModelVersion.is_active.is_(True)))
