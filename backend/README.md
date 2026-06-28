# backend — inference & platform API

FastAPI service that **loads a versioned ML artifact and serves inference**. It
never trains: it only deserializes a Pipeline produced by the `ml/` package and
runs `predict_proba` + SHAP. Training lives entirely in `ml/` / `train.py`.

## What it serves
- `GET  /health` — liveness + which model/contract is loaded (no auth)
- `POST /auth/register`, `POST /auth/token`, `GET /auth/me` — JWT auth
- `POST /predict` — risk band + class probabilities + SHAP top-features; writes
  an audit trail (`FeatureRecord → RiskAssessment → Prediction`, FK'd to the
  `ModelVersion`)
- `POST /drivers`, `GET /drivers`, `GET /risk/{driver_id}` — drivers + history
- `GET  /models`, `GET /models/contract` — served-artifact registry + the input
  feature contract (handy for building request forms)
- OpenAPI docs at `/docs`.

## How the artifact is selected
Set in `.env` (see `.env.example` at the repo root):
- `MODEL_RUN_DIR` — a specific `ml/artifacts/runs/<ts>_<sha>/` directory, **or**
  leave it blank to auto-pick the latest run under `ARTIFACTS_ROOT` that contains
  `{MODEL_NAME}.pkl` + `feature_contract.json`.
- `MODEL_NAME` — `random_forest` | `xgboost` | `baseline`.

At startup the loaded model's expected feature set is checked against the
contract; **mismatch fails fast** (`ContractMismatchError`). If no artifact is
found at all, the app starts *degraded* (`/health` reports it, `/predict` → 503).

The backend feeds the model the **raw engineered features** named in the
contract's `input_features`; the persisted Pipeline encodes internally, so the
request shape matches the contract exactly.

## Run it
```bash
# from the repo root, with the project venv active
pip install -r backend/requirements.txt
cp .env.example .env          # set SECRET_KEY; point MODEL_RUN_DIR at a run
uvicorn backend.app.main:app --reload --port 8000
# -> http://localhost:8000/docs
```

Default `DATABASE_URL` is SQLite (repo root); set a `postgresql+psycopg2://…`
URL for PostgreSQL. Tables are created on startup; Alembic owns prod migrations.

## Tests
```bash
pytest backend/tests          # 20 tests: health, auth, predict (happy + bad-feature), contract fail-fast
```
Backend tests build their own tiny self-contained artifact in a temp dir, so they
don't depend on the gitignored `ml/artifacts/`.
