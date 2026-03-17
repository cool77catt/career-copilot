# Backend

## Run locally
1. `cp .env.example .env`
2. `uv sync`
3. `uv run alembic upgrade head`
4. `uv run uvicorn app.main:app --reload`

## Profile report agent env
- Set `OPENAI_API_KEY` to enable profile report generation.
- Optional: set `OPENAI_PROFILE_AGENT_MODEL` (default: `gpt-4.1-mini`).

## Resume builder phase A env
- `OPENAI_API_KEY`
- Optional model overrides:
  - `OPENAI_RESUME_BUILDER_JD_MODEL`
  - `OPENAI_RESUME_BUILDER_ASSESSMENT_MODEL`
  - `OPENAI_RESUME_BUILDER_DOCX_MODEL`

## Resume builder phase A status
- Phase A only defines shared contracts, prompts, and model configuration.
- Script 1 (job description normalization) is implemented.
- Scripts 2 and 3 are not implemented yet.

## Run resume builder script 1
- `uv run python -m app.agents.resume_builder.jd_to_markdown_cli --input-file ../tmp/job-description.txt --output-path ../tmp/job-description.md`

## Run profile report agent from CLI
- `uv run python -m app.agents.profile_report_agent.cli --user-id 1`

## Run tests
- `uv run pytest`
