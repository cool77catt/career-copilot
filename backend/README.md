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
  - `OPENAI_RESUME_BUILDER_RESUME_IMPORT_MODEL`
  - `OPENAI_RESUME_BUILDER_JD_MODEL`
  - `OPENAI_RESUME_BUILDER_ASSESSMENT_MODEL`
  - `OPENAI_RESUME_BUILDER_DOCX_MODEL`

## Resume builder phase A status
- Resume import script (`.pdf`/`.docx` -> markdown) is implemented.
- Phase A defines shared contracts, prompts, and model configuration.
- Script 1 (job description normalization) is implemented.
- Script 2 (fit assessment + tailored resume markdown) is implemented.
- Script 3 (markdown-to-docx rendering) is implemented as a deterministic template renderer.

## Run resume builder resume import script
- `uv run python -m app.agents.resume_builder.resume_source_to_markdown_cli --input-resume-file ../tmp/resume.docx --output-markdown-path ../tmp/resume.md`

## Run resume builder script 1
- `uv run python -m app.agents.resume_builder.jd_to_markdown_cli --input-file ../tmp/job-description.txt --output-path ../tmp/job-description.md`

## Run resume builder script 2
- `uv run python -m app.agents.resume_builder.assessment_cli --job-description-file ../tmp/job-description.md --user-profile-file ../tmp/profile.md --current-resume-file ../tmp/resume.md --linkedin-file ../tmp/linkedin.md --qa-json-file ../tmp/qa.json --constraints-json-file ../tmp/constraints.json --output-json-path ../tmp/assessment.json --output-resume-markdown-path ../tmp/tailored-resume.md`

## Run resume builder script 3
- `uv run python -m app.agents.resume_builder.render_docx_cli --resume-markdown-file ../tmp/tailored-resume.md --template-docx-file ../tmp/template.docx --output-docx-path ../tmp/tailored-resume.docx`

## Run profile report agent from CLI
- `uv run python -m app.agents.profile_report_agent.cli --user-id 1`

## Run tests
- `uv run pytest`
