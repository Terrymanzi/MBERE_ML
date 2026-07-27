![logo](image-2.png)

# MBERE ML

Driver-context crash-severity risk profiling ML inference API + React dashboard for Rwandan motor insurers and fleet operators.

**Reframing note:** this system estimates a _crash-severity risk profile_ from driver, vehicle and environmental context it is **not** a claim about any individual driver's future crash probability. That would require per-driver exposure data (trips, kilometres, telematics) and longitudinal outcomes, neither of which exist in the underlying crash-record dataset. See [Model Selection & Decision Gate](#model-selection--decision-gate) and [Limitations](#limitations) below.

---

## Demo

- **Demo & Testing Video:** [Click here](https://youtu.be/y-XU-ljegIc)
- **Deployed app:** [Click here](https://mbere-ml.netlify.app/)
- **Backend server status monitoring:** [Click here](https://nrx1yhr8.status.cron-job.org/) live uptime status page for the Render-hosted backend, polled on a cron schedule.
- **Full technical report (PDF):** [docs/MBERE_ML_Capstone_Report_Terry Manzi.pdf](docs/MBERE_ML_Capstone_Report_Terry%20Manzi.pdf) the authoritative writeup: exact data version, model run, per-class results, limitations, and testing evidence. This README summarizes and must stay consistent with it; where the two ever disagree, the report + the committed `ml/artifacts/reports/*/metrics.json` files are ground truth.
- **Deployment runbook:** [DEPLOYMENT.md](DEPLOYMENT.md) environment config, migrations, monitoring, rollback, recovery, and end-to-end checks against the hosted API.

---

## Installation & Running

### Prerequisites

- Python 3.11+ (backend/ML pinned to 3.12.10 in production see `.python-version`)
- Node.js 18+ (developed/tested against Node 22, npm 10)
- Docker (optional, for a local PostgreSQL container)

### 1. Clone & configure environment

```bash
git clone https://github.com/Terrymanzi/MBERE_ML
cd MBERE_ML
cp .env.example .env.development  # edit values as needed
```

`backend/app/config.py` picks `.env.<APP_ENV>` (falling back to `.env` if that file
doesn't exist), so local dev reads `.env.development` and a real deployment reads
`.env.production` see [DEPLOYMENT.md](DEPLOYMENT.md) §1 for the full dev/prod
variable table. Neither file is committed; both are git-ignored.

### 2. Backend

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Run DB migrations (SQLite by default; see .env.development for PostgreSQL)
alembic upgrade head

# Seed demo data (creates admin@mbere.local / ChangeMe!2026)
python scripts/seed.py

# Start API server (http://localhost:8000)
uvicorn backend.app.main:app --reload
```

> **PostgreSQL (optional):** set `DATABASE_URL=postgresql+psycopg2://mbere:mbere@localhost:5432/mbere` in `.env.development`, then run `docker compose up -d db` before migrations.

### 3. Frontend

```bash
cd frontend
# frontend/.env.development already sets VITE_API_BASE_URL=http://localhost:8000
# (Vite loads it automatically in dev mode; frontend/.env.production is used for
# `npm run build` see DEPLOYMENT.md §3 for the Netlify equivalent)
npm install
npm run dev      # http://localhost:5173 (Netlify prod build serves the same app on :3000-shaped CORS origins)
```

### 4. ML train a model (optional)

```bash
pip install -r ml/requirements.txt
python train.py    # outputs artifact to ml/artifacts/runs/
```

`ml/artifacts/runs/` is git-ignored (local experiment scratch space see [Model Selection & Decision Gate](#model-selection--decision-gate)). The models actually served by the backend are the pinned, committed catalog under `ml/artifacts/*.pkl` + `ml/artifacts/reports/`. To promote a new local run into that catalog, copy its `{name}.pkl` / `{name}.meta.json` / `reports/{name}/` into `ml/artifacts/` the same layout the backend's model catalog expects and make sure it passes the decision gate before activating it (`POST /models/{name}/activate`, see below).

`MODEL_NAME` in `.env.development`/`.env.production` selects which catalog entry the backend serves by default; it must point at a model that passes the decision gate (currently `xgboost_tuned` see below), otherwise `POST /models/{name}/activate` will reject it.

### 5. Deployment

The app is deployed today: frontend on Netlify, backend + PostgreSQL on Render. See **[DEPLOYMENT.md](DEPLOYMENT.md)** for environment-specific config (dev vs. prod), the migration/monitoring/rollback/recovery runbook, and a scripted end-to-end check (`scripts/smoke_check.py`) you can run against the live hosted API.

---

## Project Layout

```
data/     raw, processed, and external datasets
ml/      reusable ML code, trained artifacts, tests
backend/    FastAPI inference API, auth, database
frontend/   React + TypeScript dashboard
docs/     full technical report (PDF), architecture, API docs
scripts/    automation helpers (seed, data prep, smoke_check.py, load_check.py)
DEPLOYMENT.md hosted-deployment runbook (env config, migrations, monitoring, rollback, recovery)
```

---

## Testing

### Backend (pytest, 38 tests)

```bash
pytest backend/tests/
```

Covers auth, health, the model registry/service, catalog + activation (including the decision gate), and `/predict` (happy path, bad features, contract fail-fast). Backend tests build their own tiny self-contained artifact in a temp dir, so they don't depend on the real `ml/artifacts/` catalog.

### ML pipeline (pytest)

```bash
pytest ml/tests/
```

Unit, integration, leakage-safety (SMOTE-fires-once-on-the-train-fold), and `ml/tests/test_gate.py`: the decision-gate module is regression-tested directly against the committed catalog metrics, so the "which models are/aren't deployable" claim below can't silently drift from the code that enforces it.

### Frontend (Vitest + React Testing Library, 31 tests) new

```bash
cd frontend
npm run test:run   # one-shot
npm run test     # watch mode
npm run typecheck   # tsc --noEmit
```

Covers the API client (auth headers, FastAPI error-body parsing, 401 handling, network failures), token storage, and UI components (`Button`, `RiskBadge`). There was previously no frontend automated test suite (the report's Chapter 4 disclosed this honestly as a limitation) this is the fix.

### End-to-end / deployment smoke checks new

```bash
python scripts/smoke_check.py --api https://mbere-ml.onrender.com --frontend https://mbere-ml.netlify.app
python scripts/load_check.py --api https://mbere-ml.onrender.com --requests 50 --concurrency 10
```

`smoke_check.py` exercises the real golden path against the **hosted** backend: health → register/login → feature contract → predict → SHAP explanation → active model's decision-gate status → frontend reachability. `load_check.py` is a lightweight concurrency/latency probe. Both are plain-stdlib Python (no extra install) so they run against any target local, Render, or a future environment. See [DEPLOYMENT.md](DEPLOYMENT.md#4-end-to-end-checks-against-the-hosted-api) for exit-code/CI semantics.

### Test matrix

The previous test suite (unit/integration/invalid-input/leakage) never demonstrated behaviour across operating systems, browsers, or language runtimes, and there was no load/latency evidence at all. Recorded here honestly real rows are what was actually run and observed; nothing below is extrapolated or assumed.

| Dimension              | Covered                                                                                 | Evidence                                                                                                                                                                                                                                                                       |
| ---------------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| OS                     | Windows 11 (10.0.26200)                                                                 | All commands above run and passing in this environment                                                                                                                                                                                                                         |
| Python                 | 3.13.9 (local dev venv), 3.12.10 (pinned prod via `.python-version`)                    | `pytest backend/tests ml/tests` 38+ passed on 3.13.9; Render deploy pinned to 3.12.10                                                                                                                                                                                          |
| Node.js                | v22.18.0 / npm 10.9.3                                                                   | `npm run test:run` 31 passed                                                                                                                                                                                                                                                   |
| Browser                | Chromium-family (manual, via the deployed Netlify app)                                  | Demo video; no automated cross-browser suite (Firefox/Safari) exists yet disclosed gap, not a claim                                                                                                                                                                            |
| Database mode          | SQLite (dev + full pytest suite), PostgreSQL 16 (prod, Render + local `docker-compose`) | SQLite: automated tests. Postgres: manual `docker compose up -d db && alembic upgrade head` locally, and the live Render deploy. No CI job runs the suite against Postgres yet disclosed gap                                                                                   |
| Hardware / latency     | Single local dev machine, 1 uvicorn worker, isolated throwaway SQLite DB                | `load_check.py --requests 60 --concurrency 10`: 0 failures, 29.3 req/s, latency p50=232ms p95=1134ms p99=2012ms (mean 322ms). SHAP computation on every `/predict` call is the dominant cost see [DEPLOYMENT.md](DEPLOYMENT.md)                                                |
| Load                   | 10 concurrent requests, 60 total                                                        | See above; not yet tested at higher concurrency or against the live Render instance (cold-start + free-tier CPU limits would change these numbers materially)                                                                                                                  |
| Deployment smoke check | Local (isolated DB)                                                                     | `smoke_check.py` all steps PASS, including `gate_passed=True` for the active `xgboost_tuned` model. **Not yet run against the live hosted URLs** this sandbox has no outbound network access; see [DEPLOYMENT.md §4](DEPLOYMENT.md#4-end-to-end-checks-against-the-hosted-api) |

Filling in the remaining gaps (macOS/Linux, Firefox/Safari, Postgres-backed CI, hosted-URL smoke run, higher-concurrency load) is tracked as follow-up work, not silently assumed done.

### Legacy screenshots

![Backend Testing Results](image.png)
![Ml Testing Results](image-1.png)

- Functionality under different testing strategies (unit, integration, end-to-end)
- Predictions with different driver/trip data values
- Performance on different hardware/software specs (see the **Test matrix** above for what's now actually measured, vs. what this screenshot originally summarized qualitatively)

---

## Analysis

The proposal sets three objectives.

### Objective 1: Data and features

The Addis Ababa RTA dataset (12,316 records, split 9,852 train / 2,464 test) was cleaned and 11 driver-and-context features were selected via mutual information (of 13 engineered candidates; `driver_sex` and `driver_education` were pruned as the weakest signal which also removes a direct protected attribute).
The prediction target is accident severity Slight Injury ≈ 84.6%, Serious Injury ≈ 14.2%, Fatal Injury ≈ 1.3% used as a risk-level proxy, making this a highly imbalanced multiclass problem. Because of that imbalance, macro-F1, recall, and ROC-AUC not accuracy are the headline metrics, and resampling is applied inside cross-validation on the training folds only, so no synthetic rows leak into evaluation.
A synthetic Rwandan-context validation set was generated with Tonic Fabricate (functionality/robustness check only, never a metrics source see the full report).

Note on feature signal: the engineered features carry weak individual predictive signal (mutual-information scores in the range 0.0002–0.0027). This is itself a finding, not a failure: predicting a crash-severity outcome from aggregated crash-record attributes, without behavioural telematics or per-driver exposure, is inherently hard, and it is reported transparently rather than hidden behind an aggregate accuracy figure.

### Objective 2: Models

Seven multiclass model configurations (a transparent rule-based baseline, plain Random Forest / XGBoost, and tuned/resampled variants of each) were trained and compared under stratified 5-fold cross-validation, with the baseline as the bar every ML candidate had to clear. Held-out test-set metrics (the only source of reported performance `ml/artifacts/reports/*/metrics.json`):

| Model                        | Macro-F1   | Macro-recall | Macro-precision | ROC-AUC (OvR) | Accuracy | Fatal recall | Passes deployment gate?                  |
| ---------------------------- | ---------- | ------------ | --------------- | ------------- | -------- | ------------ | ---------------------------------------- |
| Rule-based baseline          | 0.3357     | 0.3332       | 0.3435          | 0.5314        | 0.7646   | 0.0000       | (reference)                              |
| Random Forest                | 0.3126     | 0.3293       | 0.3155          | 0.5564        | 0.8194   | 0.0000       | ❌ fails F1 + recall                     |
| XGBoost                      | 0.3160     | 0.3354       | 0.3510          | 0.5489        | 0.8369   | 0.0000       | ❌ fails F1                              |
| Random Forest (tuned)        | 0.3344     | 0.3435       | 0.3397          | 0.5356        | 0.7573   | **0.0645**   | ❌ fails F1 (barely: 0.3344 vs. 0.3357)  |
| Random Forest (resampled)    | 0.3457     | 0.3499       | 0.3444          | 0.5456        | 0.7244   | 0.0000       | ✅ passes                                |
| XGBoost (resampled)          | 0.3447     | 0.3462       | 0.3433          | 0.5527        | 0.7472   | 0.0000       | ✅ passes                                |
| **XGBoost (tuned) selected** | **0.3473** | **0.3490**   | 0.3459          | 0.5547        | 0.7443   | 0.0000       | ✅ **passes canonical/production model** |

`xgboost_tuned` (v0.2.0-tuned) is the model actually served in production and the one this README, the full report, and the deployed app (`GET /health`, `GET /models/catalog`) all agree on. It beats the baseline on all three headline metrics macro-F1 +0.0116, macro-recall +0.0158, ROC-AUC +0.0233 and is also the best model on test macro-F1 among all seven candidates. See [Model Selection & Decision Gate](#model-selection--decision-gate) for why the _other_ six model files are still present in the catalog (for comparison/research) but are not the operational default.

The hardest class is Fatal Injury (≈1.3% of records, 31 held-out cases). Fatal recall on the held-out test set is **0.0000 for the selected model and for five of the seven candidates** the sole exception is `random_forest_tuned`, which recovers 2 of 31 cases (recall 0.0645) at low precision, but that model fails the deployment gate on macro-F1 and is not used operationally. Even with resampling, all models struggle severely with this class: 31 test cases is simply too few, and too similar in feature space to the Serious class, for reliable detection. This is reported explicitly, not smoothed over by the aggregate metrics see [Reframing](#reframing) below for what this means for how the output should and shouldn't be used.

### Objective 3: Platform

The React/TypeScript dashboard and FastAPI inference API were delivered and deployed (see the live demo link above; deployment details in [DEPLOYMENT.md](DEPLOYMENT.md)). An insurer or fleet manager can select driver records from the interface and receive, per driver, a risk band, class probabilities, and SHAP-based explanations of the prediction. The SHAP analysis confirms that driver experience, driver age band, and time of day are the top three predictive features by mean |SHAP| value for the selected model, consistent with domain expectations. The dashboard, batch predict endpoint, and SHAP explanation endpoint are working end-to-end; real-time telematics integration and a Rwandan-specific retraining pipeline are scoped out of this prototype.

Synthetic validation (context check, not accuracy). Passing the Fabricate Rwandan-context set through the trained model confirmed the expected monotonic trend: higher generated severity labels produced higher mean predicted probability of the severe classes. This confirms the system behaves plausibly on Rwanda-shaped inputs; it is not a measure of real-world Rwandan accuracy.
The Addis held-out test set remains the only source of performance metrics.

---

## Model Selection & Decision Gate

**The conflict this section resolves.** An earlier version of this README described an older training run's Random Forest result as "the production model," while the most recently saved plain `random_forest` catalog artifact the one that would have been served if the backend's default `MODEL_NAME` had been left unchanged actually underperforms the rule-based baseline on macro-F1 (0.3126 vs. 0.3357) and macro-recall (0.3293 vs. 0.3332), and recovers **zero** of the 31 Fatal test cases. That is not a documentation typo to smooth over; it is a real discrepancy between "what the README claimed" and "what the committed artifact actually does," and the fix has two parts:

1. **One canonical run, everywhere.** `xgboost_tuned` (v0.2.0-tuned, trained on the same Addis Ababa split as every other candidate in the table above) is now the single model this README, the full technical report, and the deployed backend's default configuration (`MODEL_NAME=xgboost_tuned` in `backend/app/config.py` / `.env.example`) all agree on. `GET /health` and `GET /models/catalog` on the running app report this same model, so "what's documented" and "what's served" can be checked against each other at any time that check is exactly what `scripts/smoke_check.py` automates.
2. **A default model-selection rule (the decision gate), enforced in code, not just in prose.** `ml/evaluation/gate.py` defines the rule: a candidate is deployable only if it is **≥ the rule-based baseline on all three held-out-test headline metrics** macro-F1, macro-recall, and one-vs-rest ROC-AUC (accuracy is deliberately excluded a model can hit ~85% accuracy by always predicting the majority class). This is exactly the acceptance criterion the full report already used to select `xgboost_tuned`; the gap this closes is that it previously lived only in the report, not in the running system. It is now:

- **Regression-tested** (`ml/tests/test_gate.py`) directly against the committed catalog metrics, so `xgboost_tuned` passing and plain `random_forest` failing are asserted, not just narrated.
- **Enforced at runtime**: `POST /models/{name}/activate` (the endpoint that flips the org-wide served model) rejects a gate-failing candidate with `409 Conflict` and the specific reasons, unless the caller explicitly passes `?force=true` a deliberate, human-reviewed override, never an automatic one.
- **Surfaced in the API**: `GET /models/catalog` reports `gate_passed` / `gate_reasons` per model, so the frontend (or an operator hitting the API directly) can see gate status without cross-referencing this README.

**Why Fatal-class recall is not a gate criterion.** It might seem like the gate should also require non-zero Fatal recall. It deliberately doesn't: every candidate trained so far baseline included recovers at most 2 of 31 held-out Fatal cases, so treating it as a hard blocker would make the gate unsatisfiable by construction rather than informative. Instead, near-zero Fatal recall is a disclosed limitation (see below) that is handled by _reframing what the output is allowed to claim_, not by pretending a model exists that solves it.

## Reframing

Given the above, the served output is explicitly scoped as follows, and the platform's disclaimers, docs, and this README are kept consistent with it:

- The risk band/score is a **crash-severity risk profile**, derived from aggregated driver/vehicle/environment attributes on _recorded_ crashes **not** a prediction of whether a specific driver will crash, and **not** a calibrated probability (no probability calibration is applied; resampling can itself degrade calibration).
- It does **not** model **individual driver exposure** (trips, kilometres, time-on-road) the source data has no such measure, so two drivers with identical profile features get identical predictions regardless of how much either actually drives.
- It does **not** model **longitudinal outcomes** there is no per-driver history in the training data linking the same driver across multiple crashes or none; the `RiskAssessment` audit trail in this platform accumulates prospectively (per operator-entered driver) but the _model_ was never trained on any such longitudinal signal.
- Given nonzero-but-poor Fatal-class detection across the model family (§ above), the output must not be read as a Fatal-outcome screen. Adding real per-driver exposure and longitudinal outcome data (telematics, claims history) is the concrete prerequisite for moving beyond this framing see Recommendations.
- Consistent with this, `xgboost_tuned` is not deployed for automatic decisions of any kind: every prediction requires human review, and the platform is documented throughout (see also the full report's Ethics & Responsible Use section) as decision support, not an automated pricing or eligibility tool.

---

## Discussion

The value of this project lies as much in how it was built as in the headline metrics.

**Methodological milestones.**

- **A reproducible, leak-free pipeline** fixed seeds, versioned artifacts, and resampling confined to training folds so any result can be regenerated with a single `python train.py`.
- **A baseline-to-beat design, now enforced by code.** The interpretable rule-based model gave the ML approach a comparator, which turns any improvement (or its absence) into a real finding instead of an unanchored score and the decision gate (above) makes "beat the baseline" a runtime constraint on what can be served, not just a reporting convention.
- **Explainability by default** via SHAP, because the intended users (insurers and fleet operators) must be able to justify decisions, not merely receive them.
- **Why the framing matters.** Existing Rwandan road-safety ML operates at the aggregate level (accident counts, hotspots, ambulance placement). MBERE ML is the first in that context to attempt **driver-context** crash-severity risk profiling, operationalizing the individual profile factors (age, experience, vehicle type, environment) that Rwandan and regional studies have shown to be predictive. Even where the predictive signal is modest, demonstrating an end-to-end, explainable, reproducible, gate-enforced pipeline is the contribution.

**Limitations**

These limitations do not undermine the result; they define precisely what the system does and does not claim.

- The model is trained on **Ethiopian (Addis Ababa) data as a proxy** for the Rwandan context; transfer is assumed, not proven.
- The Fabricate synthetic set validates **contextual behaviour, not accuracy**.
- Without **telematics or exposure data**, the features describe driver/vehicle/environment _profiles_ rather than actual driving behaviour or individual exposure, which caps the individual-level signal available (see [Reframing](#reframing)).
- Severe **class imbalance** makes the Fatal class hard to predict reliably across every model trained so far (max recall 0.0645); minority-class recall deserves as much attention as any aggregate score, and is why the decision gate does not treat it as a pass/fail criterion (see [Model Selection & Decision Gate](#model-selection--decision-gate)).
- **No calibration** is applied to the risk score; it is a relative ranking signal, not a statistically calibrated probability.
- Test-matrix coverage is real but partial (see [Testing](#testing)): no macOS/Linux or non-Chromium browser verification yet, no Postgres-backed CI, and the hosted-URL smoke/load checks have been written and locally verified but not yet run against the live Render/Netlify URLs from an environment with outbound network access.

---

## Recommendations

**Practical and community applications.**

- Motor insurers could pilot the risk bands as one input into risk-based pricing, therefore moving away from flat pooling subject to the fairness audit and regulatory review flagged in the full report.
- Fleet operators, especially motorcycle-taxi cooperatives in Rwanda, could use per-driver risk scores and SHAP explanations to target driver feedback, training and safety check-ins where they matter most.
- Regulators and road-safety bodies (e.g. BNR, Rwanda National Police, road-safety NGOs) could use aggregated risk patterns to focus limited intervention resources.

**Future work.**

- Collection of real Rwandan driver-level data in partnership with the Rwanda National Police, Rwanda Biomedical Centre or insurers, and run a true external validation.
- Fairness and ethics audit: because attributes such as age are predictive, using them to price risk scores raises real fairness and potential regulatory/legal concerns. Before any real-world pricing use, audit the model for disparate impact, decide which attributes are ethically and legally acceptable as pricing inputs, and document the trade-offs.
- Add telematics and **per-driver exposure** (speed, braking, time-of-day, trips/kilometres) plus **longitudinal outcomes**, to move from profile-based to behaviour-based risk this is the concrete prerequisite for relaxing the [Reframing](#reframing) constraints above, and where the driver-level literature finds the strongest signal.
- Close the remaining test-matrix and deployment-evidence gaps called out in [Testing](#testing) and [DEPLOYMENT.md](DEPLOYMENT.md) §5: a CI pipeline running the full suite (incl. against Postgres) on every push, and a hosted-URL smoke/load run from a network-connected environment (continuous uptime monitoring is already live see the [status page](https://nrx1yhr8.status.cron-job.org/)).
- Re-evaluate the decision gate as new candidates are trained: any future model must still be regression-tested against `ml/evaluation/gate.py` and pass `POST /models/{name}/activate` without `?force=true` before it can become the operational default.
