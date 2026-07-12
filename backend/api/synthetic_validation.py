"""POST /synthetic-validation — model performance simulation on the Rwandan
contextualised synthetic dataset.

This endpoint is for MODEL VALIDATION AND SIMULATION ONLY.
Results are NEVER used as ground-truth performance metrics.
The Addis held-out test set remains the sole source of performance metrics.

Accepts an optional `fabricate_csv` path (defaults to the bundled synthetic
CSV). Runs load_and_validate -> batch inference -> returns mean P(Fatal) and
P(Serious) grouped by synthetic_severity_label with monotonicity flags.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict

from ..app.config import PROJECT_ROOT, get_settings
from ..auth.deps import get_current_user
from ..database.models import User
from ..services.model_registry import model_registry

router = APIRouter(tags=["synthetic-validation"])

_DEFAULT_CSV = PROJECT_ROOT / "data" / "external" / "synthetic" / "rwanda_driver_risk_profiles_synthetic.csv"


class SyntheticValidationRequest(BaseModel):
    fabricate_csv: str | None = None  # defaults to bundled CSV if omitted


class SyntheticValidationResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    note: str
    model_name: str
    model_version: str
    n_rows: int
    labels_evaluated: list[str]
    mean_p_fatal: dict[str, float]
    mean_p_serious: dict[str, float]
    monotonic_fatal: bool
    monotonic_serious: bool


@router.post("/synthetic-validation", response_model=SyntheticValidationResponse)
def synthetic_validation(
    payload: SyntheticValidationRequest | None = None,
    user: User = Depends(get_current_user),
) -> SyntheticValidationResponse:
    """Run a contextual sanity check of the latest model artifact against the
    synthetic Rwandan driver-risk dataset.

    This is MODEL PERFORMANCE SIMULATION only — results are not persisted and
    never merged into metrics.json.
    """
    svc = model_registry.default()
    if svc is None or not svc.loaded:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "no model loaded")

    csv_path = Path(payload.fabricate_csv) if (payload and payload.fabricate_csv) else _DEFAULT_CSV
    if not csv_path.is_absolute():
        csv_path = PROJECT_ROOT / csv_path
    if not csv_path.exists():
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Fabricate CSV not found: {csv_path}",
        )

    contract_path = svc.run_dir / "feature_contract.json"
    model_path = svc.run_dir / f"{svc.name}.pkl"

    try:
        # Import here to keep the backend independent of the ml package at module load.
        from ml.synthetic.generate import load_and_validate, sanity_check

        df = load_and_validate(csv_path, contract_path)
        result = sanity_check(df, model_path, encoder_path=None, contract_path=contract_path)
    except ValueError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc))
    except Exception as exc:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Sanity check failed: {exc}")

    return SyntheticValidationResponse(
        note=result["note"],
        model_name=svc.name,
        model_version=svc.version,
        n_rows=result["n_rows"],
        labels_evaluated=result["labels_evaluated"],
        mean_p_fatal=result["mean_p_fatal"],
        mean_p_serious=result["mean_p_serious"],
        monotonic_fatal=result["monotonic_fatal"],
        monotonic_serious=result["monotonic_serious"],
    )
