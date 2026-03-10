from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader

from app.core.config import settings


def extract_text_from_upload(filename: str, file_bytes: bytes) -> str:
    # Try proper PDF extraction first; fallback keeps local/dev tests deterministic.
    if filename.lower().endswith(".pdf"):
        try:
            reader = PdfReader(BytesIO(file_bytes))
        except Exception:
            reader = None

        if reader is not None:
            page_text: list[str] = []
            for page in reader.pages:
                text = page.extract_text() or ""
                if text:
                    page_text.append(text)
            combined = "\n".join(page_text).strip()
            if combined:
                return combined

    return file_bytes.decode("utf-8", errors="ignore").strip()


def derive_follow_up_questions(profile_context: str, additional_information: str, follow_up_answers: dict[str, str]) -> list[str]:
    merged_answers = " ".join(follow_up_answers.values())
    merged = f"{profile_context}\n{additional_information}\n{merged_answers}".lower()
    questions: list[str] = []

    if "lead" not in merged and "manage" not in merged:
        questions.append("Have you led teams, projects, or cross-functional initiatives?")
    if "impact" not in merged and "result" not in merged and "improve" not in merged:
        questions.append("Can you share measurable outcomes from your work (revenue, time saved, growth, etc.)?")
    if "skill" not in merged and "tool" not in merged and "python" not in merged:
        questions.append("Which technical tools, platforms, or skills should be emphasized for your target roles?")
    if "startup" not in merged and "industry" not in merged:
        questions.append("What industries or company stages (startup, growth, enterprise) do you prefer?")

    if not questions:
        questions.append("What additional experience should be highlighted that is missing from current documents?")

    return questions


def render_profile_markdown_v2(
    linkedin_context: str,
    resume_context: str,
    follow_up_questions: list[str],
    follow_up_answers: dict[str, str],
    additional_information: str,
) -> str:
    linkedin_section = linkedin_context.strip() or "No LinkedIn profile input yet."
    resume_section = resume_context.strip() or "No resume input yet."
    additional_section = additional_information.strip() or "No additional information yet."

    if follow_up_questions:
        qa_lines: list[str] = []
        for question in follow_up_questions:
            answer = follow_up_answers.get(question, "").strip() or "No answer provided yet."
            qa_lines.append(f"- **Q:** {question}")
            qa_lines.append(f"  - **A:** {answer}")
        qa_block = "\n".join(qa_lines)
    else:
        qa_block = "- No follow-up questions currently generated."

    return (
        "# profile.md\n\n"
        "## LinkedIn Profile Input\n"
        f"{linkedin_section}\n\n"
        "## Resume Input\n"
        f"{resume_section}\n\n"
        "## Follow-up Questions and Answers\n"
        f"{qa_block}\n\n"
        "## Additional Information\n"
        f"{additional_section}\n"
    )


def build_profile_directory(user_id: int) -> Path:
    root = Path(settings.profile_storage_dir)
    root.mkdir(parents=True, exist_ok=True)
    profile_dir = root / f"user-{user_id}"
    profile_dir.mkdir(parents=True, exist_ok=True)
    return profile_dir


def build_profile_paths(user_id: int) -> dict[str, str]:
    profile_dir = build_profile_directory(user_id)
    return {
        "profile": str(profile_dir / "profile.md"),
        "linkedin": str(profile_dir / "linkedin-profile.md"),
        "resume": str(profile_dir / "resume.md"),
        "follow_up": str(profile_dir / "follow-up-answers.md"),
        "additional_info": str(profile_dir / "additional-information.md"),
    }


def write_profile_markdown(path: str, content: str) -> None:
    profile_path = Path(path)
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    profile_path.write_text(content, encoding="utf-8")


def render_section_markdown(title: str, body: str) -> str:
    section_body = body.strip() or "No information provided yet."
    return f"# {title}\n\n{section_body}\n"


def render_follow_up_answers_markdown(questions: list[str], answers: dict[str, str]) -> str:
    ordered_questions = list(questions)
    for question in answers.keys():
        if question not in ordered_questions:
            ordered_questions.append(question)

    if not ordered_questions:
        return "# Follow-up Answers\n\nNo follow-up questions currently generated.\n"

    lines: list[str] = ["# Follow-up Answers", ""]
    for question in ordered_questions:
        answer = answers.get(question, "").strip()
        lines.append(f"## {question}")
        lines.append("")
        lines.append(answer)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def read_profile_markdown(path: str) -> str:
    profile_path = Path(path)
    if not profile_path.exists():
        return ""
    return profile_path.read_text(encoding="utf-8")


def parse_follow_up_answers(value: str | None) -> dict[str, str]:
    if not value:
        return {}
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return {}
    if not isinstance(parsed, dict):
        return {}
    clean: dict[str, str] = {}
    for key, answer in parsed.items():
        if isinstance(key, str):
            clean[key] = str(answer) if answer is not None else ""
    return clean


def parse_follow_up_answers_markdown(content: str) -> dict[str, str]:
    answers: dict[str, str] = {}
    current_question: str | None = None
    current_lines: list[str] = []

    for line in content.splitlines():
        if line.startswith("## "):
            if current_question is not None:
                answers[current_question] = "\n".join(current_lines).strip()
            current_question = line[3:].strip()
            current_lines = []
            continue

        if current_question is not None:
            current_lines.append(line)

    if current_question is not None:
        answers[current_question] = "\n".join(current_lines).strip()

    return answers


def read_follow_up_answers(path: str) -> dict[str, str]:
    return parse_follow_up_answers_markdown(read_profile_markdown(path))


def parse_section_markdown(content: str) -> str:
    lines = content.splitlines()
    if lines and lines[0].startswith("#"):
        lines = lines[1:]
        while lines and not lines[0].strip():
            lines = lines[1:]
    return "\n".join(lines).strip()


def read_section_markdown(path: str) -> str:
    return parse_section_markdown(read_profile_markdown(path))
