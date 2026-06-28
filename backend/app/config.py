"""Application settings, loaded from environment / .env (never hardcode secrets).

The backend is an INFERENCE service: it selects a versioned ML run artifact
(produced by the `ml/` package) via ``model_run_dir`` / ``model_name`` and serves
it. No training configuration lives here.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/config.py -> parents[2] == repo root
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # protected_namespaces=() so ``model_*`` fields don't collide with pydantic's
    # reserved ``model_`` namespace.
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", protected_namespaces=()
    )

    app_name: str = "mbere-ml backend"
    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # --- auth (override SECRET_KEY in .env for any non-local use) ---
    secret_key: str = "dev-insecure-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # --- database (prod: PostgreSQL; dev/test default: SQLite) ---
    database_url: str = "sqlite:///./mbere_backend.db"

    # --- CORS (comma-separated origins) ---
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # --- model artifact selection ---
    # If model_run_dir is unset, the latest run under artifacts_root that contains
    # `{model_name}.pkl` + feature_contract.json is auto-selected.
    artifacts_root: str = "ml/artifacts/runs"
    model_run_dir: str | None = None
    model_name: str = "random_forest"

    # --- risk banding on the [0,1] risk score (positive-class / expected severity) ---
    risk_band_low_max: float = 0.34
    risk_band_medium_max: float = 0.67
    explain_top_k: int = 8

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
