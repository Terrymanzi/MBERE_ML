"""Driver request/response schemas."""
from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, ConfigDict


class DriverCreate(BaseModel):
    license_number: str
    full_name: str
    date_of_birth: dt.date | None = None
    notes: str | None = None


class DriverUpdate(BaseModel):
    license_number: str | None = None
    full_name: str | None = None
    date_of_birth: dt.date | None = None
    notes: str | None = None


class DriverRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    license_number: str
    full_name: str
    date_of_birth: dt.date | None = None
    notes: str | None = None
    created_by_user_id: int | None = None
    created_at: dt.datetime
