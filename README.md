# Outside Edge

Outside Edge is a full-stack cricket intelligence application. It turns RSS
cricket news into a persisted article library, generates a Daily Yorker
briefing, exposes issue and match-centre APIs, supports subscriber management,
and renders a polished React frontend.

The project is intentionally scoped: it is a working modular monolith with
PostgreSQL persistence, safe email dry-runs, provider-neutral mock scores, CI,
and deployment documentation. It does not claim live score integrations,
AI-generated analysis, RAG, user accounts, or production email sending.

## Highlights

- FastAPI backend with route -> service -> repository boundaries.
- PostgreSQL data model managed by Alembic migrations.
- RSS ingestion from ESPNcricinfo and BBC Cricket.
- Article URL normalization and idempotent deduplication.
- Daily Yorker issue generation, archive, and dated issue API.
- Subscriber signup, reactivation, unsubscribe tokens, and admin listing.
- HTML/plain-text newsletter rendering with Resend provider abstraction.
- Safe newsletter preview and dry-run delivery workflows.
- Duplicate-send protection for issue/subscriber deliveries.
- Provider-neutral match schema with realistic mock Test, ODI, and T20 data.
- React/Vite frontend with responsive layout, dark/light theme, archive,
  dated issues, match centre, loading states, empty states, and error states.
- CLI jobs for ingestion, issue generation, and the daily publisher.
- GitHub Actions for tests, migrations, frontend lint/build, and scheduled
  dry-run publishing.

## Tech Stack

| Area | Tools |
| --- | --- |
| Backend | FastAPI, SQLAlchemy, Pydantic |
| Database | PostgreSQL, Alembic |
| Frontend | React, Vite, TypeScript, React Router, Tailwind CSS |
| Email | Resend-compatible provider abstraction, dry-run by default |
| Jobs | Python CLI modules under `backend/app/jobs` |
| CI | GitHub Actions |
| Deployment target | Cloudflare Pages, Supabase Postgres, Render/Koyeb-style FastAPI service |

## Architecture

```text
frontend/                 React/Vite application
backend/app/api/          FastAPI route modules
backend/app/services/     Business logic and provider abstractions
backend/app/repositories/ SQLAlchemy database access
backend/app/models/       SQLAlchemy ORM models
backend/app/schemas/      Pydantic request/response schemas
backend/app/jobs/         CLI entrypoints for operational workflows
backend/migrations/       Alembic migration history
.github/workflows/        CI and scheduled dry-run publisher
```

Core data flow:

```text
RSS feeds
  -> ArticleService
  -> ArticleRepository
  -> PostgreSQL
  -> IssueService
  -> /issues APIs
  -> React frontend

Subscribers + issue
  -> EmailService
  -> email renderer/provider
  -> delivery records

Score provider
  -> ScoreService
  -> ScoreRepository
  -> /matches APIs
  -> React match centre
```

## What Works

Public product flows:

- View latest Daily Yorker briefing on the homepage.
- Browse the Daily Yorker archive.
- Open a dated Daily Yorker issue.
- View live, upcoming, and recent mock cricket matches.
- Subscribe by email.
- Unsubscribe through a no-login token link.

Admin and operational flows:

- Fetch RSS news through a protected admin route or CLI job.
- Generate or replace today's Daily Yorker.
- Sync mock score data idempotently.
- Preview the latest Daily Yorker email.
- Dry-run newsletter delivery without sending real email.

All `/admin` routes require:

```text
X-Admin-API-Key: your-admin-key
```

## Intentional Limits

- Scores are mock/provider-neutral data, not a real cricket data feed.
- Email delivery is safe by default. Local, CI, and scheduled workflows use
  dry-run mode and do not require `RESEND_API_KEY`.
- RAG and LLM-generated insights are intentionally not implemented.
- There are no user accounts, paid subscriptions, betting features, or
  ball-by-ball score models.
- Deployment configuration is documented and prepared, but this repository does
  not include credentials and does not claim that a live deployment exists.

## Local Setup

Copy backend environment defaults:

```bash
cp backend/.env.example backend/.env
```

Minimum local backend environment:

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

Start PostgreSQL:

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

The Docker stack is also available:

```bash
ADMIN_API_KEY=replace-me docker compose up --build
```

Docker frontend: `http://127.0.0.1:8080`

## Demo Workflow

Set an admin key for local API calls:

```bash
export OUTSIDE_EDGE_ADMIN_KEY=replace-with-your-admin-key
```

Fetch news:

```bash
curl -X POST http://127.0.0.1:8000/admin/fetch-news \
  -H "X-Admin-API-Key: $OUTSIDE_EDGE_ADMIN_KEY"
```

Generate today's Daily Yorker:

```bash
curl -X POST http://127.0.0.1:8000/admin/generate-issue \
  -H "X-Admin-API-Key: $OUTSIDE_EDGE_ADMIN_KEY"
```

Seed mock scores:

```bash
curl -X POST http://127.0.0.1:8000/admin/sync-scores \
  -H "X-Admin-API-Key: $OUTSIDE_EDGE_ADMIN_KEY"
```

Preview the latest newsletter:

```bash
curl -X POST http://127.0.0.1:8000/admin/email/preview-latest \
  -H "X-Admin-API-Key: $OUTSIDE_EDGE_ADMIN_KEY"
```

Run the daily publisher safely from the CLI:

```bash
cd backend
venv/bin/python -m app.jobs.publish_daily_yorker --dry-run
```

The publisher fetches news, generates or replaces today's issue, preserves
delivery history, renders the email, and reports fetched/saved/sent/skipped
counts. `--send` exists, but real delivery still requires all safeguards:

1. `EMAIL_DRY_RUN=false`
2. a valid `RESEND_API_KEY`
3. the command or route using `dry_run=false` / `--send`

## API Surface

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

Selected protected endpoints:

- `POST /admin/fetch-news`
- `POST /admin/generate-issue`
- `POST /admin/sync-scores`
- `POST /admin/email/preview-latest`
- `POST /admin/email/send-latest?dry_run=true`
- `POST /admin/email/send-issue/{issue_date}?dry_run=true`

## Tests And Quality

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
frontend build on pushes and pull requests.

## Deployment Notes

Prepared low-cost topology:

- Frontend: Cloudflare Pages.
- Database: Supabase Postgres.
- Backend: standalone FastAPI web service on Render or Koyeb.
- Scheduler: GitHub Actions.
- Email: dry-run only until explicitly enabled.

Backend environment variables:

```env
DATABASE_URL=postgres://postgres.project-ref:password@aws-region.pooler.supabase.com:5432/postgres
DATABASE_SSLMODE=require
ADMIN_API_KEY=long-random-secret
CORS_ORIGINS=https://your-project.pages.dev,https://your-custom-domain.example
SCORE_STALE_AFTER_MINUTES=5
EMAIL_FROM=Outside Edge <newsletter@example.com>
PUBLIC_SITE_URL=https://your-project.pages.dev
EMAIL_REPLY_TO=
EMAIL_DRY_RUN=true
RESEND_API_KEY=
```

Frontend environment variable:

```env
VITE_API_BASE_URL=https://your-backend.example.com
```

Cloudflare Pages settings:

- Root directory: `frontend`
- Build command: `npm ci && npm run build`
- Output directory: `dist`
- Node version: `22`

Render/Koyeb-style backend settings:

- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health check path: `/health`

`render.yaml` remains as optional Render configuration, but the preferred
database is Supabase and the preferred scheduled publisher is GitHub Actions.
