# Outside Edge Frontend

React/Vite frontend for Outside Edge.

## Commands

```bash
npm install
npm run dev
npm run lint
npm run build
```

Copy `.env.example` to `.env.local` for local development:

```bash
cp .env.example .env.local
```

`VITE_API_BASE_URL` is required and should point at the FastAPI backend.

Cloudflare Pages uses:

- Root directory: `frontend`
- Build command: `npm ci && npm run build`
- Output directory: `dist`
- Environment variable: `VITE_API_BASE_URL=https://your-backend.example.com`

React Router deep links are handled by `public/_redirects`.
