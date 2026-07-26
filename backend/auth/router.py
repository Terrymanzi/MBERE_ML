"""Auth endpoints: register, token (login), refresh, logout, change-password,
and current-user."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database.models import User
from ..database.session import get_db
from ..schemas.auth import ChangePasswordRequest, RefreshRequest, Token, UserCreate, UserRead
from .deps import get_current_user
from .security import (
    JWTError,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])

_REFRESH_CREDENTIALS_EXC = HTTPException(
    status.HTTP_401_UNAUTHORIZED, "invalid or expired refresh token"
)


def _issue_token_pair(user: User) -> Token:
    return Token(
        access_token=create_access_token(user.id, role=user.role.value),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    exists = db.scalar(select(User).where(User.email == payload.email))
    if exists is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "email already registered")
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/token", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> Token:
    email = form.username.strip().lower()
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _issue_token_pair(user)


@router.post("/refresh", response_model=Token)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> Token:
    try:
        decoded = decode_access_token(payload.refresh_token)
        if decoded.get("type") != "refresh":
            raise _REFRESH_CREDENTIALS_EXC
        user_id = int(decoded["sub"])
    except (JWTError, ValueError, TypeError, KeyError):
        raise _REFRESH_CREDENTIALS_EXC

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise _REFRESH_CREDENTIALS_EXC
    return _issue_token_pair(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current: User = Depends(get_current_user)) -> Response:
    """No-op: tokens are stateless JWTs with no server-side session to revoke
    yet (see the ``user_sessions`` table in the later roadmap). Exposed now so
    the frontend has a real endpoint to call, and revocation is a one-line
    addition here once that table exists."""
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    payload: ChangePasswordRequest,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    if not verify_password(payload.current_password, current.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "current password is incorrect")
    current.hashed_password = hash_password(payload.new_password)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserRead)
def me(current: User = Depends(get_current_user)) -> User:
    return current
