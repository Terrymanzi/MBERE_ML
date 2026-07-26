# Deployment

MBERE ML is deployed as three independent, separately-hosted pieces that only
ever talk to each other over HTTPS/JSON (never a shared filesystem or process):

| Component | Host | URL |
| --- | --- | --- |
| Frontend (React/Vite static build) | Netlify | https://mbere-ml.netlify.app |
| Backend (FastAPI inference API) | Render (web service) | https://mbere-ml.onrender.com |
| Database (PostgreSQL 17) | Supabase (managed Postgres) | private, `DATABASE_URL` only |

> **Migration note (2026-07-26):** the database moved from Render's managed
> Postgres to Supabase Postgres. Data was migrated with `pg_dump -Fc` /
> `pg_restore` (row counts and content verified to match post-restore). The old
> Render Postgres instance is being kept running, unmodified, as a cold backup
> for now — it is no longer the source of truth and nothing points at it
> anymore. Decommission it once you're confident in the Supabase setup.

This document is the operational counterpart to the [README](README.md)'s
"Installation & Running" section, which covers **local** dev. It exists because
the feedback that prompted it was explicit: the app being live isn't the same
as the deployment being *documented* — this file is that documentation, plus
the gaps that were missing (env separation, migrations, monitoring, rollback,
recovery, and a scripted end-to-end check against the real hosted API).

---

## 1. Environment-specific configuration

The backend reads all configuration from environment variables (via
`backend/app/config.py` / `pydantic-settings`), never from a committed secret.
Locally, `backend/app/config.py` picks `.env.<APP_ENV>` — i.e. `.env.development`
or `.env.production` — falling back to a plain `.env` if that file doesn't
exist; both `.env.development` and `.env.production` are git-ignored (never
committed). On Render, real env vars set in the dashboard's *Environment* tab
take precedence over any file, so this file-selection logic never matters
there — it only affects local runs. Dev and prod diverge on exactly these
values:

| Variable | Dev (local `.env.development`) | Prod (`.env.production` locally / Render env vars) |
| --- | --- | --- |
| `APP_ENV` | `development` | `production` |
| `DATABASE_URL` | `sqlite:///./mbere_backend.db` | `postgresql+psycopg2://…` (Supabase Postgres session-pooler connection string) |
| `SECRET_KEY` | dev default (in `.env.example`) | a real 48-byte secret, generated once and stored **only** in Render's env var UI |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173` | `https://mbere-ml.netlify.app` |
| `MODEL_NAME` | `xgboost_tuned` | `xgboost_tuned` (must match the catalog entry documented in the README as canonical) |
| `MODEL_CATALOG_DIR` | `ml/artifacts` (default) | `ml/artifacts` (default — the repo, including the pinned catalog artifacts, ships with the image) |

The frontend has its own, much smaller, environment surface — Vite natively
picks `.env.development` (dev server) or `.env.production` (`npm run build`),
and both files are safe to commit since they hold no secrets:

| Variable | Dev (local `frontend/.env.development`) | Prod (`frontend/.env.production` / Netlify env var) |
| --- | --- | --- |
| `VITE_API_BASE_URL` | `http://localhost:8000` | `https://mbere-ml.onrender.com` |

> **The bug this fixes:** the root README previously told developers to set
> `VITE_API_URL`, but the code (`apiClient.ts`, `vite-env.d.ts`) only ever reads
> `VITE_API_BASE_URL`. Both `.env.example` files already used the correct name;
> only the prose in the root README was wrong. It's fixed there now — this
> table is the single source of truth for the variable name going forward.

Nothing else differs between dev and prod: same Alembic migrations, same
FastAPI app, same model catalog, same auth flow. That symmetry is deliberate —
it's what makes "it works locally" a meaningful signal for "it'll work in prod".

---

## 2. Backend on Render

Render builds and runs the repo root (not just `backend/`), because the
backend imports the sibling `ml` package at runtime (model deserialization,
the decision gate, the synthetic-validation endpoint).

**Build command:**
```bash
pip install -r backend/requirements.txt
```

