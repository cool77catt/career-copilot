import os

import psycopg
from psycopg import sql
from sqlalchemy.engine import make_url


def to_psycopg_dsn(database_url: str, database: str) -> str:
    url = make_url(database_url)
    admin_url = url.set(database=database)
    dsn = admin_url.render_as_string(hide_password=False)
    if dsn.startswith("postgresql+psycopg://"):
        return dsn.replace("postgresql+psycopg://", "postgresql://", 1)
    return dsn


def main() -> None:
    database_url = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/job_finder")
    url = make_url(database_url)

    if not url.drivername.startswith("postgresql"):
        print("Skipping DB init: non-Postgres DATABASE_URL")
        return

    target_db = url.database
    if not target_db:
        raise RuntimeError("DATABASE_URL is missing database name")

    admin_db = os.getenv("POSTGRES_ADMIN_DB", "postgres")
    admin_dsn = to_psycopg_dsn(database_url, admin_db)

    with psycopg.connect(admin_dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_db,))
            exists = cur.fetchone() is not None
            if exists:
                print(f"Database '{target_db}' already exists")
                return

            cur.execute(sql.SQL("CREATE DATABASE {} ").format(sql.Identifier(target_db)))
            print(f"Created database '{target_db}'")


if __name__ == "__main__":
    main()
