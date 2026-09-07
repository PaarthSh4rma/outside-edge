# Outside Edge

Outside Edge is an ad-free cricket intelligence application built with a
FastAPI backend, PostgreSQL persistence, Alembic migrations, and a React/Vite
frontend. It ingests cricket news from RSS feeds, stores and deduplicates
articles, generates the Daily Yorker briefing, exposes a match centre backed by
a provider-neutral score layer, and supports safe newsletter preview/dry-run
delivery through Resend.

This is a modular monolith portfolio project. The backend follows a
route -> service -> repository structure, and operational jobs reuse the same
services directly rather than calling HTTP endpoints.

## Implemented Features

- RSS ingestion from ESPNcricinfo and BBC Cricket.
- URL normalization and idempotent article persistence.
- Daily Yorker issue generation from stored articles.
- Public issue APIs for latest issue, archive, and dated issues.
- Subscriber signup, reactivation, and admin subscriber listing.
- Email rendering for HTML and plain text Daily Yorker newsletters.
- Resend email provider abstraction with safe dry-run defaults.
- Duplicate-send protection per issue/subscriber.
- Hashed unsubscribe tokens with no-login unsubscribe confirmation.
- Provider-neutral cricket score schema with realistic mock Test, ODI, and T20
  data.
- Public match APIs for live, upcoming, recent, and individual matches.
- React frontend with homepage, Daily Yorker archive, dated issue view, match
  centre, subscriber form, dark/light theme, responsive layout, and empty/error
  states.
- CLI jobs for fetching news, generating issues, and running the daily
  publisher.
- GitHub Actions CI for backend tests/migrations and frontend lint/build.
- Safe scheduled Daily Yorker dry-run workflow.
- Deployment documentation for a zero-cost fallback and optional Render setup.

## What Is Intentionally Mocked Or Limited

- Match data uses `MockScoreProvider`. The database/API shape is
  provider-neutral, but no real cricket score API is integrated yet.
- Newsletter delivery can send through Resend only when explicitly configured.
  Local, CI, and scheduled workflows default to dry-run and do not send email.
- The low-cost deployment path uses a public static frontend, a standalone
  FastAPI backend, Supabase Postgres, and GitHub Actions for scheduled dry-runs.
- There is no LLM/RAG layer, no user accounts, no betting/odds, and no
  ball-by-ball score model.

## Architecture

```text
frontend/                 React, Vite, React Router, Tailwind CSS
backend/app/api/          FastAPI route modules
backend/app/services/     Business logic and provider abstractions
backend/app/repositories/ SQLAlchemy database access
backend/app/models/       SQLAlchemy ORM models
backend/app/schemas/      Pydantic request/response schemas
backend/app/jobs/         CLI entrypoints for operational workflows
backend/migrations/       Alembic migrations
.github/workflows/        CI and scheduled dry-run publisher
```

Core backend flow:

```text
RSS feeds -> ArticleService -> ArticleRepository -> PostgreSQL
stored articles -> IssueService -> IssueRepository -> /issues APIs -> React UI
subscribers + issue -> EmailService -> renderer/provider -> delivery records
score provider -> ScoreService -> ScoreRepository -> /matches APIs -> React UI
```

## Local Setup

Copy the backend environment file:

```bash
cp backend/.env.example backend/.env
```

Minimum local backend env:

```env
DATABASE_URL=postgresql+psycopg2://sillypoint:sillypoint@localhost:5432/silly_point_db
DATABASE_SSLMODE=
ADMIN_API_KEY=replace-with-a-long-random-secret
CORS_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
SCORE_STALE_AFTER_MINUTES=5
EMAIL_FROM=Outside Edge <newsletter@example.com>
PUBLIC_SITE_URL=http://127.0.0.1:5173
EMAIL_DRY_RUN=true
RESEND_API_KEY=
```

Start PostgreSQL with Docker:

```bash
docker compose up postgres
```

Install and run the backend:

```bash
cd backend
python -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/alembic upgrade head
venv/bin/uvicorn app.main:app --reload
```

Install and run the frontend:

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Local URLs:

- Frontend: `http://127.0.0.1:5173`
- Backend docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

The complete Docker stack is also available:

