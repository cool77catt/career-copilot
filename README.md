# Job Finder LLM

## Overview
Job Finder LLM is a full-stack app that helps users build a stronger profile, discover aligned jobs, and generate tailored application materials.

Deliverable 2 includes:
- FastAPI backend with JWT auth and seeded dev user
- Postgres integration + Alembic migration for `users`
- Dockerized backend runtime
- Next.js frontend workflow skeleton (no deep business logic yet)
- Login screen bypass via backend auto-login using seeded credentials
- Backend pytest suite
- Frontend Cypress E2E test

## Architecture
- `frontend/`: Next.js TypeScript UI skeleton
- `backend/`: FastAPI API + SQLAlchemy + Alembic
- `docker-compose.yml`: Postgres + backend services
- `scripts/`: setup/run/test helper scripts
- `docs/`: prompt/spec/plan docs

## Seeded Development User
- Name: Chris Carl
- Email: `chris77carl@gmail.com`
- Password: `default`

## Setup
1. Copy env files:
```bash
./scripts/setup_env.sh
```

2. Initialize **local Postgres** database (idempotent):
```bash
./scripts/init_local_db.sh
```

3. Install backend deps + migrate:
```bash
cd backend
uv sync --group dev
uv run alembic upgrade head
```

4. Install frontend deps:
```bash
cd frontend
pnpm install
```

## Running the App
Run backend:
```bash
cd backend
uv run uvicorn app.main:app --reload
```

Run frontend:
```bash
cd frontend
pnpm dev
```

Open `http://localhost:3000`.

## Testing
Backend tests:
```bash
./scripts/backend_test.sh
```

Frontend E2E (Cypress):
```bash
./scripts/frontend_e2e.sh
```

## Dockerized Backend
To run backend and db together:
```bash
./scripts/setup_env.sh
./scripts/init_db.sh
docker compose up --build
```

## Local vs Docker DB
- Local DB (default for day-to-day dev): `./scripts/init_local_db.sh`
- Docker DB (isolated/test env): `./scripts/init_db.sh`
- Full local bootstrap (recommended): `./scripts/dev_up_local.sh`
- Full bootstrap with Docker DB: `./scripts/dev_up_docker.sh`

## Troubleshooting: `FATAL: database \"job_finder\" does not exist`
This usually means your Postgres volume already existed and was initialized before `job_finder` was configured.

Fix for local Postgres without deleting data:
```bash
./scripts/init_local_db.sh
cd backend
uv run alembic upgrade head
```

If you are using Docker Postgres and want a full reset:
```bash
docker compose down -v
./scripts/init_db.sh
cd backend
uv run alembic upgrade head
```

Deployment-specific notes are in `deployments/README.md`.
