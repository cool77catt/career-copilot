from __future__ import annotations

from pathlib import Path

from app.agents.resume_builder.assessment_agent import ResumeAssessmentAgent
from app.agents.resume_builder.contracts import ResumeMarkdownGenerateRequest, ResumeMarkdownGenerateResult


def run_resume_assessment_and_write_outputs(
    request: ResumeMarkdownGenerateRequest,
    *,
    output_json_path: str,
    output_resume_markdown_path: str,
    agent: ResumeAssessmentAgent | None = None,
) -> ResumeMarkdownGenerateResult:
    json_path = Path(output_json_path)
    resume_path = Path(output_resume_markdown_path)
    for path in (json_path, resume_path):
        if path.exists() and path.is_dir():
            raise ValueError(f"Output path points to a directory: {path}")

    agent_instance = agent or ResumeAssessmentAgent()
    result = agent_instance.generate_assessment(request)

    json_path.parent.mkdir(parents=True, exist_ok=True)
    resume_path.parent.mkdir(parents=True, exist_ok=True)

    json_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    resume_path.write_text(result.resume_markdown, encoding="utf-8")
    return result