```bash
ADMIN_API_KEY=replace-me docker compose up --build
```

Docker frontend: `http://127.0.0.1:8080`

## Daily Workflow

Set the admin key for local API calls:

```bash
export OUTSIDE_EDGE_ADMIN_KEY=replace-with-your-admin-key
```

Fetch RSS news:

```bash
curl -X POST http://127.0.0.1:8000/admin/fetch-news \
  -H "X-Admin-API-Key: $OUTSIDE_EDGE_ADMIN_KEY"
```

Generate today's Daily Yorker:

```bash
curl -X POST http://127.0.0.1:8000/admin/generate-issue \
  -H "X-Admin-API-Key: $OUTSIDE_EDGE_ADMIN_KEY"
```

Seed or refresh mock scores:

```bash
curl -X POST http://127.0.0.1:8000/admin/sync-scores \
  -H "X-Admin-API-Key: $OUTSIDE_EDGE_ADMIN_KEY"
```

Preview the latest email:

```bash
curl -X POST http://127.0.0.1:8000/admin/email/preview-latest \
  -H "X-Admin-API-Key: $OUTSIDE_EDGE_ADMIN_KEY"
```

Run a safe email dry-run:

```bash
curl -X POST \
  "http://127.0.0.1:8000/admin/email/send-latest?dry_run=true" \
  -H "X-Admin-API-Key: $OUTSIDE_EDGE_ADMIN_KEY"
```

## CLI Jobs

The same operational workflow can run without HTTP:

```bash
cd backend
venv/bin/python -m app.jobs.fetch_news
venv/bin/python -m app.jobs.generate_issue
venv/bin/python -m app.jobs.publish_daily_yorker --dry-run
```

The publisher fetches news, generates or replaces today's issue while
preserving issue delivery history, renders the email, and reports fetched,
saved, article, recipient, sent, skipped, and failed counts.

`--send` is available, but real delivery still requires all safeguards:

1. `EMAIL_DRY_RUN=false`
2. a valid `RESEND_API_KEY`
3. the command or route using `dry_run=false` / `--send`

Successful deliveries are not repeated for the same issue/subscriber unless
`force=true` is supplied through the admin route.

## Public API

Selected public endpoints:

- `GET /health`
- `GET /articles?limit=50`
- `GET /issues/latest`
- `GET /issues`
- `GET /issues/{issue_date}`
- `POST /subscribers`
- `GET /matches/live`
- `GET /matches/upcoming`
- `GET /matches/recent`
- `GET /matches/{match_id}`
- `GET /unsubscribe/{token}`
- `POST /unsubscribe/{token}`

Every `/admin` route requires:

```text
X-Admin-API-Key: your-admin-key
```

## Testing And Quality

Backend:

```bash
cd backend
venv/bin/python -m pytest -q
EMAIL_FROM="Outside Edge <newsletter@example.com>" \
PUBLIC_SITE_URL="http://127.0.0.1:5173" \
EMAIL_DRY_RUN=true \
venv/bin/alembic upgrade head
EMAIL_FROM="Outside Edge <newsletter@example.com>" \
PUBLIC_SITE_URL="http://127.0.0.1:5173" \
EMAIL_DRY_RUN=true \
venv/bin/alembic check
```

Frontend:

```bash
cd frontend
npm run lint
npm run build
```

GitHub Actions runs backend tests, Alembic upgrade/check, frontend lint, and
frontend build on pull requests and pushes to `main`.

## Deployment

No deployment is included or assumed. The repository is prepared for a
low-cost/manual deployment topology:

- Frontend: Cloudflare Pages.
- Database: Supabase Postgres.
- Backend: standalone FastAPI web service on Render or Koyeb.
- Daily publisher: GitHub Actions scheduled workflow.
- Email: dry-run only by default.

### Supabase Postgres

Create a Supabase project and copy a Postgres connection string from the
dashboard. For IPv4-only hosts, use the Session Pooler connection string. The
backend accepts either `postgres://...` or `postgresql://...` and normalizes it
for SQLAlchemy.

Recommended production database env:

```text
DATABASE_URL=postgres://postgres.project-ref:password@aws-region.pooler.supabase.com:5432/postgres
DATABASE_SSLMODE=require
```

