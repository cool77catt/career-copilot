import click
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


@click.command()
@click.option(
    "--database-url",
    envvar="DATABASE_URL",
    default="postgresql+psycopg://postgres:postgres@localhost:5432/job_finder",
    show_default=True,
    help="SQLAlchemy DATABASE_URL used to derive target database.",
)
@click.option(
    "--postgres-admin-db",
    envvar="POSTGRES_ADMIN_DB",
    default="postgres",
    show_default=True,
    help="Admin database used to create the target DB if missing.",
)
def main(database_url: str, postgres_admin_db: str) -> None:
    url = make_url(database_url)

    if not url.drivername.startswith("postgresql"):
        click.echo("Skipping DB init: non-Postgres DATABASE_URL")
        return

    target_db = url.database
    if not target_db:
        raise click.ClickException("DATABASE_URL is missing database name")

    admin_dsn = to_psycopg_dsn(database_url, postgres_admin_db)

    with psycopg.connect(admin_dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_db,))
            exists = cur.fetchone() is not None
            if exists:
                click.echo(f"Database '{target_db}' already exists")
                return

            cur.execute(sql.SQL("CREATE DATABASE {} ").format(sql.Identifier(target_db)))
            click.echo(f"Created database '{target_db}'")


if __name__ == "__main__":
    main()
