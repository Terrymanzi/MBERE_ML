"""Per-owner data isolation: a driver (and everything tied to it -- feature
records, risk assessments, predictions) is visible only to the user who
created it, plus ADMIN. Returns 404 rather than 403 for a driver that exists
but isn't owned by the caller, so a non-owner can't distinguish "doesn't
exist" from "exists but isn't yours"."""
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..database.models import Driver, User, UserRole


def get_owned_driver(db: Session, driver_id: int, user: User) -> Driver:
    driver = db.get(Driver, driver_id)
    if driver is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "driver not found")
    if user.role != UserRole.ADMIN and driver.created_by_user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "driver not found")
    return driver
