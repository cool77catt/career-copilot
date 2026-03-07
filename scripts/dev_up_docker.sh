#!/usr/bin/env bash
set -euo pipefail

./scripts/setup_env.sh
./scripts/init_db.sh

(
  cd backend
  uv sync --group dev
  uv run alembic upgrade head
) &

(
  cd frontend
  pnpm install
) &

wait

echo "Docker DB setup complete."
echo "Run backend: (cd backend && uv run uvicorn app.main:app --reload)"
echo "Run frontend: (cd frontend && pnpm dev)"
