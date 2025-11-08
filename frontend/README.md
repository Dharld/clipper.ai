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

## Stack

- React + TypeScript
- TailwindCSS with custom palette
- Framer Motion for subtle motion
- Radix UI dialog + Lucide icons
- TanStack Query + Axios for API integration
