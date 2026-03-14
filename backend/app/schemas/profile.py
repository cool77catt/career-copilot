from datetime import datetime

from pydantic import BaseModel, Field


class ProfileResponse(BaseModel):
    profile_markdown_path: str
    section_markdown_paths: dict[str, str]
    profile_report_latest_path: str | None = None
    profile_report_revision_paths: list[str] = Field(default_factory=list)
    content: str
    follow_up_questions: list[str]
    follow_up_answers: dict[str, str]
    additional_information: str
    has_linkedin_profile: bool
    has_resume: bool
    updated_at: datetime | None = None