If your Supabase URL already includes `sslmode=require` or
`sslmode=verify-full`, keep it in the URL. The optional `DATABASE_SSLMODE`
setting only adds an SSL mode when the URL does not already include one.

Run migrations against Supabase:

```bash
cd backend
DATABASE_URL="postgres://..." \
DATABASE_SSLMODE=require \
ADMIN_API_KEY="migration-only-secret" \
EMAIL_FROM="Outside Edge <newsletter@example.com>" \
PUBLIC_SITE_URL="https://your-project.pages.dev" \
EMAIL_DRY_RUN=true \
venv/bin/alembic upgrade head
```

### Backend On Render Or Koyeb

Deploy only the `backend` directory as a Python web service.

Backend environment variables:

- `DATABASE_URL`: Supabase Postgres or Session Pooler connection string.
- `DATABASE_SSLMODE`: `require` unless the URL already has `sslmode`.
- `ADMIN_API_KEY`: long random secret used for `/admin` routes.
- `CORS_ORIGINS`: comma-separated Cloudflare Pages origins, for example
  `https://your-project.pages.dev,https://outside-edge.example.com`.
- `SCORE_STALE_AFTER_MINUTES`: `5`.
- `EMAIL_FROM`: `Outside Edge <newsletter@example.com>` or a verified sender
  later.
- `PUBLIC_SITE_URL`: Cloudflare Pages URL.
- `EMAIL_REPLY_TO`: optional.
- `EMAIL_DRY_RUN`: `true`.
- `RESEND_API_KEY`: leave unset while email is dry-run only.

Render settings:

- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Pre-deploy command: `alembic upgrade head`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health check path: `/health`

Koyeb settings:

- Service type: Python web service from the `backend` directory.
- Build command: `pip install -r requirements.txt`
- Run command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Expose the HTTP port provided through `PORT`.
- Run `alembic upgrade head` from GitHub Actions or locally before/after the
  first deploy, since this repository does not require a hosted cron or worker.

`render.yaml` remains as an optional Render web/static blueprint, but it no
longer provisions Render PostgreSQL or Render cron. Use Supabase for the
database and GitHub Actions for the scheduled publisher.

### Cloudflare Pages Frontend

Cloudflare Pages settings:

- Root directory: `frontend`
- Build command: `npm ci && npm run build`
- Output directory: `dist`
- Node version: pinned by `frontend/.node-version`
- Environment variable: `VITE_API_BASE_URL=https://your-backend.example.com`

React Router deep links are handled by `frontend/public/_redirects`.

If `VITE_API_BASE_URL` is omitted, API-backed sections will show unavailable
states because the frontend intentionally does not hardcode a backend URL.

### GitHub Actions Scheduler

Add these GitHub repository secrets:

- `DATABASE_URL`
- `DATABASE_SSLMODE` set to `require` if the URL does not already include
  `sslmode`
- `ADMIN_API_KEY`
- `EMAIL_FROM`
- `PUBLIC_SITE_URL`
- `EMAIL_DRY_RUN` set to `true`

The scheduled workflow at `.github/workflows/daily-yorker.yml` runs:

```bash
python -m app.jobs.publish_daily_yorker --dry-run
```

Before publishing, the workflow runs `alembic upgrade head` against the same
Supabase database. It does not require `RESEND_API_KEY` and must not send real
email while the command remains `--dry-run` and `EMAIL_DRY_RUN=true`.

To enable real newsletter sending later:

1. Run the workflow manually and confirm `effective_dry_run=true`.
2. Add `RESEND_API_KEY` as a GitHub secret.
3. Set `EMAIL_DRY_RUN=false`.
4. Change the scheduled command from `--dry-run` to `--send`.
5. Run manually again before trusting the schedule.

Keep the scheduled workflow dry-run until a verified Resend sender, seed
subscriber, and manual preview have all been checked.

## Resume Positioning

This project is safe to describe as a complete full-stack portfolio application
with automated ingestion, PostgreSQL persistence, issue generation, public APIs,
subscriber management, safe newsletter workflows, mock/provider-neutral scores,
CI, and documented deployment options.

Do not describe it as using live score data, AI-generated insight, RAG, or a
fully hosted production backend unless those are added later.
