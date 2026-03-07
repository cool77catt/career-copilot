#!/usr/bin/env bash
set -euo pipefail

POSTGRES_HOST=${POSTGRES_HOST:-localhost}
POSTGRES_PORT=${POSTGRES_PORT:-5432}
POSTGRES_USER=${POSTGRES_USER:-postgres}
POSTGRES_DB=${POSTGRES_DB:-job_finder}
POSTGRES_ADMIN_DB=${POSTGRES_ADMIN_DB:-postgres}

if [[ ! "$POSTGRES_DB" =~ ^[a-zA-Z0-9_]+$ ]]; then
  echo "Invalid POSTGRES_DB value: '$POSTGRES_DB'" >&2
  exit 1
fi

DB_EXISTS=$(psql \
  -h "$POSTGRES_HOST" \
  -p "$POSTGRES_PORT" \
  -U "$POSTGRES_USER" \
  -d "$POSTGRES_ADMIN_DB" \
  -tAc "SELECT 1 FROM pg_database WHERE datname='${POSTGRES_DB}'")

if [[ "$DB_EXISTS" != "1" ]]; then
  psql \
    -h "$POSTGRES_HOST" \
    -p "$POSTGRES_PORT" \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_ADMIN_DB" \
    -v ON_ERROR_STOP=1 \
    -c "CREATE DATABASE \"${POSTGRES_DB}\";"
fi

echo "Local database '${POSTGRES_DB}' is ready on ${POSTGRES_HOST}:${POSTGRES_PORT}."
