from __future__ import annotations

from typing import Any

from openai import OpenAI

from app.agents.resume_builder.contracts import JobDescriptionNormalizeRequest, JobDescriptionNormalizeResult
from app.agents.resume_builder.prompts import JD_TO_MARKDOWN_SYSTEM_PROMPT
from app.core.config import settings


class JobDescriptionMarkdownAgentError(RuntimeError):
    """Raised when the JD-to-markdown agent cannot complete successfully."""


class JobDescriptionMarkdownAgent:
    def __init__(
        self,
        *,
        client: OpenAI | Any | None = None,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        resolved_api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_resume_builder_jd_model
        if client is not None:
            self.client = client
            return
        if not resolved_api_key:
            raise JobDescriptionMarkdownAgentError(
                "OPENAI_API_KEY is not configured. Set OPENAI_API_KEY before running the resume builder JD agent."
            )
        self.client = OpenAI(api_key=resolved_api_key)

    def generate_markdown(self, request: JobDescriptionNormalizeRequest) -> JobDescriptionNormalizeResult:
        if not request.raw_text.strip():
            raise JobDescriptionMarkdownAgentError("Job description text is required.")

        response = self.client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": JD_TO_MARKDOWN_SYSTEM_PROMPT}],
                },
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": _render_user_prompt(request.raw_text)}],
                },
            ],
        )
        markdown = _extract_output_text(response).strip()
        if not markdown:
            raise JobDescriptionMarkdownAgentError("OpenAI response did not include normalized markdown content.")

        return JobDescriptionNormalizeResult(
            output_markdown_path=request.output_markdown_path,
            markdown_content=markdown,
        )


def _render_user_prompt(raw_text: str) -> str:
    return (
        "Convert the following job description text into normalized markdown.\n\n"
        "Requirements:\n"
        "- Preserve factual content from the source text.\n"
        "- Use stable markdown headings where supported by the text.\n"
        "- Keep the output useful for downstream fit analysis.\n\n"
        "## Raw Job Description Text\n"
        f"{raw_text.strip()}\n"
    )


def _extract_output_text(response: Any) -> str:
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str) and output_text.strip():
        return output_text

    output = getattr(response, "output", None)
    if not isinstance(output, list):
        return ""

    collected: list[str] = []
    for item in output:
        content_items = getattr(item, "content", None)
        if not isinstance(content_items, list):
            continue
        for content in content_items:
            content_type = getattr(content, "type", None)
            text = getattr(content, "text", None)
            if content_type == "output_text" and isinstance(text, str) and text.strip():
                collected.append(text)

    return "\n\n".join(collected)
