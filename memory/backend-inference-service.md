---
name: backend-inference-service
description: FastAPI backend loads a versioned ml/ artifact and serves inference (no training); key wiring, auth, audit ERD, and the contract fail-fast
metadata:
  type: project
---

**Boundary:** `backend/` is inference-only — it deserializes a Pipeline artifact from `ml/artifacts/runs/<ts>_<sha>/` and runs `predict_proba` + SHAP. No sklearn fitting in backend app code (test fixtures may fit; that's allowed). Training stays in `ml/` + `train.py` ([[train-entrypoint-and-repro]]).

**Artifact = Pipeline, so feed RAW features:** the persisted `.pkl` is an imblearn/sklearn Pipeline `encoder -> [smote] -> classifier`; at inference the sampler is a no-op and the encoder transforms internally. The backend builds a 1-row DataFrame of the contract's `input_features` (raw engineered values) and calls `model.predict_proba` — never pre-encodes. SHAP is computed on the unwrapped tree classifier over the encoded row, then **aggregated back onto source feature names** (strip `transformer__` prefix, longest-prefix match) so explanations read as `vehicle_type / weather / road_surface`, not one-hot columns.

**Model selection (env, see root .env.example):** `MODEL_RUN_DIR` (specific run) or blank → auto-pick latest run under `ARTIFACTS_ROOT` containing `{MODEL_NAME}.pkl` + `feature_contract.json`; `MODEL_NAME` ∈ random_forest|xgboost|baseline. Startup validates the model's `feature_names_in_` set == contract feature names and meta class order == contract classes; mismatch raises `ContractMismatchError` (fail fast). Missing artifact → degraded start (`/health` flags it, `/predict` 503), not a crash. A `ModelVersion` row is upserted at startup and marked the sole `is_active`.

**Risk band vs class:** response gives both `predicted_class` (argmax) and a `risk_band` Low/Med/High from a `risk_score` in [0,1] — binary = P(positive); multiclass = normalized expected severity `Σ i·p_i/(n-1)`. Thresholds in Settings (0.34/0.67).

**Audit ERD:** `/predict` persists `FeatureRecord → RiskAssessment → Prediction`, and `Prediction.model_version_id` FKs the served `ModelVersion` for traceability. Tables: User, Driver, FeatureRecord, RiskAssessment, ModelVersion, Prediction (SQLAlchemy 2.0, generic `JSON` cols → works on SQLite + Postgres).

**Stack/env gotchas:** auth = passlib[bcrypt] + python-jose JWT; **pin `bcrypt==4.0.1`** (has a py3.13 wheel and avoids the passlib 1.7.4 `__about__` breakage). DB default is SQLite at repo root (`*.db` gitignored); prod = `postgresql+psycopg2://`. Run: `uvicorn backend.app.main:app`. Tests added to `pyproject` testpaths (`backend/tests`); backend tests build a self-contained temp artifact so they don't need `ml/artifacts/`. Full suite: 59 passing (39 ml + 20 backend). See [[python-env-313]].
