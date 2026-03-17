from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings


@dataclass(frozen=True)
class ResumeBuilderModelRegistry:
    job_description_model: str
    assessment_model: str
    docx_model: str

    @classmethod
    def from_settings(cls) -> "ResumeBuilderModelRegistry":
        return cls(
            job_description_model=settings.openai_resume_builder_jd_model,
            assessment_model=settings.openai_resume_builder_assessment_model,
            docx_model=settings.openai_resume_builder_docx_model,
        )
