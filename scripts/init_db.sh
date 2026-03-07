#!/usr/bin/env bash
set -euo pipefail

POSTGRES_USER=${POSTGRES_USER:-postgres}
POSTGRES_DB=${POSTGRES_DB:-job_finder}

# Ensure db container is up

docker compose up -d db

for _ in {1..60}; do
  if docker compose exec -T db pg_isready -U "$POSTGRES_USER" -d postgres >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if [[ ! "$POSTGRES_DB" =~ ^[a-zA-Z0-9_]+$ ]]; then
  echo "Invalid POSTGRES_DB value: '$POSTGRES_DB'" >&2
  exit 1
fi

DB_EXISTS=$(docker compose exec -T db psql -U "$POSTGRES_USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='${POSTGRES_DB}'")

if [[ "$DB_EXISTS" != "1" ]]; then
  docker compose exec -T db psql -U "$POSTGRES_USER" -d postgres -v ON_ERROR_STOP=1 -c "CREATE DATABASE \"${POSTGRES_DB}\";"
fi

echo "Database '${POSTGRES_DB}' is ready."
