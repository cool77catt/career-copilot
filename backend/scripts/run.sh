#!/usr/bin/env bash
set -euo pipefail

uv run python scripts/init_db.py
uv run alembic upgrade head
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
