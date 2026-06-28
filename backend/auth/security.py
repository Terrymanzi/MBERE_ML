"""Password hashing (passlib/bcrypt) and JWT issuance/decoding (python-jose)."""
from __future__ import annotations

import datetime as dt

from jose import JWTError, jwt
from passlib.context import CryptContext

from ..app.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: str | int, expires_minutes: int | None = None) -> str:
    settings = get_settings()
    minutes = expires_minutes if expires_minutes is not None else settings.access_token_expire_minutes
    now = dt.datetime.now(dt.timezone.utc)
    payload = {
        "sub": str(subject),
        "iat": now,
        "exp": now + dt.timedelta(minutes=minutes),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    """Decode/verify a JWT. Raises ``jose.JWTError`` on any problem."""
    settings = get_settings()
    return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])


__all__ = [
    "JWTError",
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
]
