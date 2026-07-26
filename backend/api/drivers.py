"""Driver CRUD + per-driver risk history."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from ..auth.deps import get_current_user
from ..database.models import Driver, RiskAssessment, User, UserRole
from ..database.session import get_db
from ..schemas.driver import DriverCreate, DriverRead, DriverUpdate
from ..schemas.prediction import RiskAssessmentRead
from ..services.ownership import get_owned_driver

router = APIRouter(tags=["drivers"])


@router.post("/drivers", response_model=DriverRead, status_code=status.HTTP_201_CREATED)
def create_driver(
    payload: DriverCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Driver:
    exists = db.scalar(select(Driver).where(Driver.license_number == payload.license_number))
    if exists is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "license_number already exists")
    driver = Driver(
        license_number=payload.license_number,
        full_name=payload.full_name,
        date_of_birth=payload.date_of_birth,
        notes=payload.notes,
        created_by_user_id=user.id,
    )
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver


@router.get("/drivers", response_model=list[DriverRead])
def list_drivers(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    q: str | None = Query(None, description="Case-insensitive search over full_name / license_number"),
) -> list[Driver]:
    stmt = select(Driver)
    if user.role != UserRole.ADMIN:
        stmt = stmt.where(Driver.created_by_user_id == user.id)
    if q and q.strip():
        pattern = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(Driver.full_name.ilike(pattern), Driver.license_number.ilike(pattern))
        )
    return list(
        db.scalars(
            stmt.order_by(Driver.created_at.desc()).limit(limit).offset(offset)
        ).all()
    )


@router.get("/drivers/{driver_id}", response_model=DriverRead)
def get_driver(
    driver_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Driver:
    return get_owned_driver(db, driver_id, user)


@router.put("/drivers/{driver_id}", response_model=DriverRead)
def update_driver(
    driver_id: int,
    payload: DriverUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Driver:
    driver = get_owned_driver(db, driver_id, user)
    if payload.license_number is not None and payload.license_number != driver.license_number:
        conflict = db.scalar(select(Driver).where(Driver.license_number == payload.license_number))
        if conflict is not None:
            raise HTTPException(status.HTTP_409_CONFLICT, "license_number already exists")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(driver, field, value)
    db.commit()
    db.refresh(driver)
    return driver


@router.delete("/drivers/{driver_id}")
def delete_driver(
    driver_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Response:
    driver = get_owned_driver(db, driver_id, user)
    db.delete(driver)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/risk/{driver_id}", response_model=list[RiskAssessmentRead])
def driver_risk_history(
    driver_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[RiskAssessment]:
    get_owned_driver(db, driver_id, user)
    return list(
        db.scalars(
            select(RiskAssessment)
            .where(RiskAssessment.driver_id == driver_id)
            .order_by(RiskAssessment.created_at.desc())
            .options(selectinload(RiskAssessment.prediction))
        ).all()
    )
