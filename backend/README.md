# Backend

## Run locally
1. `cp .env.example .env`
2. `uv sync`
3. `uv run alembic upgrade head`
4. `uv run uvicorn app.main:app --reload`

## Run tests
- `uv run pytest`
