# Outside Edge

Outside Edge is an ad-free cricket intelligence site built around RSS news
ingestion and the Daily Yorker briefing.

## Local stack

The complete stack can run with Docker:

```bash
ADMIN_API_KEY=replace-me docker compose up --build
```

- Frontend: `http://127.0.0.1:8080`
- API and OpenAPI docs: `http://127.0.0.1:8000/docs`
- PostgreSQL: `localhost:5432`

For local development without containers, copy `backend/.env.example` to
`backend/.env`, install `backend/requirements.txt`, and run:

```bash
cd backend
alembic upgrade head
uvicorn app.main:app --reload
```

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend requires Node.js 20.19 or newer. Set `VITE_API_BASE_URL` when the
API is not available at `http://127.0.0.1:8000`.

## Daily briefing workflow

With PostgreSQL, the backend, and the frontend running, use the configured admin
key to prepare today's Daily Yorker:

```bash
export OUTSIDE_EDGE_ADMIN_KEY=replace-with-your-admin-key

curl -X POST http://127.0.0.1:8000/admin/fetch-news \
  -H "X-Admin-API-Key: $OUTSIDE_EDGE_ADMIN_KEY"

curl -X POST http://127.0.0.1:8000/admin/generate-issue \
  -H "X-Admin-API-Key: $OUTSIDE_EDGE_ADMIN_KEY"
```

The first request fetches RSS entries and safely stores new articles. The second
generates or replaces today's published issue from the stored articles.

Open the product views at:

- Homepage: `http://127.0.0.1:5173/`
- Archive: `http://127.0.0.1:5173/daily-yorker`
- Dated issue: `http://127.0.0.1:5173/daily-yorker/YYYY-MM-DD`

Use today's date in ISO format for the issue generated above. The Docker
frontend exposes the same paths at `http://127.0.0.1:8080`.

## Mock match scores

Milestone 2 uses a small provider-neutral mock feed. Seed or refresh it through
the protected admin endpoint:

```bash
curl -X POST http://127.0.0.1:8000/admin/sync-scores \
  -H "X-Admin-API-Key: $OUTSIDE_EDGE_ADMIN_KEY"
```

Read the live match API:

```bash
curl http://127.0.0.1:8000/matches/live
```

The full match centre is available at `http://127.0.0.1:5173/matches`, or at
`http://127.0.0.1:8080/matches` when using Docker. Repeating the sync updates
the same mock records without duplicating matches or identical snapshots.
`SCORE_STALE_AFTER_MINUTES` controls the live-score freshness threshold and
defaults to five minutes.

## Daily Yorker email delivery

Configure the canonical sender and public site URL:

```env
EMAIL_FROM=Outside Edge <newsletter@example.com>
PUBLIC_SITE_URL=https://outside-edge.example
EMAIL_REPLY_TO=editor@example.com
EMAIL_DRY_RUN=true
RESEND_API_KEY=
```

`EMAIL_FROM` and `PUBLIC_SITE_URL` are required. `EMAIL_REPLY_TO` is optional.
Keep `EMAIL_DRY_RUN=true` for local development. `RESEND_API_KEY` is only
required when real delivery is enabled.

Preview the latest published issue without creating deliveries or contacting
Resend:

```bash
curl -X POST http://127.0.0.1:8000/admin/email/preview-latest \
  -H "X-Admin-API-Key: $OUTSIDE_EDGE_ADMIN_KEY"
```

Run the full recipient selection and duplicate checks in dry-run mode:

```bash
curl -X POST \
  "http://127.0.0.1:8000/admin/email/send-latest?dry_run=true" \
  -H "X-Admin-API-Key: $OUTSIDE_EDGE_ADMIN_KEY"
```

To send a specific published issue, use:

```bash
curl -X POST \
  "http://127.0.0.1:8000/admin/email/send-issue/YYYY-MM-DD?dry_run=true" \
  -H "X-Admin-API-Key: $OUTSIDE_EDGE_ADMIN_KEY"
```

Real delivery requires all three safeguards:

1. Set `EMAIL_DRY_RUN=false`.
2. Configure a valid `RESEND_API_KEY`.
3. Call a send route with `dry_run=false`.

```bash
curl -X POST \
  "http://127.0.0.1:8000/admin/email/send-latest?dry_run=false" \
  -H "X-Admin-API-Key: $OUTSIDE_EDGE_ADMIN_KEY"
```

Successful issue/subscriber deliveries are not repeated unless `force=true` is
explicitly supplied. Provider failures are recorded per recipient and do not
stop the remainder of the batch.

Every email contains a no-login unsubscribe link. Opening it with `GET` shows a
confirmation page without changing subscription state. Confirming performs an
idempotent `POST` and marks the subscriber inactive. Submitting the public
signup form again explicitly reactivates that subscriber.

## Database migrations

Alembic is the only production schema authority. New databases should run:

```bash
cd backend
alembic upgrade head
```

For a database created by the pre-Alembic application, mark the existing schema
as the baseline before applying the normalized URL migration:

```bash
alembic stamp 20260709_0001
alembic upgrade head
```

## Admin API

Every `/admin` route requires the configured key:

```text
X-Admin-API-Key: your-admin-key
```

`DATABASE_URL` and `ADMIN_API_KEY` are required at startup. `CORS_ORIGINS` is a
comma-separated list and defaults to the local Vite origins.

## Checks

```bash
cd backend
python -m pytest -q

cd frontend
npm run lint
npm run build
```
