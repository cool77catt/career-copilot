#!/usr/bin/env bash
set -euo pipefail

cd backend
env UV_CACHE_DIR=/tmp/uv-cache uv run python -m app.agents.resume_builder.resume_source_to_markdown_cli "$@"
