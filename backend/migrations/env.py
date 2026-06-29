"""Alembic environment.

The target metadata is the backend's SQLAlchemy ``Base.metadata`` (the exact
models served by the API), and the database URL is taken from the backend
settings (which read ``DATABASE_URL`` from ``.env``). Nothing here hardcodes a
connection string or secret -- the same migrations run against SQLite (dev) or
PostgreSQL (prod) based purely on the environment.
"""
from __future__ import annotations

from logging.config import fileConfig

from alembic import context

# Backend wiring: the already-configured engine (URL resolved from .env) and the
# declarative Base. Importing the models module registers every table on the
# metadata so autogenerate / create-all see the full schema.
from backend.database import models  # noqa: F401  (populates Base.metadata)
from backend.database.base import Base
from backend.database.session import engine

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Emit SQL to stdout without a live DB connection (`alembic ... --sql`)."""
    context.configure(
        url=str(engine.url),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against the live engine configured from .env."""
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            # batch mode lets SQLite (dev) handle ALTERs in future migrations;
            # it's a no-op for PostgreSQL.
            render_as_batch=connection.dialect.name == "sqlite",
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
