"""add user role

Replaces the unused ``users.is_superuser`` boolean with a ``role`` column
(ADMIN / INSURER / FLEET_MANAGER), backfilled from the old flag so existing
admins stay admins. Stored as VARCHAR + CHECK (native_enum=False in the ORM)
rather than a Postgres-native ENUM so it stays portable across the SQLite
(dev) / Postgres (prod) split this app runs on, and so adding a future role
doesn't require an ``ALTER TYPE``.

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-26
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ROLE_TYPE = sa.String(length=20)


def upgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("role", ROLE_TYPE, nullable=True))

    op.execute(
        "UPDATE users SET role = CASE WHEN is_superuser THEN 'ADMIN' ELSE 'FLEET_MANAGER' END"
    )

    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column("role", existing_type=ROLE_TYPE, nullable=False)
        batch_op.create_check_constraint(
            "ck_users_role", "role IN ('ADMIN', 'INSURER', 'FLEET_MANAGER')"
        )
        batch_op.drop_column("is_superuser")


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(
            sa.Column("is_superuser", sa.Boolean(), nullable=True)
        )

    op.execute("UPDATE users SET is_superuser = (role = 'ADMIN')")

    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column("is_superuser", existing_type=sa.Boolean(), nullable=False)
        batch_op.drop_constraint("ck_users_role", type_="check")
        batch_op.drop_column("role")
