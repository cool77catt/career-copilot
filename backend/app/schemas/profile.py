from datetime import datetime

from pydantic import BaseModel


class ProfileResponse(BaseModel):
    profile_markdown_path: str
    section_markdown_paths: dict[str, str]
    content: str
    follow_up_questions: list[str]
    follow_up_answers: dict[str, str]
    additional_information: str
    has_linkedin_profile: bool
    has_resume: bool
    updated_at: datetime | None = None
