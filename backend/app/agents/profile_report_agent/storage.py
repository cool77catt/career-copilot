from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from app.profile_service import build_profile_directory, write_profile_markdown

LATEST_REPORT_FILENAME = "profile-report-latest.md"


def build_profile_report_directory(user_id: int) -> Path:
    return build_profile_directory(user_id) / "profile-report-revisions"


def latest_profile_report_path(user_id: int) -> str | None:
    latest_path = build_profile_report_directory(user_id) / LATEST_REPORT_FILENAME
    if latest_path.exists():
        return str(latest_path)
    return None


def list_profile_report_revisions(user_id: int) -> list[str]:
    report_dir = build_profile_report_directory(user_id)
    if not report_dir.exists():
        return []

    revisions = sorted(
        (
            path
            for path in report_dir.glob("profile-report-*.md")
            if path.name != LATEST_REPORT_FILENAME
        ),
        key=lambda path: path.name,
        reverse=True,
    )
    return [str(path) for path in revisions]


def save_profile_report_revision(user_id: int, markdown_content: str) -> tuple[str, str]:
    generated_at = datetime.now(timezone.utc)
    timestamp = generated_at.strftime("%Y%m%d-%H%M%S-%f")

    report_dir = build_profile_report_directory(user_id)
    report_dir.mkdir(parents=True, exist_ok=True)

    revision_path = report_dir / f"profile-report-{timestamp}.md"
    latest_path = report_dir / LATEST_REPORT_FILENAME

    rendered_markdown = (
        f"<!-- generated_at: {generated_at.isoformat()} -->\n\n"
        "# Profile Report\n\n"
        f"{markdown_content.strip()}\n"
    )

    write_profile_markdown(str(revision_path), rendered_markdown)
    write_profile_markdown(str(latest_path), rendered_markdown)

    return str(revision_path), str(latest_path)
