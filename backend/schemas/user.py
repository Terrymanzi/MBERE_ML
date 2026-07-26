"""Admin user-management + audit-log schemas."""
from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, ConfigDict, field_validator

from ..database.models import UserRole
from .auth import _EMAIL_RE, _validate_password_strength


class UserAdminCreate(BaseModel):
    """Unlike self-registration's ``UserCreate``, an admin may set any role."""

    email: str
    password: str
    full_name: str | None = None
    role: UserRole

    @field_validator("email")
    @classmethod
    def _valid_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not _EMAIL_RE.match(v):
            raise ValueError("invalid email address")
        return v

    @field_validator("password")
    @classmethod
    def _strong_enough(cls, v: str) -> str:
        return _validate_password_strength(v)


class UserUpdate(BaseModel):
    email: str | None = None
    full_name: str | None = None

    @field_validator("email")
    @classmethod
    def _valid_email(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip().lower()
        if not _EMAIL_RE.match(v):
            raise ValueError("invalid email address")
        return v


class RoleUpdateRequest(BaseModel):
    role: UserRole


class ActiveUpdateRequest(BaseModel):
    is_active: bool


class AdminResetPasswordRequest(BaseModel):
    new_password: str

    @field_validator("new_password")
    @classmethod
    def _strong_enough(cls, v: str) -> str:
        return _validate_password_strength(v)


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None
    action: str
    resource: str
    resource_id: int | None
    created_at: dt.datetime
