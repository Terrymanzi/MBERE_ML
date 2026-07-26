"""Auth dependencies: resolve the current user from a bearer JWT, and gate
endpoints by role."""
from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..database.models import User, UserRole
from ..database.session import get_db
from .security import JWTError, decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

_CREDENTIALS_EXC = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    try:
        payload = decode_access_token(token)
        if payload.get("type") == "refresh":
            raise _CREDENTIALS_EXC
        subject = payload.get("sub")
        if subject is None:
            raise _CREDENTIALS_EXC
        user_id = int(subject)
    except (JWTError, ValueError, TypeError):
        raise _CREDENTIALS_EXC

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise _CREDENTIALS_EXC
    return user


def require_role(*roles: UserRole) -> Callable[[User], User]:
    """Dependency factory: 403s unless the current user's (live, DB-checked)
    role is one of ``roles``. Layers on top of ``get_current_user``, so a 401
    still takes priority for an unauthenticated/invalid request."""
    allowed = set(roles)

    def _check(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "insufficient permissions")
        return user

    return _check
