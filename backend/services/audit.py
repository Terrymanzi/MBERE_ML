"""Accountability trail: one row per admin action."""
from __future__ import annotations

from sqlalchemy.orm import Session

from ..database.models import AuditLog, User


def log_action(
    db: Session, user: User, action: str, resource: str, resource_id: int | None = None
) -> AuditLog:
    entry = AuditLog(user_id=user.id, action=action, resource=resource, resource_id=resource_id)
    db.add(entry)
    db.commit()
    return entry
