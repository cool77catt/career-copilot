from __future__ import annotations

import logging
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.agents.profile_report_agent.agent import ProfileReportAgent, ProfileReportAgentInput
from app.agents.profile_report_agent.storage import (
    latest_profile_report_path,
    list_profile_report_revisions,
    save_profile_report_revision,
)
from app.db.profile_repository import get_profile_by_user_id
from app.profile_service import read_follow_up_answers, read_section_markdown

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ProfileReportRunResult:
    user_id: int
    revision_path: str
    latest_path: str
    markdown_content: str


def generate_profile_report_for_user(db: Session, user_id: int) -> ProfileReportRunResult | None:
    profile = get_profile_by_user_id(db, user_id)
    if profile is None:
        return None

    linkedin_profile = read_section_markdown(profile.linkedin_markdown_path)
    resume = read_section_markdown(profile.resume_markdown_path)
    additional_information = read_section_markdown(profile.additional_info_markdown_path)
    follow_up_answers = read_follow_up_answers(profile.follow_up_markdown_path)

    agent_input = ProfileReportAgentInput(
        linkedin_profile=linkedin_profile,
        resume=resume,
        additional_information=additional_information,
        follow_up_answers=follow_up_answers,
    )
    markdown = ProfileReportAgent().generate_report(agent_input)
    revision_path, latest_path = save_profile_report_revision(user_id, markdown)

    return ProfileReportRunResult(
        user_id=user_id,
        revision_path=revision_path,
        latest_path=latest_path,
        markdown_content=markdown,
    )


def generate_profile_report_for_user_safe(db: Session, user_id: int) -> ProfileReportRunResult | None:
    try:
        return generate_profile_report_for_user(db, user_id)
    except Exception:
        logger.exception("Profile report agent failed", extra={"user_id": user_id})
        return None


def get_profile_report_history(user_id: int) -> tuple[str | None, list[str]]:
    return latest_profile_report_path(user_id), list_profile_report_revisions(user_id)
