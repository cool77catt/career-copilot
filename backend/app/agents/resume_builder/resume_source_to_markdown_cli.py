from __future__ import annotations

import argparse
import json
import sys

from app.agents.resume_builder.contracts import ResumeSourceToMarkdownRequest
from app.agents.resume_builder.resume_source_to_markdown_runner import run_resume_source_to_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert an incoming resume (.pdf or .docx) into markdown using the resume builder agent."
    )
    parser.add_argument("--input-resume-file", required=True, help="Path to the source resume file (.pdf or .docx).")
    parser.add_argument("--output-markdown-path", required=True, help="Path where the markdown file should be written.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        request = ResumeSourceToMarkdownRequest(
            input_resume_path=args.input_resume_file,
            output_markdown_path=args.output_markdown_path,
        )
        result = run_resume_source_to_markdown(request)
    except Exception as exc:
        print(f"Resume import failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result.model_dump(), ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
