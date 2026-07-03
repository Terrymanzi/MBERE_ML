# MBERE ML

Driver road-accident risk prediction system — ML inference API + React dashboard.

---

## Demo

- **Demo & Teting Video:** [Click here](https://youtu.be/y-XU-ljegIc)
- **Deployed app:** [Click here](https://mbere-ml.netlify.app/)

---

## Installation & Running

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (optional, for PostgreSQL)

### 1. Clone & configure environment

```bash
git clone <repo-url>
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

_[Add analysis here — how results achieved or missed the objectives stated in the proposal]_

---

## Discussion

_[Add discussion here — importance of milestones and impact of results]_

---

## Recommendations

_[Add recommendations here — community applications and future work]_
