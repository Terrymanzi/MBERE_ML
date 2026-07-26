"""Auth request/response schemas."""
from __future__ import annotations

import datetime as dt
import re

from pydantic import BaseModel, ConfigDict, field_validator

from ..database.models import UserRole

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate_password_strength(v: str) -> str:
    if len(v) < 8:
        raise ValueError("password must be at least 8 characters")
    return v


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str | None = None
    # Self-registration can only ever create INSURER/FLEET_MANAGER accounts --
    # ADMIN is rejected below. Admins exist only via scripts/seed.py today.
    role: UserRole = UserRole.FLEET_MANAGER

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

    @field_validator("role")
    @classmethod
    def _no_self_service_admin(cls, v: UserRole) -> UserRole:
        if v is UserRole.ADMIN:
            raise ValueError("cannot self-register as ADMIN")
        return v


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str | None = None
    role: UserRole
    is_active: bool
    created_at: dt.datetime


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def _strong_enough(cls, v: str) -> str:
        return _validate_password_strength(v)