**Start command:**
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

**Runtime:** Python is pinned via the repo's `.python-version` (`3.12.10`) —
Render's Python buildpack reads this automatically. This pin exists because an
earlier deploy broke on Render's then-default Python version; don't remove it
without re-verifying a clean deploy.

**Required Render env vars** (set in the service's *Environment* tab, never
committed): `SECRET_KEY`, `DATABASE_URL` (points at Supabase's session pooler —
see §2.1 — since the database is no longer a linked Render Postgres instance,
this must be set manually rather than auto-injected), `CORS_ORIGINS`,
`MODEL_NAME`. See the table in §1 for prod values.

**Artifacts:** the model catalog (`ml/artifacts/*.pkl`, `*.meta.json`,
`reports/`) is committed to the repo and ships as part of the deploy — there is
no separate artifact upload step. `ml/artifacts/runs/` (ad-hoc local training
runs) is gitignored and irrelevant to what's served; see the README's "Model
Selection & Decision Gate" section for why only the top-level catalog matters.

### 2.1 Database migrations (Supabase Postgres)

Schema changes are owned by Alembic (`backend/migrations/`), never by
`Base.metadata.create_all` (that only fires as a dev convenience no-op once the
schema exists). Run migrations against the **prod** database from a shell with
`DATABASE_URL` pointed at Supabase — either Render's own **Shell** tab on the
backend service (env vars are already in scope there), or locally with the
prod `DATABASE_URL` exported for one command:

```bash
DATABASE_URL="postgresql+psycopg2://<supabase-session-pooler-connection-string>" alembic upgrade head
```

Use Supabase's **session pooler** connection string (Dashboard → Project
Settings → Database → Connection string → *Session pooler*), not the direct
`db.<ref>.supabase.co` host — that host is IPv6-only on this project's plan
and isn't reachable from Render or most local networks. The session pooler
(port 5432) is required over the transaction pooler (port 6543) because
SQLAlchemy relies on prepared statements, which the transaction pooler doesn't
support reliably.

Run this **once per new migration**, as part of the deploy (before or
immediately after Render restarts the service — the app tolerates a moment of
schema lag since `create_all` is a harmless no-op, but don't rely on that for
anything but the very first deploy). To check what's applied:

```bash
DATABASE_URL="..." alembic current
DATABASE_URL="..." alembic history
```

There is currently one migration (`0001_20260629_initial_schema`); it creates
the full schema (users, drivers, feature records, model versions, risk
assessments, predictions) in one shot.

### 2.2 Monitoring

