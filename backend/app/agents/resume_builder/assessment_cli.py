from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.agents.resume_builder.assessment_runner import run_resume_assessment_and_write_outputs
from app.agents.resume_builder.contracts import (
    QuestionAnswer,
    ResumeConstraintSet,
    ResumeMarkdownGenerateRequest,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Assess candidate fit against a job description and generate a tailored markdown resume."
    )
    parser.add_argument("--job-description-file", required=True, help="Path to the normalized JD markdown file.")
    parser.add_argument("--user-profile-file", help="Path to the user profile markdown file.")
    parser.add_argument("--current-resume-file", help="Path to the current resume markdown file.")
    parser.add_argument("--linkedin-file", help="Path to the LinkedIn markdown file.")
    parser.add_argument("--additional-context-file", help="Path to additional context text or markdown.")
    parser.add_argument("--qa-json-file", help="Path to a JSON file containing question/answer entries.")
    parser.add_argument("--constraints-json-file", help="Path to a JSON file containing resume constraints.")
    parser.add_argument("--output-json-path", required=True, help="Path where the full assessment JSON should be written.")
    parser.add_argument(
        "--output-resume-markdown-path",
        required=True,
        help="Path where the tailored resume markdown should be written.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        request = ResumeMarkdownGenerateRequest(
            job_description_markdown=_read_text(args.job_description_file),
            user_profile_markdown=_read_optional_text(args.user_profile_file),
            current_resume_markdown=_read_optional_text(args.current_resume_file),
            linkedin_markdown=_read_optional_text(args.linkedin_file),
            additional_context=_read_optional_text(args.additional_context_file),
            question_answers=_read_question_answers(args.qa_json_file),
            constraints=_read_constraints(args.constraints_json_file),
        )
        result = run_resume_assessment_and_write_outputs(
            request,
            output_json_path=args.output_json_path,
            output_resume_markdown_path=args.output_resume_markdown_path,
        )
    except Exception as exc:
        print(f"Resume assessment failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result.model_dump(), ensure_ascii=True))
    return 0


def _read_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _read_optional_text(path: str | None) -> str | None:
    if not path:
        return None
    return _read_text(path)


def _read_question_answers(path: str | None) -> list[QuestionAnswer]:
    if not path:
        return []
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Q&A JSON file must contain a list of objects.")
    return [QuestionAnswer.model_validate(item) for item in payload]


def _read_constraints(path: str | None) -> ResumeConstraintSet:
    if not path:
        return ResumeConstraintSet()
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return ResumeConstraintSet.model_validate(payload)


if __name__ == "__main__":
    raise SystemExit(main())
