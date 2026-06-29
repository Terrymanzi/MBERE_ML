---
name: frontend-console
description: React/Vite frontend in frontend/ — feature-based, typed fetch client mirroring backend schemas, contract-driven prediction form, dashboard via risk fan-out
metadata:
  type: project
---

**Frontend lives in `frontend/`** (React 18 + TS + Vite + Tailwind + TanStack Query + React Router + Recharts). UI only — all data from the FastAPI [[backend-inference-service]]; no mock data committed. Stack additions were kept to the declared set: **no axios** (typed `fetch` wrapper in `src/services/apiClient.ts`), **no icon lib** (inline SVGs in `src/components/icons.tsx`), **no form lib**.

**Feature-based layout:** `src/services/` (typed client + `types.ts` mirrored 1:1 from `backend/schemas/*`), `src/lib/` (queryClient, queryKeys, format, cn), `src/components/` (ui/, feedback/, layout/), `src/features/{auth,dashboard,drivers,prediction,analytics,models,settings,marketing}`. Path alias `@/` → `src/` (set in both tsconfig paths and vite resolve.alias).

**Auth:** JWT in `localStorage` (key `mbere.jwt`), attached as Bearer by the client; `AuthContext` validates a persisted token via `/auth/me` on load; a 401 on any authed request dispatches a `mbere:unauthorized` window event → global logout. Login uses the OAuth2 **form-encoded** `/auth/token` (username=email). Routes gated by `ProtectedRoute` under `/app/*`; public `/` landing + `/login`.

**Two integration subtleties that matter:**
1. **Prediction form is generated from `GET /models/contract`** (categorical→`<select>` from `categories`, numeric→number input). `featureForm.ts` converts DOM strings back to native types (numeric→Number, categorical→the category's native value) because the backend coerces numeric `_cat` categories as ints. This keeps the form dataset-agnostic (Porto/Addis) with zero hardcoded feature names.
2. **No aggregate endpoint exists**, so the dashboard (`useDashboard.ts`) composes real data by fanning out `GET /risk/{driver_id}` across `GET /drivers` and deriving risk-band counts (latest per driver), latest-predictions table, and mean-|SHAP| feature importance. Cached under one `["dashboard"]` key; invalidated after a predict/create-driver mutation.

**Verified (2026-06-29):** `npm run build` green (tsc + vite, chunk-split react/charts/query). Live integration smoke against a seeded SQLite backend passed the frontend's exact request sequence: form login → `/auth/me` → public `/models/contract` (23 inputs) → `/predict` (driver-attached, band Low, score 0.290, SHAP method, 8 top_features, probs sum 1) → `/drivers` (5 seeded) → `/risk/{id}` (assessment with prediction) → `/models` (1 active). Dev server runs on port 3000 (in backend CORS allow-list); `VITE_API_BASE_URL` defaults to `http://localhost:8000`.