- **`GET /health`** is the primary liveness/readiness signal: `{"status": "ok" | "degraded", "db_ok": bool, "model_loaded": bool, "model": {...}}`. `degraded` means either the DB ping failed or no model is loaded — both are things to alert on, not crash on (the app deliberately stays up in a degraded state rather than refusing to boot, so `/health` itself always answers).
- **Render's built-in dashboard** (Logs, Metrics tabs) covers process-level signals: CPU/memory, restart events, deploy history, and structured `logger.info`/`logger.warning` output from `backend/app/main.py` (model load, activation, degraded-start reasons).
- **External uptime monitoring (live):** [cron-job.org status page](https://nrx1yhr8.status.cron-job.org/) polls the hosted backend on a schedule and publishes a public uptime/incident history. This is the continuous-monitoring evidence for the deploy — link it (or a screenshot of its history) alongside any deployment sign-off. It complements, but doesn't replace, `scripts/smoke_check.py` (§4): the status page proves the process is *up*; the smoke check proves the golden path (auth → predict → SHAP → gate status) is actually *correct*.

### 2.3 Rollback

Three independent rollback levers, because the three things that can break
independently (code, schema, active model) can each need to roll back alone:

1. **Code rollback.** Render keeps a deploy history per service; use *Manual
   Deploy → Deploy a previous commit* (or `git revert` + push, which is the
   safer default per this project's git safety rules) to redeploy the last
   known-good commit.
2. **Model rollback.** Switching the *served* model does not require a code
   deploy at all: `POST /models/{name}/activate` (JWT-authenticated) flips the
   org-wide active model to any catalog entry, and it's recorded in the
   `ModelVersion` table with a timestamp — so "what was active when" is always
   reconstructable. A candidate that fails the deployment decision gate (see
   README) is rejected with `409` unless you pass `?force=true`, so an accidental
   rollback to a known-weak model can't happen silently.
3. **Schema rollback.** `alembic downgrade -1` (or `alembic downgrade base` for
   a full teardown) reverses the most recent migration against the prod
   database. Treat this as a last resort — reversing a schema change that has
   already accepted new-shape data can lose that data.

### 2.4 Backup & recovery

Supabase's managed Postgres takes automated backups with point-in-time
recovery (retention depends on your Supabase plan — check Project Settings →
Database → **Backups** for the exact window). To restore:

- **Supabase UI restore:** Project Settings → Database → Backups → pick a
  snapshot → *Restore*.
- **Manual logical backup** (extra safety net, run from anywhere with
  `DATABASE_URL` in scope — a local Docker `postgres` container works well
  here if `pg_dump`/`pg_restore` aren't installed natively, since the client
  version must be >= the server's):
  ```bash
  pg_dump "$DATABASE_URL" -Fc --no-owner --no-privileges -f mbere_backup_$(date +%Y%m%d).dump
  pg_restore -d "$DATABASE_URL" --no-owner --no-privileges mbere_backup_20260101.dump   # restore
  ```
- **Old Render Postgres instance:** kept running, untouched, as a cold backup
  of the pre-migration (2026-07-26) data. It is not wired to anything anymore
  — treat it as a last-resort fallback, not a live replica.
- **Model-artifact recovery** doesn't need a database restore at all: the
  catalog is version-controlled in git, so `git checkout <commit> -- ml/artifacts`
  followed by a redeploy recovers any previously-served model exactly.

---

## 3. Frontend on Netlify

**Build command:** `npm run build` (runs `tsc` then `vite build`)
**Publish directory:** `dist`
**Redirects:** `frontend/netlify.toml` rewrites all paths to `/index.html` (the
app is a client-routed SPA via `react-router-dom`).

**Required Netlify env var:** `VITE_API_BASE_URL=https://mbere-ml.onrender.com`
(Site settings → Environment variables — Vite inlines this at *build* time, so
changing it requires a rebuild, not just a restart).

**Rollback:** Netlify keeps every deploy; *Deploys* tab → pick a prior deploy →
*Publish deploy* instantly repoints the live URL, no rebuild needed.

---

## 4. End-to-end checks against the hosted API

`scripts/smoke_check.py` is a dependency-free script (stdlib `urllib` only —
runs anywhere with a Python 3 interpreter and outbound internet access) that
exercises the real golden path against the **live** hosted backend: health →
register/login → feature contract → predict → SHAP explanation → decision-gate
status of the active model → frontend reachability. It's the automated version
of the manual "definition of done" checklist in `frontend/README.md`.

```bash
python scripts/smoke_check.py \
    --api https://mbere-ml.onrender.com \
    --frontend https://mbere-ml.netlify.app
```

It prints `[PASS]`/`[FAIL]` per step and exits non-zero on the first failure,
so it's CI-friendly (e.g. run it as a post-deploy step, or on the recurring
schedule mentioned in §2.2).

**Honesty note:** the sandbox this repository was edited in has no outbound
network access, so this script has been written and reviewed but **not yet
executed against the live hosted URLs** as part of this change. Run it
yourself and treat its first real output as the actual e2e evidence for this
deployment — don't take this file's word for what it prints.

---

## 5. What's still missing (tracked honestly, not hidden)

- No automated CI pipeline runs `pytest` / `vitest` / the smoke check on every
  push; all of the above are run manually today (the uptime monitor in §2.2 is
  the one continuous/automated check that does exist).
- Render's free-tier web services spin down on idle and cold-start on the next
  request — acceptable for a capstone demo, worth flagging before any real
  usage commitment (cold start manifests as a slow first `/health` or `/predict`
  call, not a failure).
