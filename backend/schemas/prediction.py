"""Prediction / model / health schemas.

The /predict request accepts a free-form ``features`` map; it is validated at
request time against the loaded model's feature contract (names, kinds, types),
so the accepted shape always matches the served artifact exactly.
"""
from __future__ import annotations

import datetime as dt
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ModelInfo(BaseModel):
    name: str
    version: str
    dataset: str
    kind: str
    classes: list[str]


class ContractFeature(BaseModel):
    name: str
    kind: str               # categorical | numeric
    encoding: str           # ordinal | onehot | numeric
    dtype: str
    categories: list[Any] | None = None


class FeatureContractResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model: ModelInfo
    input_features: list[ContractFeature]


class ModelPerformance(BaseModel):
    n_samples: int
    accuracy: float
    f1_macro: float
    recall_macro: float
    precision_macro: float
    roc_auc_ovr_macro: float


class ModelCatalogEntry(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    name: str
    version: str
    dataset_name: str
    kind: str
    target_classes: list[str]
    git_commit: str | None = None
    created_utc: str | None = None
    metrics_cv: dict[str, Any]
    metrics_test: ModelPerformance | None = None
    is_active: bool
    model_version_id: int | None = None


class ModelCatalogResponse(BaseModel):
    catalog_dir: str
    models: list[ModelCatalogEntry]


class PredictRequest(BaseModel):
    driver_id: int | None = Field(
        default=None, description="Optional driver to attach this assessment to."
    )
    model_name: str | None = Field(
        default=None,
        description=(
            "Optional catalog model name (see GET /models/catalog) to use for "
            "this prediction only. Omit to use the current active model."
        ),
    )
    features: dict[str, Any] = Field(
        ..., description="Raw feature map; keys/types must match the model contract."
    )


class FeatureContribution(BaseModel):
    feature: str
    value: Any | None = None
    contribution: float
    abs_contribution: float


class Explanation(BaseModel):
    method: str                          # shap | linear | none
    base_value: float | None = None
    top_features: list[FeatureContribution]


class PredictResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    risk_assessment_id: int
    prediction_id: int
    driver_id: int | None = None
    model: ModelInfo
    predicted_class: str
    risk_band: str                       # Low | Medium | High
    risk_score: float                    # [0,1]
    probabilities: dict[str, float]
    explanation: Explanation
    created_at: dt.datetime


class PredictionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: int
    predicted_class: str
    risk_band: str
    risk_score: float
    probabilities: dict[str, float]
    explanation: dict[str, Any]
    model_version_id: int
    created_at: dt.datetime


class RiskAssessmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    driver_id: int | None = None
    status: str
    created_at: dt.datetime
    prediction: PredictionRead | None = None


class ModelVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    version: str
    dataset_name: str
    kind: str
    target_classes: list[str]
    git_commit: str | None = None
    metrics: dict[str, Any]
    is_active: bool
    created_at: dt.datetime


class HealthResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    status: str
    db_ok: bool
    model_loaded: bool
    model: ModelInfo | None = None
    n_input_features: int | None = None
