#!/usr/bin/env bash
set -euo pipefail

cd backend
uv sync --group dev
uv run pytest -q
