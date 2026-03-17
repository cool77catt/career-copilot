from __future__ import annotations

from typing import Any

from openai import OpenAI

from app.agents.resume_builder.contracts import (
    QuestionAnswer,
    ResumeConstraintSet,
    ResumeMarkdownGenerateRequest,
    ResumeMarkdownGenerateResult,
)
from app.agents.resume_builder.prompts import ASSESS_AND_GENERATE_SYSTEM_PROMPT
from app.core.config import settings


class ResumeAssessmentAgentError(RuntimeError):
    """Raised when the resume assessment agent cannot complete successfully."""


class ResumeAssessmentAgent:
    def __init__(
        self,
        *,
        client: OpenAI | Any | None = None,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        resolved_api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_resume_builder_assessment_model
        if client is not None:
            self.client = client
            return
        if not resolved_api_key:
            raise ResumeAssessmentAgentError(
                "OPENAI_API_KEY is not configured. Set OPENAI_API_KEY before running the resume builder assessment agent."
            )
        self.client = OpenAI(api_key=resolved_api_key)

    def generate_assessment(self, request: ResumeMarkdownGenerateRequest) -> ResumeMarkdownGenerateResult:
        response = self.client.responses.parse(
            model=self.model,
            instructions=ASSESS_AND_GENERATE_SYSTEM_PROMPT,
            input=_render_user_prompt(request),
            text_format=ResumeMarkdownGenerateResult,
        )

        parsed = getattr(response, "output_parsed", None)
        if isinstance(parsed, ResumeMarkdownGenerateResult):
            return parsed

        raise ResumeAssessmentAgentError("OpenAI response did not parse into the expected resume assessment schema.")


def _render_user_prompt(request: ResumeMarkdownGenerateRequest) -> str:
    return (
        "Analyze candidate fit against the target job description and return the structured response schema.\n\n"
        "## Job Description Markdown\n"
        f"{request.job_description_markdown.strip()}\n\n"
        "## User Profile Markdown\n"
        f"{_optional_block(request.user_profile_markdown, 'No user profile markdown provided.')}\n\n"
        "## Current Resume Markdown\n"
        f"{_optional_block(request.current_resume_markdown, 'No current resume markdown provided.')}\n\n"
        "## LinkedIn Markdown\n"
        f"{_optional_block(request.linkedin_markdown, 'No LinkedIn markdown provided.')}\n\n"
        "## Additional Context\n"
        f"{_optional_block(request.additional_context, 'No additional context provided.')}\n\n"
        "## Question and Answer Context\n"
        f"{_render_question_answers(request.question_answers)}\n\n"
        "## Resume Constraints\n"
        f"{_render_constraints(request.constraints)}\n"
    )


def _optional_block(value: str | None, fallback: str) -> str:
    if value and value.strip():
        return value.strip()
    return fallback


def _render_question_answers(question_answers: list[QuestionAnswer]) -> str:
    if not question_answers:
        return "- No Q&A context provided."
    lines: list[str] = []
    for item in question_answers:
        lines.append(f"- Q: {item.question}")
        lines.append(f"  A: {item.answer}")
    return "\n".join(lines)


def _render_constraints(constraints: ResumeConstraintSet) -> str:
    sections = ", ".join(constraints.section_order) if constraints.section_order else "Not specified"
    required = ", ".join(constraints.required_inclusions) if constraints.required_inclusions else "None"
    prohibited = ", ".join(constraints.prohibited_claims) if constraints.prohibited_claims else "None"
    exclusions = ", ".join(constraints.exclusion_rules) if constraints.exclusion_rules else "None"
    additional = "; ".join(constraints.additional_instructions) if constraints.additional_instructions else "None"

    return (
        f"- Section order: {sections}\n"
        f"- Max pages: {constraints.max_pages if constraints.max_pages is not None else 'Not specified'}\n"
        f"- Tone: {constraints.tone or 'Not specified'}\n"
        f"- Required inclusions: {required}\n"
        f"- Prohibited claims: {prohibited}\n"
        f"- Exclusion rules: {exclusions}\n"
        f"- Additional instructions: {additional}"
    )
