# Clipper.ai Frontend

React + Vite single-page experience inspired by the Clipper.ai design direction.

## Getting started

```bash
npm install
npm run dev
```

Set the backend API origin with `.env.local`:

```env
VITE_API_URL=http://localhost:8000
```

## Available scripts

- `npm run dev` – start Vite dev server on http://localhost:5173
- `npm run build` – type-check and build production assets
- `npm run preview` – preview production build locally

## Docker (development)

If you prefer to run the frontend in Docker (no local Node needed), there's a development override that mounts your source and runs Vite with hot reload.

Start only the frontend (builds image if needed):

```bash
docker compose up --build frontend
```

Or use the override for a dev workflow (this mounts your working tree and will run `npm ci` inside the container if dependencies are missing):

```bash
docker compose up --build
```

Access the app at http://localhost:5173. If file changes aren't detected on your host, the compose override sets `CHOKIDAR_USEPOLLING=1` to use polling.

## Stack

- React + TypeScript
- TailwindCSS with custom palette
- Framer Motion for subtle motion
- Radix UI dialog + Lucide icons
- TanStack Query + Axios for API integration
