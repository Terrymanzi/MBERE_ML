"""Backend test fixtures.

We build a tiny, self-contained model artifact (a real sklearn Pipeline +
feature_contract.json + meta.json) in a temp dir and point the app at it via
env vars BEFORE importing the app. This keeps backend tests independent of the
gitignored `ml/artifacts/runs/` directory, while still exercising the real
load -> validate -> predict -> SHAP path.

Fitting a model HERE (in a test fixture) is fine — the constraint is that the
backend *application* code never trains; it only deserializes.
"""
from __future__ import annotations

import json
import os
import tempfile
import uuid
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest

CLASSES = ["Slight Injury", "Serious Injury", "Fatal Injury"]

# --- temp artifact + DB, wired via env before any backend import -------------
_TMP = Path(tempfile.mkdtemp(prefix="mbere_backend_test_"))
_RUN = _TMP / "run"
_RUN.mkdir(parents=True, exist_ok=True)
_DB = _TMP / "test.db"

os.environ["DATABASE_URL"] = f"sqlite:///{_DB.as_posix()}"
os.environ["ARTIFACTS_ROOT"] = str(_TMP)
os.environ["MODEL_RUN_DIR"] = str(_RUN)
os.environ["MODEL_NAME"] = "random_forest"
os.environ["SECRET_KEY"] = "test-secret-key-not-for-prod"


def _build_artifact(run_dir: Path, *, model_name: str = "random_forest",
                    feature_names_override: list[str] | None = None) -> None:
    """Fit a tiny 3-class Pipeline and write the versioned-artifact trio."""
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder

    rng = np.random.default_rng(42)
    n = 240
    vehicle = rng.choice(["Automobile", "Motorcycle", "Lorry"], size=n)
    age = rng.integers(18, 70, size=n).astype(float)
    experience = rng.integers(0, 40, size=n).astype(float)
    # Interpretable signal: motorcycle / young / inexperienced -> higher severity.
    risk = (
        1.6 * (vehicle == "Motorcycle")
        + 1.0 * (age < 25)
        + 1.0 * (experience < 3)
        + rng.normal(0, 0.5, n)
    )
    cuts = np.quantile(risk, [0.34, 0.67])
    y = np.digitize(risk, cuts)  # -> 0,1,2 (balanced terciles)

    X = pd.DataFrame(
        {"vehicle_type": vehicle, "driver_age": age, "driver_experience": experience}
    )
    encoder = ColumnTransformer([
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False), ["vehicle_type"]),
        ("numeric", "passthrough", ["driver_age", "driver_experience"]),
    ])
    pipe = Pipeline([
        ("encoder", encoder),
        ("classifier", RandomForestClassifier(n_estimators=40, random_state=0)),
    ])
    pipe.fit(X, y)

    joblib.dump(pipe, run_dir / f"{model_name}.pkl")

    onehot_cats = (
        pipe.named_steps["encoder"].named_transformers_["onehot"].categories_[0].tolist()
    )
    names = feature_names_override or ["vehicle_type", "driver_age", "driver_experience"]
    contract = {
        "dataset": "addis_test",
        "kind": "multiclass",
        "git_commit": "testcommit0",
        "random_state": 42,
        "target": {"column": "severity", "classes": CLASSES},
        "input_features": [
            {"name": names[0], "kind": "categorical", "encoding": "onehot",
             "dtype": "string", "categories": onehot_cats},
            {"name": names[1], "kind": "numeric", "encoding": "numeric", "dtype": "float64"},
            {"name": names[2], "kind": "numeric", "encoding": "numeric", "dtype": "float64"},
        ],
        "encoded_feature_names": list(pipe.named_steps["encoder"].get_feature_names_out()),
    }
    (run_dir / "feature_contract.json").write_text(json.dumps(contract, indent=2), encoding="utf-8")

    meta = {
        "model": model_name,
        "model_version": "0.1.0-test",
        "git_commit": "testcommit0",
        "dataset": {"name": "addis_test", "kind": "multiclass", "rows": n,
                    "target": "severity", "classes": CLASSES},
        "metrics_cv": {"f1_macro": 0.5, "recall_macro": 0.5},
    }
    (run_dir / f"{model_name}.meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")


_build_artifact(_RUN)


@pytest.fixture(scope="session")
def artifact_dir() -> Path:
    return _RUN


@pytest.fixture(scope="session")
def build_artifact():
    """Expose the artifact builder for tests that need their own variant dir."""
    return _build_artifact


@pytest.fixture(scope="session")
def client():
    from fastapi.testclient import TestClient

    from backend.app.main import app

    with TestClient(app) as c:  # context manager triggers lifespan (load + seed)
        yield c


@pytest.fixture
def auth_headers(client) -> dict[str, str]:
    email = f"user-{uuid.uuid4().hex[:8]}@test.com"
    password = "supersecret1"
    reg = client.post(
        "/auth/register", json={"email": email, "password": password, "full_name": "Tester"}
    )
    assert reg.status_code == 201, reg.text
    tok = client.post("/auth/token", data={"username": email, "password": password})
    assert tok.status_code == 200, tok.text
    return {"Authorization": f"Bearer {tok.json()['access_token']}"}


@pytest.fixture
def valid_features() -> dict:
    return {"vehicle_type": "Motorcycle", "driver_age": 19, "driver_experience": 1}
