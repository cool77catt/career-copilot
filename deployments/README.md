# Deployments

## Database Initialization
The backend expects a Postgres database named `job_finder`.

If your Postgres volume was previously created without that database, you can hit:
`FATAL: database "job_finder" does not exist`.

Use the idempotent initializer:

```bash
./scripts/init_db.sh
```

This command:
1. Starts the `db` service
2. Waits for Postgres readiness
3. Creates `job_finder` if missing

## Typical Local Bring-up
```bash
./scripts/setup_env.sh
./scripts/init_local_db.sh
cd backend && uv sync --group dev && uv run alembic upgrade head
cd ../frontend && pnpm install
```

## Docker DB Bring-up (optional)
```bash
./scripts/setup_env.sh
./scripts/init_db.sh
cd backend && uv sync --group dev && uv run alembic upgrade head
cd ../frontend && pnpm install
```

## If you want a full DB reset
```bash
docker compose down -v
./scripts/init_db.sh
```
