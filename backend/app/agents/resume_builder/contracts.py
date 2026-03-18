from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class QuestionAnswer(BaseModel):
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)


class ResumeSourceToMarkdownRequest(BaseModel):
    input_resume_path: str = Field(min_length=1)
    output_markdown_path: str = Field(min_length=1)


class ResumeSourceToMarkdownResult(BaseModel):
    input_resume_path: str = Field(min_length=1)
    output_markdown_path: str = Field(min_length=1)
    source_format: Literal["pdf", "docx"]
    markdown_content: str = Field(min_length=1)


class JobDescriptionNormalizeRequest(BaseModel):
    raw_text: str = Field(min_length=1)
    output_markdown_path: str = Field(min_length=1)


class JobDescriptionNormalizeResult(BaseModel):
    output_markdown_path: str = Field(min_length=1)
    markdown_content: str = Field(min_length=1)


class ResumeConstraintSet(BaseModel):
    section_order: list[str] = Field(default_factory=list)
    max_pages: int | None = Field(default=None, ge=1)
    tone: str | None = None
    required_inclusions: list[str] = Field(default_factory=list)
    prohibited_claims: list[str] = Field(default_factory=list)
    exclusion_rules: list[str] = Field(default_factory=list)
    additional_instructions: list[str] = Field(default_factory=list)


class FitAssessment(BaseModel):
    percentage_fit: int = Field(ge=0, le=100)
    summary: str = Field(min_length=1)
    confirmed_strengths: list[str] = Field(default_factory=list)
    inferred_strengths: list[str] = Field(default_factory=list)


class GapItem(BaseModel):
    gap_type: Literal["hard_gap", "clarifiable_gap", "weak_evidence"]
    requirement: str = Field(min_length=1)
    details: str = Field(min_length=1)
    impact: str = Field(min_length=1)
    evidence_status: str = Field(min_length=1)
    follow_up_hint: str | None = None


class GapAssessment(BaseModel):
    summary: str = Field(min_length=1)
    hard_gaps: list[GapItem] = Field(default_factory=list)
    clarifiable_gaps: list[GapItem] = Field(default_factory=list)
    weak_evidence_areas: list[GapItem] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_gap_buckets(self) -> "GapAssessment":
        for gap in self.hard_gaps:
            if gap.gap_type != "hard_gap":
                raise ValueError("Items in hard_gaps must use gap_type='hard_gap'.")
        for gap in self.clarifiable_gaps:
            if gap.gap_type != "clarifiable_gap":
                raise ValueError("Items in clarifiable_gaps must use gap_type='clarifiable_gap'.")
        for gap in self.weak_evidence_areas:
            if gap.gap_type != "weak_evidence":
                raise ValueError("Items in weak_evidence_areas must use gap_type='weak_evidence'.")
        return self


class ClarifyingQuestion(BaseModel):
    question: str = Field(min_length=1)
    rationale: str = Field(min_length=1)
    target_gaps: list[str] = Field(default_factory=list)
    priority: Literal["high", "medium", "low"] = "medium"


class ResumeMarkdownGenerateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_description_markdown: str = Field(min_length=1)
    user_profile_markdown: str | None = None
    current_resume_markdown: str | None = None
    linkedin_markdown: str | None = None
    additional_context: str | None = None
    question_answers: list[QuestionAnswer] = Field(default_factory=list)
    constraints: ResumeConstraintSet = Field(default_factory=ResumeConstraintSet)

    @model_validator(mode="after")
    def validate_candidate_context(self) -> "ResumeMarkdownGenerateRequest":
        context_fields = [
            self.user_profile_markdown,
            self.current_resume_markdown,
            self.linkedin_markdown,
            self.additional_context,
        ]
        if not any(value and value.strip() for value in context_fields) and not self.question_answers:
            raise ValueError(
                "At least one candidate-context input is required: profile, resume, LinkedIn, "
                "additional context, or question_answers."
            )
        return self


class ResumeMarkdownGenerateResult(BaseModel):
    fit_assessment: FitAssessment
    gap_assessment: GapAssessment
    clarifying_questions: list[ClarifyingQuestion] = Field(default_factory=list)
    resume_markdown: str = Field(min_length=1)


class ResumeDocxRenderRequest(BaseModel):
    resume_markdown: str = Field(min_length=1)
    template_docx_path: str = Field(min_length=1)
    output_docx_path: str = Field(min_length=1)


class ResumeDocxRenderResult(BaseModel):
    output_docx_path: str = Field(min_length=1)
    template_docx_path: str = Field(min_length=1)
    formatting_notes: list[str] = Field(default_factory=list)
