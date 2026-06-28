"""Driver CRUD + per-driver risk history."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..auth.deps import get_current_user
from ..database.models import Driver, RiskAssessment, User
from ..database.session import get_db
from ..schemas.driver import DriverCreate, DriverRead
from ..schemas.prediction import RiskAssessmentRead

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
) -> list[Driver]:
    return list(
        db.scalars(
            select(Driver).order_by(Driver.created_at.desc()).limit(limit).offset(offset)
        ).all()
    )


@router.get("/risk/{driver_id}", response_model=list[RiskAssessmentRead])
def driver_risk_history(
    driver_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[RiskAssessment]:
    driver = db.get(Driver, driver_id)
    if driver is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "driver not found")
    return list(
        db.scalars(
            select(RiskAssessment)
            .where(RiskAssessment.driver_id == driver_id)
            .order_by(RiskAssessment.created_at.desc())
            .options(selectinload(RiskAssessment.prediction))
        ).all()
    )
