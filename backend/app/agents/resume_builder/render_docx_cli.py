from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.agents.resume_builder.contracts import ResumeDocxRenderRequest
from app.agents.resume_builder.docx_runner import run_resume_docx_renderer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render a tailored resume markdown file into a new .docx using a template resume."
    )
    parser.add_argument("--resume-markdown-file", required=True, help="Path to the tailored resume markdown file.")
    parser.add_argument("--template-docx-file", required=True, help="Path to the template .docx resume.")
    parser.add_argument("--output-docx-path", required=True, help="Path where the rendered .docx should be written.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        request = ResumeDocxRenderRequest(
            resume_markdown=Path(args.resume_markdown_file).read_text(encoding="utf-8"),
            template_docx_path=args.template_docx_file,
            output_docx_path=args.output_docx_path,
        )
        result = run_resume_docx_renderer(request)
    except Exception as exc:
        print(f"Resume docx rendering failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result.model_dump(), ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
