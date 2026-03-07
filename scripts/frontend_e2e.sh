#!/usr/bin/env bash
set -euo pipefail

cd frontend
unset ELECTRON_RUN_AS_NODE
pnpm install --config.confirmModulesPurge=false
pnpm exec cypress install
pnpm dev --hostname 127.0.0.1 --port 3000 >/tmp/job-finder-frontend.log 2>&1 &
FRONTEND_PID=$!

cleanup() {
  kill "$FRONTEND_PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT

for _ in {1..40}; do
  if curl -sSf http://127.0.0.1:3000 >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if ! curl -sSf http://127.0.0.1:3000 >/dev/null 2>&1; then
  cat /tmp/job-finder-frontend.log
  exit 1
fi

pnpm exec cypress run --headless
