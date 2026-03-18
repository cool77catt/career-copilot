from __future__ import annotations

from pathlib import Path

from app.agents.resume_builder.contracts import ResumeSourceToMarkdownRequest, ResumeSourceToMarkdownResult
from app.agents.resume_builder.resume_source_to_markdown_agent import ResumeSourceToMarkdownAgent


def run_resume_source_to_markdown(
    request: ResumeSourceToMarkdownRequest,
    *,
    agent: ResumeSourceToMarkdownAgent | None = None,
) -> ResumeSourceToMarkdownResult:
    output_path = Path(request.output_markdown_path)
    if output_path.exists() and output_path.is_dir():
        raise ValueError(f"Output path points to a directory: {output_path}")

    agent_instance = agent or ResumeSourceToMarkdownAgent()
    result = agent_instance.generate_markdown(request)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result.markdown_content, encoding="utf-8")
    return result
