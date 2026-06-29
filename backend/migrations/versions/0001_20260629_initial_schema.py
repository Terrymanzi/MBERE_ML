"""initial schema

Creates the full audit-trail schema mirroring backend/database/models.py:
users, drivers, model_versions, feature_records, risk_assessments, predictions.

Every Prediction / RiskAssessment carries a ``model_version_id`` FK so each
served inference is traceable back to the exact artifact that produced it.

Revision ID: 0001
Revises:
Create Date: 2026-06-29
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- users ------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # --- drivers ----------------------------------------------------------
    op.create_table(
        "drivers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("license_number", sa.String(length=64), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("notes", sa.String(length=512), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"], ["users.id"], name="fk_drivers_created_by_user_id_users"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_drivers"),
    )
    op.create_index("ix_drivers_license_number", "drivers", ["license_number"], unique=True)

    # --- model_versions (artifact registry) -------------------------------
    op.create_table(
        "model_versions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("version", sa.String(length=32), nullable=False),
        sa.Column("dataset_name", sa.String(length=64), nullable=False),
        sa.Column("kind", sa.String(length=16), nullable=False),
        sa.Column("target_classes", sa.JSON(), nullable=True),
        sa.Column("run_dir", sa.String(length=512), nullable=False),
        sa.Column("git_commit", sa.String(length=64), nullable=True),
        sa.Column("metrics", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_model_versions"),
        sa.UniqueConstraint("name", "version", "run_dir", name="uq_model_identity"),
    )

    # --- feature_records --------------------------------------------------
    op.create_table(
        "feature_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("driver_id", sa.Integer(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["driver_id"], ["drivers.id"], name="fk_feature_records_driver_id_drivers"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_feature_records"),
    )

    # --- risk_assessments -------------------------------------------------
    op.create_table(
        "risk_assessments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("driver_id", sa.Integer(), nullable=True),
        sa.Column("feature_record_id", sa.Integer(), nullable=False),
        sa.Column("model_version_id", sa.Integer(), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["driver_id"], ["drivers.id"], name="fk_risk_assessments_driver_id_drivers"
        ),
        sa.ForeignKeyConstraint(
            ["feature_record_id"],
            ["feature_records.id"],
            name="fk_risk_assessments_feature_record_id_feature_records",
        ),
        sa.ForeignKeyConstraint(
            ["model_version_id"],
            ["model_versions.id"],
            name="fk_risk_assessments_model_version_id_model_versions",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
            name="fk_risk_assessments_created_by_user_id_users",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_risk_assessments"),
    )
    op.create_index(
        "ix_risk_assessments_driver_id", "risk_assessments", ["driver_id"], unique=False
    )

    # --- predictions (FK'd to model_versions for auditability) ------------
    op.create_table(
        "predictions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("risk_assessment_id", sa.Integer(), nullable=False),
        sa.Column("model_version_id", sa.Integer(), nullable=False),
        sa.Column("predicted_class", sa.String(length=64), nullable=False),
        sa.Column("risk_band", sa.String(length=16), nullable=False),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("probabilities", sa.JSON(), nullable=False),
        sa.Column("explanation", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["risk_assessment_id"],
            ["risk_assessments.id"],
            name="fk_predictions_risk_assessment_id_risk_assessments",
        ),
        sa.ForeignKeyConstraint(
            ["model_version_id"],
            ["model_versions.id"],
            name="fk_predictions_model_version_id_model_versions",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_predictions"),
        sa.UniqueConstraint("risk_assessment_id", name="uq_predictions_risk_assessment_id"),
    )


def downgrade() -> None:
    # Reverse dependency order so FKs never block a drop.
    op.drop_table("predictions")
    op.drop_index("ix_risk_assessments_driver_id", table_name="risk_assessments")
    op.drop_table("risk_assessments")
    op.drop_table("feature_records")
    op.drop_table("model_versions")
    op.drop_index("ix_drivers_license_number", table_name="drivers")
    op.drop_table("drivers")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
