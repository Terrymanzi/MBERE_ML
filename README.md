![logo](image-2.png)

# MBERE ML

Driver road-accident risk prediction system — ML inference API + React dashboard.

---

## Demo

- **Demo & Testing Video:** [Click here](https://youtu.be/y-XU-ljegIc)
- **Deployed app:** [Click here](https://mbere-ml.netlify.app/)

---

## Installation & Running

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (optional, for PostgreSQL)

### 1. Clone & configure environment

```bash
git clone https://github.com/Terrymanzi/MBERE_ML
cd Codebase
cp .env.example .env   # edit values as needed
```

### 2. Backend

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Run DB migrations (SQLite by default; see .env for PostgreSQL)
alembic upgrade head

# Seed demo data (creates admin@mbere.local / ChangeMe!2026)
python scripts/seed.py

# Start API server (http://localhost:8000)
uvicorn backend.app.main:app --reload
```

> **PostgreSQL (optional):** set `DATABASE_URL=postgresql+psycopg2://mbere:mbere@localhost:5432/mbere` in `.env`, then run `docker compose up -d db` before migrations.

### 3. Frontend

```bash
cd frontend
cp .env.example .env   # set VITE_API_URL=http://localhost:8000
npm install
npm run dev            # http://localhost:5173
```

### 4. ML — train a model (optional)

```bash
pip install -r ml/requirements.txt
python train.py        # outputs artifact to ml/artifacts/runs/
```

Set `MODEL_NAME` and optionally `MODEL_RUN_DIR` in `.env` to point the backend at a specific run.

---

## Project Layout

```
data/          raw, processed, and external datasets
ml/            reusable ML code, trained artifacts, tests
backend/       FastAPI inference API, auth, database
frontend/      React + TypeScript dashboard
docs/          proposal, architecture, API docs
scripts/       automation helpers (seed, data prep)
```

---

## Testing

### Backend

```bash
pytest backend/tests/
```

### ML pipeline

```bash
pytest ml/tests/
```

---

## Testing Results

![Backend Testing Results](image.png)
![Ml Testing Results](image-1.png)

- Functionality under different testing strategies (unit, integration, end-to-end)
- Predictions with different driver/trip data values
- Performance on different hardware/software specs

---

## Analysis

The proposal sets three objectives.

### Objective 1: Data and features

The Addis Ababa RTA dataset (12,316 records, split 9,852 train / 2,464 test) was cleaned and 7 driver-and-context features were engineered and selected: driver age band, driver experience, time of day, vehicle type, weather, road surface, and light condition.
The prediction target is accident severity — Slight Injury ≈ 84.6%, Serious Injury ≈ 14.2%, Fatal Injury ≈ 1.3% — used as a risk-level proxy, making this a highly imbalanced multiclass problem. Because of that imbalance, macro-F1, recall, and ROC-AUC — not accuracy — are the headline metrics, and SMOTE is applied inside cross-validation on the training folds only, so no synthetic rows leak into evaluation.
A synthetic Rwandan-context validation set was generated with Tonic Fabricate (cited in the proposal's Appendix A for the generation policy).

Note on my feature signal: the engineered features carry weak individual predictive signal (mutual-information scores in the range 0.0006–0.0027). This is itself a finding, not a failure because I found out that predicting an individual's outcome from aggregated crash-record attributes, without behavioural telematics, is inherently hard and I have reported it transparently rather than hidding it behind a high accuracy figure.

### Objective 2: Models

Three models were trained and compared under stratified 5-fold cross-validation (CV metrics), with the transparent rule-based baseline as the bar the ML models had to beat.
The held-out test set metrics are reported alongside:

| Model               | Precision (macro) | Recall (macro) | F1 (macro) | ROC-AUC (OvR) |
| ------------------- | ----------------- | -------------- | ---------- | ------------- |
| Rule-based baseline | 0.343             | 0.333          | 0.336      | 0.531         |
| Random Forest       | 0.344             | 0.344          | 0.344      | 0.567         |
| XGBoost             | 0.331             | 0.331          | 0.330      | 0.530         |

(Test-set metrics from reports/\*/metrics.json; CV metrics are consistent with these figures.)

Random Forest beat the baseline on both macro-F1 (+0.008) and ROC-AUC (+0.036) and was selected as the production model. XGBoost matched the baseline on F1 but fell slightly below it on ROC-AUC on the held-out test set, despite stronger CV ROC-AUC (0.554), suggesting modest overfitting to the training distribution. The margins are small therefore this is the result given the weak feature signal documented above. Random Forest's ROC-AUC improvement of 3.6 points over the baseline is genuine and reproducible across CV folds.

The hardest class is Fatal Injury (≈1.3% of records). Fatal recall on the held-out test set: Random Forest = 3.2%, XGBoost = 0.0%, Baseline = 0.0%. Even with SMOTE, all three models struggle severely with this class — the 31 Fatal test cases are simply too few and too similar in feature space to the Serious class for reliable detection. This is reported explicitly rather than obscured by the aggregate metrics.

### Objective 3: Platform.

The React/TypeScript dashboard and FastAPI inference API were delivered and deployed (see the live demo link above). An insurer or fleet manager can select driver records from the interface and receive, per driver, a risk band, class probabilities, and SHAP-based explanations of the prediction. The SHAP analysis confirms that driver experience, driver age band, and time of day are the top three predictive features by mean |SHAP| value across both tree models, consistent with domain expectations. The dashboard, batch predict endpoint, and SHAP explanation endpoint are working end-to-end; real-time telematics integration and a Rwandan-specific retraining pipeline are scoped out of this prototype.

Synthetic validation (context check, not accuracy). Passing the Fabricate Rwandan-context set through the trained Random Forest model confirmed the expected monotonic trend: higher generated severity labels produced higher mean predicted probability of the severe classes. This confirms the system behaves plausibly on Rwanda-shaped inputs; it is not a measure of real-world Rwandan accuracy.
The Addis held-out test set remains the only source of performance metrics.

---

## Discussion

The value of this project lies as much in how it was built as in the headline metrics.

**Methodological milestones.**

- **A reproducible, leak-free pipeline** — fixed seeds, versioned artifacts, and SMOTE confined to training folds so any result can be regenerated with a single `python train.py`.
- **A baseline-to-beat design.** The interpretable rule-based model gave the ML approach a comparator, which is what turns any improvement (or its absence) into a real finding instead of an unanchored scores across.
- **Explainability by default** via SHAP, because the intended users(insurers and fleet operators), must be able to justify decisions, not merely receive them.
  **Why the framing matters.** Existing Rwandan road-safety ML operates at the aggregate level (accident counts, hotspots, ambulance placement). MBERE ML is the first in that context to attempt **driver-level** risk, operationalizing the individual profile factors such as sex, age, experience, education, that Rwandan studies have shown to be predictive. Even where the predictive signal is modest, demonstrating an end-to-end, explainable, reproducible driver-level pipeline is the contribution.

**limitations.**

These limitations do not undermine the result; they define precisely what the system does and does not claim.

- The model is trained on **Ethiopian (Addis Ababa) data as a proxy** for the Rwandan context; transfer is assumed, not proven.
- The Fabricate set validates **contextual behaviour, not accuracy**.
- Without **telematics**, the features describe driver/vehicle/environment _profiles_ rather than actual driving behaviour, which caps the individual signal available.
- Severe **class imbalance** makes the Fatal class hard to predict reliably, so minority-class recall deserves as much attention as any aggregate score.

---

## Recommendations

**Practical and community applications.**

- Motor insurers could pilot the risk bands as one input into risk-based pricing, therefore moving away from flat pooling.
- Fleet operators especially motorcycle-taxi cooperatives in Rwanda could use per-driver risk scores and SHAP explanations to target driver feedback, training and safety check-ins where they matter most.
- Regulators and road-safety bodies (e.g. BNR, Rwanda National Police, road-safety NGOs) could use aggregated risk patterns to focus limited intervention resources.

**Future work.**

- Collection of real Rwandan driver-level data in partnership with the Rwanda National Police, Rwanda Biomedical Centre or insurers, and run a true external validation.
- Fairness and ethics audit Because attributes used such as sex and age are predictive, using them to price risk scores raises real fairness and potential regulatory/legal concerns. Before any real-world pricing use, audit the model for disparate impact, decide which attributes are ethically and legally acceptable as pricing inputs, and document the trade-offs.
- Add telematics (speed, braking, time-of-day exposure) to move from profile-based to behaviour-based risk, which is where the driver-level literature finds the strongest signalling.
- Production deployment hardening: prediction monitoring, model-version rollback, and the retraining loop described in the proposal, fed by real labelled outcomes over time.
