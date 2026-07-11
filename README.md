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

The same workflow is available as production-safe CLI jobs. These commands reuse
the backend services and repositories directly; they do not call local HTTP
endpoints:

```bash
cd backend
python -m app.jobs.fetch_news
python -m app.jobs.generate_issue
python -m app.jobs.publish_daily_yorker --dry-run
```

`publish_daily_yorker --dry-run` fetches news, generates or replaces today's
issue, renders the latest issue email, and prints recipient counts without
sending real email. `publish_daily_yorker --send` attempts delivery but still
respects `EMAIL_DRY_RUN=true`, and successful deliveries are not repeated for
the same issue/subscriber.

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

## Local full-flow checklist

1. Start PostgreSQL:

   ```bash
   docker compose up postgres
   ```

2. Run migrations:

   ```bash
   cd backend
   alembic upgrade head
   ```

3. Start the API and frontend in separate terminals:

   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

   ```bash
   cd frontend
   npm run dev
   ```

4. Prepare local content:

   ```bash
   cd backend
   python -m app.jobs.fetch_news
   python -m app.jobs.generate_issue
   ```

5. Seed mock scores and inspect the product:

   ```bash
   curl -X POST http://127.0.0.1:8000/admin/sync-scores \
     -H "X-Admin-API-Key: $OUTSIDE_EDGE_ADMIN_KEY"
   ```

   Open `http://127.0.0.1:5173/`, `http://127.0.0.1:5173/matches`,
   `http://127.0.0.1:5173/daily-yorker`, and
   `http://127.0.0.1:5173/daily-yorker/YYYY-MM-DD`.

6. Preview and dry-run email:

   ```bash
   curl -X POST http://127.0.0.1:8000/admin/email/preview-latest \
     -H "X-Admin-API-Key: $OUTSIDE_EDGE_ADMIN_KEY"

   python -m app.jobs.publish_daily_yorker --dry-run
   ```

The dry-run publisher output includes fetched, saved, generated, would-send,
sent, skipped, and failed counts.

## Deployment on Render

This repository includes `render.yaml` for a Render Blueprint with:

- `outside-edge-api`: FastAPI web service.
- `outside-edge-web`: React/Vite static site.
- `outside-edge-db`: Render PostgreSQL database.
- `outside-edge-daily-yorker`: daily cron job.

Render service settings:

- Backend root directory: `backend`
- Backend build command: `pip install -r requirements.txt`
- Backend pre-deploy command: `alembic upgrade head`
- Backend start command:
  `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Backend health check path: `/health`
- Frontend root directory: `frontend`
- Frontend build command: `npm ci && npm run build`
- Frontend publish directory: `./dist`

Required backend environment variables:

- `DATABASE_URL`: set from the Render PostgreSQL connection string.
- `ADMIN_API_KEY`: dashboard-entered secret.
- `CORS_ORIGINS`: production frontend URL.
- `EMAIL_FROM`: clear Outside Edge sender identity.
- `PUBLIC_SITE_URL`: production frontend URL.
- `EMAIL_DRY_RUN`: keep `true` for first deploys.
- `RESEND_API_KEY`: dashboard-entered secret, only needed for real delivery.
- `EMAIL_REPLY_TO`: optional.
- `SCORE_STALE_AFTER_MINUTES`: optional, defaults to `5`.

Required frontend environment variable:

- `VITE_API_BASE_URL`: production backend URL.

The blueprint uses `https://outside-edge-api.onrender.com` and
`https://outside-edge-web.onrender.com` as default service URLs. If Render gives
the services different public URLs or you attach custom domains, update
`VITE_API_BASE_URL`, `CORS_ORIGINS`, and `PUBLIC_SITE_URL`.

The local Docker Compose service and volume names still use older `silly-point`
labels. They are local-only and can be cleaned up in a future maintenance pass.

## Daily publisher on Render

The default cron command in `render.yaml` is safe:

```bash
python -m app.jobs.publish_daily_yorker --dry-run
```

It is scheduled as `0 20 * * *`, which is 20:00 UTC. That corresponds to 07:00
in Melbourne during daylight saving time and 06:00 during standard time. Render
cron schedules use UTC, so adjust the cron expression if you want a different
local publishing time.

Expected dry-run output resembles:

```text
publish_daily_yorker mode=dry-run effective_dry_run=true fetched_count=...
saved_count=... issue_date=YYYY-MM-DD issue_id=... article_count=...
sections=Opening Spell=3, Powerplay=5, Around the Grounds=7
would_send_count=... sent_count=0 skipped_count=... failed_count=0
```

To send for real after verification, change the cron command to:

```bash
python -m app.jobs.publish_daily_yorker --send
```

Real delivery still requires `EMAIL_DRY_RUN=false` and a valid
`RESEND_API_KEY`. Duplicate-send protection prevents successful
issue/subscriber deliveries from being sent again if the cron is rerun.

After a cron run, verify:

- Render logs show the expected counts.
- Today's dated issue exists in the archive.
- Email preview renders with source links and the web issue link.
- Delivery counts match the active subscriber count.

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
alembic upgrade head
alembic check

cd frontend
npm run lint
npm run build
```

## Production email checklist

1. First deploy with `EMAIL_DRY_RUN=true`.
2. Run the daily cron as `--dry-run`.
3. Check Render logs for fetched/saved/generated/would-send counts.
4. Subscribe with your own email through the public form.
5. Preview the latest email with `/admin/email/preview-latest`.
6. Add `RESEND_API_KEY` in Render.
7. Set `EMAIL_DRY_RUN=false`.
8. Switch the cron command from `--dry-run` to `--send`.
9. Never commit `.env` or production secrets.
