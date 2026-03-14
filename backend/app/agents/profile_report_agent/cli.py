from __future__ import annotations

import click
from app.agents.profile_report_agent.runner import generate_profile_report_for_user
from app.db.session import SessionLocal


@click.command(help="Generate a revisioned markdown profile report for a user.")
@click.option("--user-id", type=int, required=True, help="User id to generate report for.")
@click.option("--print-report", is_flag=True, help="Print generated markdown content to stdout.")
@click.pass_context
def main(ctx: click.Context, user_id: int, print_report: bool) -> None:
    db = SessionLocal()
    try:
        result = generate_profile_report_for_user(db, user_id)
    except Exception as exc:
        click.echo(f"Profile report generation failed: {exc}", err=True)
        ctx.exit(1)
    finally:
        db.close()

    if result is None:
        click.echo(f"No profile found for user_id={user_id}", err=True)
        ctx.exit(2)

    click.echo(f"Generated profile report revision: {result.revision_path}")
    click.echo(f"Updated latest profile report: {result.latest_path}")

    if print_report:
        click.echo("\n--- Profile Report Markdown ---\n")
        click.echo(result.markdown_content)


if __name__ == "__main__":
    main()
