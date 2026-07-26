"""Admin-only user management + audit log (all endpoints require ADMIN)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..auth.deps import require_role
from ..auth.security import hash_password
from ..database.models import AuditLog, User, UserRole
from ..database.session import get_db
from ..schemas.auth import UserRead
from ..schemas.user import (
    AdminResetPasswordRequest,
    ActiveUpdateRequest,
    AuditLogRead,
    RoleUpdateRequest,
    UserAdminCreate,
    UserUpdate,
)
from ..services.audit import log_action

router = APIRouter(tags=["users"])


@router.get("/users", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(UserRole.ADMIN)),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    q: str | None = Query(None, description="Case-insensitive search over email / full_name"),
) -> list[User]:
    stmt = select(User)
    if q and q.strip():
        pattern = f"%{q.strip()}%"
        stmt = stmt.where(or_(User.email.ilike(pattern), User.full_name.ilike(pattern)))
    return list(
        db.scalars(stmt.order_by(User.created_at.desc()).limit(limit).offset(offset)).all()
    )


@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserAdminCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(UserRole.ADMIN)),
) -> User:
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
    log_action(db, admin, "create", "user", user.id)
    return user


@router.put("/users/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(UserRole.ADMIN)),
) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "user not found")
    if payload.email is not None and payload.email != user.email:
        conflict = db.scalar(select(User).where(User.email == payload.email))
        if conflict is not None:
            raise HTTPException(status.HTTP_409_CONFLICT, "email already registered")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    log_action(db, admin, "update", "user", user.id)
    return user


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(UserRole.ADMIN)),
) -> Response:
    if user_id == admin.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "cannot delete your own account")
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "user not found")
    db.delete(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "cannot delete a user with existing drivers, assessments, or audit history",
        )
    log_action(db, admin, "delete", "user", user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/users/{user_id}/role", response_model=UserRead)
def update_user_role(
    user_id: int,
    payload: RoleUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(UserRole.ADMIN)),
) -> User:
    if user_id == admin.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "cannot change your own role")
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "user not found")
    user.role = payload.role
    db.commit()
    db.refresh(user)
    log_action(db, admin, "role_change", "user", user.id)
    return user


@router.patch("/users/{user_id}/active", response_model=UserRead)
def update_user_active(
    user_id: int,
    payload: ActiveUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(UserRole.ADMIN)),
) -> User:
    if user_id == admin.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "cannot change your own active status")
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "user not found")
    user.is_active = payload.is_active
    db.commit()
    db.refresh(user)
    log_action(db, admin, "active_change", "user", user.id)
    return user


@router.post("/users/{user_id}/reset-password", status_code=status.HTTP_204_NO_CONTENT)
def reset_user_password(
    user_id: int,
    payload: AdminResetPasswordRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(UserRole.ADMIN)),
) -> Response:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "user not found")
    user.hashed_password = hash_password(payload.new_password)
    db.commit()
    log_action(db, admin, "password_reset", "user", user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/audit-logs", response_model=list[AuditLogRead])
def list_audit_logs(
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(UserRole.ADMIN)),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list[AuditLog]:
    return list(
        db.scalars(
            select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
        ).all()
    )
