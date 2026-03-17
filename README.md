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

Phase 2 now includes:
- Unified profile update API (`POST /profile/update`) for LinkedIn PDF, resume PDF, follow-up answers, and additional information
- Profile retrieval API (`GET /profile`) returning current `profile.md`, section markdown paths, follow-up Q/A, and metadata
- Flat-file profile persistence at `PROFILE_STORAGE_DIR/user-{id}/profile.md` with DB linkage via `user_profiles`
- Section markdown persistence for agent workflows:
  - `PROFILE_STORAGE_DIR/user-{id}/linkedin-profile.md`
  - `PROFILE_STORAGE_DIR/user-{id}/resume.md`
  - `PROFILE_STORAGE_DIR/user-{id}/follow-up-answers.md`
  - `PROFILE_STORAGE_DIR/user-{id}/additional-information.md`
- Profile report agent workflow:
  - `POST /profile/update` triggers an OpenAI-backed agent run in the background
  - Revisioned report outputs are stored at `PROFILE_STORAGE_DIR/user-{id}/profile-report-revisions/profile-report-<timestamp>.md`
  - Latest report pointer is stored at `PROFILE_STORAGE_DIR/user-{id}/profile-report-revisions/profile-report-latest.md`
- Frontend Profile Builder panel with 4 labeled sections, single `Update Profile` action, and raw/rendered markdown tabs

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

Optional for profile report agent runs:
```bash
cd backend
export OPENAI_API_KEY=<your-key>
# optional override:
# export OPENAI_PROFILE_AGENT_MODEL=gpt-4.1-mini
# export OPENAI_RESUME_BUILDER_JD_MODEL=gpt-4.1-mini
# export OPENAI_RESUME_BUILDER_ASSESSMENT_MODEL=gpt-4.1-mini
# export OPENAI_RESUME_BUILDER_DOCX_MODEL=gpt-4.1-mini
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

Run profile report agent directly from CLI:
```bash
./scripts/run_profile_report_agent.sh --user-id 1
```

Run resume builder script 1 directly from CLI:
```bash
./scripts/run_resume_builder_jd_normalizer.sh --input-file ../tmp/job-description.txt --output-path ../tmp/job-description.md
```

Run resume builder script 2 directly from CLI:
```bash
./scripts/run_resume_builder_assessment.sh --job-description-file ../tmp/job-description.md --user-profile-file ../tmp/profile.md --current-resume-file ../tmp/resume.md --linkedin-file ../tmp/linkedin.md --qa-json-file ../tmp/qa.json --constraints-json-file ../tmp/constraints.json --output-json-path ../tmp/assessment.json --output-resume-markdown-path ../tmp/tailored-resume.md
```

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
