from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib import error, request

from app.core.config import settings

SYSTEM_PROMPT = """You are a senior career strategy analyst.
Generate a detailed markdown report that synthesizes the user's LinkedIn profile,
resume, follow-up answers, and additional notes into a practical profile dossier
for downstream job search fit and resume/cover-letter generation.

Requirements:
- Output valid markdown only.
- Be specific and evidence-based; reference concrete signals from provided input.
- If data is missing, call it out explicitly as a gap.
- Include the following sections in order:
  1. Executive Summary
  2. Candidate Snapshot
  3. Role Fit Analysis
  4. Strengths to Emphasize
  5. Risks and Gaps
  6. Resume Strategy Recommendations
  7. Job Search Targeting Guidance
  8. Suggested Follow-up Data to Collect
"""


class ProfileReportAgentError(RuntimeError):
    """Raised when the OpenAI-backed profile report agent fails."""


@dataclass(frozen=True)
class ProfileReportAgentInput:
    linkedin_profile: str
    resume: str
    additional_information: str
    follow_up_answers: dict[str, str]


class ProfileReportAgent:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: int = 90,
    ) -> None:
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_profile_agent_model
        self.timeout_seconds = timeout_seconds

    def generate_report(self, payload: ProfileReportAgentInput) -> str:
        if not self.api_key:
            raise ProfileReportAgentError(
                "OPENAI_API_KEY is not configured. Set OPENAI_API_KEY before running the profile report agent."
            )

        request_body = {
            "model": self.model,
            "input": [
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": SYSTEM_PROMPT}],
                },
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": _render_user_prompt(payload)}],
                },
            ],
        }

        request_data = json.dumps(request_body).encode("utf-8")
        req = request.Request(
            url="https://api.openai.com/v1/responses",
            data=request_data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                body = response.read().decode("utf-8")
        except error.HTTPError as exc:
            error_message = exc.read().decode("utf-8", errors="ignore")
            raise ProfileReportAgentError(f"OpenAI request failed ({exc.code}): {error_message}") from exc
        except error.URLError as exc:
            raise ProfileReportAgentError(f"OpenAI connection failed: {exc.reason}") from exc

        try:
            payload_json = json.loads(body)
        except json.JSONDecodeError as exc:
            raise ProfileReportAgentError("OpenAI response was not valid JSON.") from exc

        markdown = _extract_output_text(payload_json).strip()
        if not markdown:
            raise ProfileReportAgentError("OpenAI response did not include report content.")

        return markdown


def _render_user_prompt(payload: ProfileReportAgentInput) -> str:
    qa_lines: list[str] = []
    if payload.follow_up_answers:
        for question, answer in payload.follow_up_answers.items():
            qa_lines.append(f"- Q: {question}")
            qa_lines.append(f"  A: {(answer or '').strip()}")
    else:
        qa_lines.append("- No follow-up answers provided.")

    linkedin = payload.linkedin_profile.strip() or "No LinkedIn profile content provided."
    resume = payload.resume.strip() or "No resume content provided."
    additional = payload.additional_information.strip() or "No additional information provided."
    qa_block = "\n".join(qa_lines)

    return (
        "Build a profile report using the following inputs.\n\n"
        "## LinkedIn Profile\n"
        f"{linkedin}\n\n"
        "## Resume\n"
        f"{resume}\n\n"
        "## Follow-up Questions and Answers\n"
        f"{qa_block}\n\n"
        "## Additional Information\n"
        f"{additional}\n"
    )


def _extract_output_text(payload: dict[str, Any]) -> str:
    output_text = payload.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text

    collected: list[str] = []
    output_items = payload.get("output", [])
    if isinstance(output_items, list):
        for item in output_items:
            if not isinstance(item, dict):
                continue
            content_items = item.get("content", [])
            if not isinstance(content_items, list):
                continue
            for content in content_items:
                if not isinstance(content, dict):
                    continue
                if content.get("type") == "output_text":
                    text = content.get("text")
                    if isinstance(text, str) and text.strip():
                        collected.append(text)

    return "\n\n".join(collected)
