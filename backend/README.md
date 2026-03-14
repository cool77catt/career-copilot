# Backend

## Run locally
1. `cp .env.example .env`
2. `uv sync`
3. `uv run alembic upgrade head`
4. `uv run uvicorn app.main:app --reload`

## Profile report agent env
- Set `OPENAI_API_KEY` to enable profile report generation.
- Optional: set `OPENAI_PROFILE_AGENT_MODEL` (default: `gpt-4.1-mini`).

## Run profile report agent from CLI
- `uv run python -m app.agents.profile_report_agent.cli --user-id 1`

## Run tests
- `uv run pytest`
