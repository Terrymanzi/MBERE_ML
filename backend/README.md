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
URL for PostgreSQL. On startup the app calls `create_all` (a no-op once the
schema exists), but **Alembic owns the schema in prod** — see below.

## PostgreSQL + migrations + seed
```bash
# 1. start Postgres 16 (named volume `mbere-pgdata`); creds from .env (POSTGRES_*)
docker compose up -d db

# 2. point the backend at it (.env)
#    DATABASE_URL=postgresql+psycopg2://mbere:mbere@localhost:5432/mbere

# 3. create the schema from the migrations (reversible)
alembic upgrade head        # run from the repo root; reads DATABASE_URL from .env
#   alembic downgrade base  # full teardown (migrations are reversible)

# 4. load demo data: a fleet-admin user, a few drivers, and a ModelVersion row
#    built from the CURRENT artifact's meta.json (so predictions are traceable)
python scripts/seed.py      # admin creds via SEED_ADMIN_EMAIL/SEED_ADMIN_PASSWORD

# 5. run the API; GET /drivers now returns the seeded fleet
uvicorn backend.app.main:app --port 8000
```
The Alembic config (`alembic.ini` at the repo root, env in `backend/migrations/`)
takes the database URL from `.env` via the backend `Settings` — no connection
string or secret is hardcoded. The same migrations target SQLite (dev) or
PostgreSQL (prod) purely from the environment.

## Tests
```bash
pytest backend/tests          # 20 tests: health, auth, predict (happy + bad-feature), contract fail-fast
```
Backend tests build their own tiny self-contained artifact in a temp dir, so they
don't depend on the gitignored `ml/artifacts/`.
