"""Seed the backend database with demo data.

Inserts (idempotently):
  * one demo fleet-admin user,
  * a handful of drivers owned by that admin,
  * one ModelVersion row built from the CURRENT artifact's meta.json (via the
    same ModelService the API uses), so seeded predictions are traceable to the
    exact served model.

Run AFTER the schema exists:
    docker compose up -d db
    alembic upgrade head
    python scripts/seed.py

No secrets are hardcoded. The admin credentials come from the environment
(SEED_ADMIN_EMAIL / SEED_ADMIN_PASSWORD); a clearly-flagged dev default is used
only when they are unset, and the password used is printed so you can log in.
"""
from __future__ import annotations

import datetime as dt
import os
import sys
from pathlib import Path

# Make `backend` importable when run as `python scripts/seed.py` from the root.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import select  # noqa: E402
from sqlalchemy.exc import OperationalError, ProgrammingError  # noqa: E402

from backend.auth.security import hash_password  # noqa: E402
from backend.database.models import Driver, User  # noqa: E402
from backend.database.session import SessionLocal, engine  # noqa: E402
from backend.services.model_service import ArtifactNotFoundError, ModelService  # noqa: E402
from backend.services.registry import ensure_model_version  # noqa: E402

DEMO_DRIVERS = [
    # license_number, full_name, date_of_birth, notes
    ("RW-DRV-0001", "Aline Uwase", dt.date(1990, 3, 14), "City delivery van; 8y experience."),
    ("RW-DRV-0002", "Jean-Paul Niyonzima", dt.date(1985, 11, 2), "Long-haul lorry driver."),
    ("RW-DRV-0003", "Claudine Mukamana", dt.date(1996, 7, 21), "Motorcycle courier (moto-taxi)."),
    ("RW-DRV-0004", "Eric Habimana", dt.date(2001, 1, 9), "Newly licensed; under probation."),
    ("RW-DRV-0005", "Diane Ingabire", dt.date(1979, 5, 30), "Fleet supervisor; minibus."),
]


def _admin_credentials() -> tuple[str, str, bool]:
    """(email, password, used_default) from the environment, with a dev default."""
    email = os.environ.get("SEED_ADMIN_EMAIL", "admin@mbere.local").strip().lower()
    password = os.environ.get("SEED_ADMIN_PASSWORD")
    if password:
        return email, password, False
    return email, "ChangeMe!2026", True


def seed_admin(db) -> User:
    email, password, used_default = _admin_credentials()
    user = db.scalar(select(User).where(User.email == email))
    if user is not None:
        print(f"  user      : {email} (already present, id={user.id})")
        return user
    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name="Fleet Admin",
        is_active=True,
        is_superuser=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    flag = "  [dev default -- set SEED_ADMIN_PASSWORD to override]" if used_default else ""
    print(f"  user      : {email} (created, id={user.id})")
    print(f"  password  : {password}{flag}")
    return user


def seed_drivers(db, owner: User) -> int:
    created = 0
    for license_number, full_name, dob, notes in DEMO_DRIVERS:
        existing = db.scalar(select(Driver).where(Driver.license_number == license_number))
        if existing is not None:
            continue
        db.add(
            Driver(
                license_number=license_number,
                full_name=full_name,
                date_of_birth=dob,
                notes=notes,
                created_by_user_id=owner.id,
            )
        )
        created += 1
    db.commit()
    n = len(db.scalars(select(Driver)).all())
    print(f"  drivers   : +{created} created ({n} total)")
    return created


def seed_model_version(db) -> None:
    """Register the currently-configured artifact from its meta.json."""
    service = ModelService()
    try:
        service.load()
    except ArtifactNotFoundError as exc:
        print(f"  model     : SKIPPED -- no servable artifact found ({exc}).")
        print("              Predictions need a ModelVersion; point MODEL_RUN_DIR at a run "
              "and re-run.")
        return
    row = ensure_model_version(db, service)
    print(
        f"  model     : {row.name} v{row.version} "
        f"[{row.dataset_name}/{row.kind}] active (id={row.id})\n"
        f"              run_dir={row.run_dir}"
    )


def main() -> int:
    print(f"Seeding {engine.url.render_as_string(hide_password=True)}")
    db = SessionLocal()
    try:
        admin = seed_admin(db)
        seed_drivers(db, admin)
        seed_model_version(db)
    except (OperationalError, ProgrammingError) as exc:
        db.rollback()
        print("\nERROR: the schema does not look ready. Run migrations first:")
        print("    alembic upgrade head")
        print(f"(underlying error: {exc.__class__.__name__})")
        return 1
    finally:
        db.close()
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
