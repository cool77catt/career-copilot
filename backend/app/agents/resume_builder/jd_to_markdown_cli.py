from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.agents.resume_builder.contracts import JobDescriptionNormalizeRequest
from app.agents.resume_builder.jd_to_markdown_runner import run_job_description_normalizer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Normalize raw job-description text into markdown using the resume builder agent."
    )
    parser.add_argument("--input-file", required=True, help="Path to a text file containing the raw job description.")
    parser.add_argument("--output-path", required=True, help="Path where the markdown file should be written.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        raw_text = Path(args.input_file).read_text(encoding="utf-8")
        request = JobDescriptionNormalizeRequest(raw_text=raw_text, output_markdown_path=args.output_path)
        result = run_job_description_normalizer(request)
    except Exception as exc:
        print(f"JD normalization failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result.model_dump(), ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
