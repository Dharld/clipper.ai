Clipper — Backend scaffold

This repository contains a minimal scaffold for the Clipper backend using:

- FastAPI
- SQLAlchemy + Alembic (migrations scaffolded)
- Dramatiq + Redis for background tasks
- PostgreSQL for the database (Docker Compose)
- MinIO as a local S3-compatible storage for development
- FFmpeg (installed in Docker image) for audio extraction

What I created:

- `app/` — FastAPI application and routes
- `app/models.py` — SQLAlchemy models (projects, clips, transcripts, silence_maps, assets)
- `app/db.py` — DB engine and session
- `app/tasks.py` — Dramatiq tasks (toy worker logic)
- `Dockerfile` — image used by `api` and `worker`
- `docker-compose.yml` — services: api, worker, redis, postgres, minio
- `requirements.txt` — Python dependencies
- `alembic/` — minimal Alembic scaffolding

Purpose of Docker Compose
-------------------------
Docker Compose lets you define and run multiple containers (services) that make up your application in a single YAML file. For this project the Compose file starts:

- `api` — the FastAPI server
- `worker` — a separate process that runs Dramatiq to consume tasks from Redis
- `postgres` — Postgres DB used by the app
- `redis` — Redis used by Dramatiq
- `minio` — S3-compatible storage for local development

Using Compose gives a reproducible development environment with one command:

```powershell
docker compose up --build
```

This will build the app image, start redis/postgres/minio, and run both the API and worker processes.

Quick test (after building):

1. Start compose: `docker compose up --build`
2. Hit the health endpoint: `http://localhost:8000/health`
3. Enqueue a toy job: POST to `http://localhost:8000/jobs/enqueue` with JSON `{ "project_id": "prj_test" }`
4. Watch the worker logs — it will pick up the job and update the DB status.

Notes and next steps
- Fill in production config for S3 (MinIO is for dev only).
- Add Alembic migrations and run them: `alembic upgrade head` (inside container or locally after configuring DB URL).
- Replace toy worker logic with the real pipeline (ffmpeg, Whisper API, Chat Completions).
