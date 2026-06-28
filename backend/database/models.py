"""SQLAlchemy ORM models (mirrors the proposal ERD).

    User  1───*  Driver
    Driver 1───*  FeatureRecord
    Driver 1───*  RiskAssessment 1───1 FeatureRecord
                  RiskAssessment 1───1 Prediction
    ModelVersion 1───*  RiskAssessment / Prediction   (audit trail)

Every Prediction carries an explicit ``model_version_id`` FK so each served
inference is auditable back to the exact artifact that produced it.
"""
from __future__ import annotations

import datetime as dt
from typing import Any, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    JSON,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


def _utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    drivers: Mapped[list["Driver"]] = relationship(back_populates="created_by")
    assessments: Mapped[list["RiskAssessment"]] = relationship(back_populates="created_by")


class Driver(Base):
    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(primary_key=True)
    license_number: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    date_of_birth: Mapped[Optional[dt.date]] = mapped_column()
    notes: Mapped[Optional[str]] = mapped_column(String(512))
    created_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    created_by: Mapped[Optional["User"]] = relationship(back_populates="drivers")
    feature_records: Mapped[list["FeatureRecord"]] = relationship(
        back_populates="driver", cascade="all, delete-orphan"
    )
    assessments: Mapped[list["RiskAssessment"]] = relationship(
        back_populates="driver", cascade="all, delete-orphan"
    )


class ModelVersion(Base):
    """Registry of served artifacts. One row per (name, version, run_dir)."""

    __tablename__ = "model_versions"
    __table_args__ = (UniqueConstraint("name", "version", "run_dir", name="uq_model_identity"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)          # e.g. random_forest
    version: Mapped[str] = mapped_column(String(32), nullable=False)        # e.g. 0.1.0
    dataset_name: Mapped[str] = mapped_column(String(64), nullable=False)
    kind: Mapped[str] = mapped_column(String(16), nullable=False)           # binary | multiclass
    target_classes: Mapped[Any] = mapped_column(JSON, default=list)
    run_dir: Mapped[str] = mapped_column(String(512), nullable=False)
    git_commit: Mapped[Optional[str]] = mapped_column(String(64))
    metrics: Mapped[Any] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    predictions: Mapped[list["Prediction"]] = relationship(back_populates="model_version")


class FeatureRecord(Base):
    """Snapshot of the raw feature payload submitted for an assessment."""

    __tablename__ = "feature_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    driver_id: Mapped[Optional[int]] = mapped_column(ForeignKey("drivers.id"))
    payload: Mapped[Any] = mapped_column(JSON, nullable=False)
    source: Mapped[str] = mapped_column(String(32), default="api")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    driver: Mapped[Optional["Driver"]] = relationship(back_populates="feature_records")
    assessment: Mapped[Optional["RiskAssessment"]] = relationship(
        back_populates="feature_record", uselist=False
    )


class RiskAssessment(Base):
    """A single assessment event: links driver + features + model + result."""

    __tablename__ = "risk_assessments"

    id: Mapped[int] = mapped_column(primary_key=True)
    driver_id: Mapped[Optional[int]] = mapped_column(ForeignKey("drivers.id"), index=True)
    feature_record_id: Mapped[int] = mapped_column(ForeignKey("feature_records.id"), nullable=False)
    model_version_id: Mapped[int] = mapped_column(ForeignKey("model_versions.id"), nullable=False)
    created_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(16), default="completed")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    driver: Mapped[Optional["Driver"]] = relationship(back_populates="assessments")
    feature_record: Mapped["FeatureRecord"] = relationship(back_populates="assessment")
    model_version: Mapped["ModelVersion"] = relationship()
    created_by: Mapped[Optional["User"]] = relationship(back_populates="assessments")
    prediction: Mapped[Optional["Prediction"]] = relationship(
        back_populates="risk_assessment", uselist=False, cascade="all, delete-orphan"
    )


class Prediction(Base):
    """Model output for an assessment, FK'd to the model version for auditability."""

    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True)
    risk_assessment_id: Mapped[int] = mapped_column(
        ForeignKey("risk_assessments.id"), unique=True, nullable=False
    )
    model_version_id: Mapped[int] = mapped_column(ForeignKey("model_versions.id"), nullable=False)
    predicted_class: Mapped[str] = mapped_column(String(64), nullable=False)
    risk_band: Mapped[str] = mapped_column(String(16), nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    probabilities: Mapped[Any] = mapped_column(JSON, nullable=False)
    explanation: Mapped[Any] = mapped_column(JSON, default=dict)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    risk_assessment: Mapped["RiskAssessment"] = relationship(back_populates="prediction")
    model_version: Mapped["ModelVersion"] = relationship(back_populates="predictions")
