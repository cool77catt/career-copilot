#!/usr/bin/env bash
set -euo pipefail

cd backend
uv run python -m app.agents.profile_report_agent.cli "$@"
