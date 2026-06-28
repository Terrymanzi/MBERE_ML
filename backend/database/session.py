"""Engine / session wiring.

DATABASE_URL drives the backend; PostgreSQL in prod, SQLite for local/dev/test.
Relative SQLite paths are resolved against the repo root so the DB lands in a
predictable place regardless of the process working directory.
"""
from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ..app.config import PROJECT_ROOT, get_settings
from .base import Base


def _resolve_url(url: str) -> str:
    """Make relative SQLite paths absolute (against the repo root)."""
    prefix = "sqlite:///"
    if url.startswith(prefix) and not url.startswith("sqlite:////"):
        raw = url[len(prefix):]
        path = (PROJECT_ROOT / raw).resolve()
        return prefix + path.as_posix()
    return url


_settings = get_settings()
_url = _resolve_url(_settings.database_url)
_connect_args = {"check_same_thread": False} if _url.startswith("sqlite") else {}

engine = create_engine(_url, future=True, pool_pre_ping=True, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Iterator[Session]:
    """FastAPI dependency: a request-scoped session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create tables. (Alembic owns migrations in prod; this bootstraps dev/test.)"""
    from . import models  # noqa: F401  -- register mappers before create_all

    Base.metadata.create_all(bind=engine)
