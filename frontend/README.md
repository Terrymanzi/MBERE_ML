# frontend — MBERE ML console

React + TypeScript + Vite UI for the inference API. **UI only**: every piece of
data comes from the FastAPI backend; no data is mocked or committed.

Stack: React 18, Vite, Tailwind, TanStack Query, React Router, Recharts.

## Architecture (feature-based)
```
src/
  services/        Typed API client + types mirrored from the backend schemas
                   (apiClient.ts attaches the JWT; *.api.ts per resource).
  lib/             queryClient, queryKeys, formatting, cn helper.
  components/      Reusable UI (ui/), feedback states, layout chrome, icons.
  features/
    auth/          AuthContext (JWT), LoginPage, ProtectedRoute.
    dashboard/     Aggregated widgets + charts (useDashboard).
    drivers/       List, details, create.
    prediction/    Contract-driven form + result (risk band, probs, SHAP).
    analytics/     Trend, score histogram, distributions.
    models/        Model registry + metrics.
    settings/      Connection/model settings + profile.
    marketing/     Public landing + 404.
```

Key ideas:
- **Types come from the backend.** `services/types.ts` is a 1:1 mirror of
  `backend/schemas/*`. The API client is a thin typed `fetch` wrapper — no axios.
- **The prediction form is generated from the model contract** (`GET /models/contract`),
  so it adapts to whatever dataset the served artifact uses (Porto today, Addis
  later) without code changes.
- **No aggregate endpoint exists**, so the dashboard composes real data by fanning
  out `GET /risk/{driver_id}` over the driver list (cached under one query key).
- **JWT** is stored in `localStorage`; a 401 on any authed request triggers logout.
- Every data view renders explicit **loading / error / empty** states.

## Run it
```bash
cd frontend
npm install
cp .env.example .env     # VITE_API_BASE_URL (default http://localhost:8000)
npm run dev              # http://localhost:3000  (in the backend CORS allow-list)
```
Production build / typecheck:
```bash
npm run build            # tsc + vite build
npm run typecheck
```

## End-to-end (definition of done)
With the backend running, migrated and seeded (see `../backend/README.md`):
1. Log in with the seeded fleet-admin (`admin@mbere.local`).
2. Dashboard shows total drivers, risk-band counts, risk distribution, SHAP
   feature importance, and the latest predictions table.
3. Drivers → open a driver → view risk history.
4. Prediction → fill the contract form → submit → risk band, class
   probabilities, and per-prediction SHAP top-features render.
