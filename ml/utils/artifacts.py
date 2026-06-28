"""Versioned-artifact helpers: persistence, metadata, git/timestamp provenance."""
from __future__ import annotations

import datetime as dt
import json
import subprocess
from pathlib import Path

import joblib

from .config import DatasetConfig
from .paths import PROJECT_ROOT


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def save_model(model, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)
    return path


def load_model(path: str | Path):
    return joblib.load(Path(path))


def write_json(obj, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    return path


def report_dir(config: DatasetConfig, model_name: str) -> Path:
    out = Path(config.paths.artifacts_dir) / "reports" / model_name
    out.mkdir(parents=True, exist_ok=True)
    return out


def json_safe_params(params: dict) -> dict:
    """Keep only JSON-serializable param values (drop estimator objects, etc.)."""
    safe = {}
    for key, value in params.items():
        try:
            json.dumps(value)
            safe[key] = value
        except (TypeError, ValueError):
            safe[key] = repr(value)
    return safe


def build_meta(
    model_name: str,
    model_version: str,
    config: DatasetConfig,
    n_rows: int,
    feature_list: list[str],
    metrics: dict,
    params: dict,
) -> dict:
    """Sidecar metadata for a saved model (versioned-artifact contract)."""
    return {
        "model": model_name,
        "model_version": model_version,
        "created_utc": utc_now_iso(),
        "git_commit": git_commit(),
        "random_state": config.random_state,
        "dataset": {
            "name": config.name,
            "kind": config.kind,
            "rows": int(n_rows),
            "target": config.target.column,
            "classes": list(config.target.classes),
        },
        "features": list(feature_list),
        "cv": {
            "scheme": "StratifiedKFold",
            "k_folds": config.split.k_folds,
            "shuffle": True,
            "random_state": config.split.random_state,
        },
        "params": json_safe_params(params),
        "metrics_cv": metrics,
    }
