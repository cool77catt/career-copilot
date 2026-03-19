import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.agents.resume_builder.assessment_agent import (
    ResumeAssessmentAgent,
    ResumeAssessmentAgentError,
    _render_user_prompt,
)
from app.agents.resume_builder.assessment_cli import main
from app.agents.resume_builder.assessment_runner import run_resume_assessment_and_write_outputs
from app.agents.resume_builder.contracts import ResumeMarkdownGenerateRequest, ResumeMarkdownGenerateResult
from app.core.config import settings


def _sample_result() -> ResumeMarkdownGenerateResult:
    return ResumeMarkdownGenerateResult.model_validate(
        {
            "fit_assessment": {
                "percentage_fit": 78,
                "summary": "Strong backend match with some cloud-depth gaps.",
                "confirmed_strengths": ["FastAPI APIs", "SQL services"],
                "inferred_strengths": ["Cross-functional execution"],
            },
            "gap_assessment": {
                "summary": "Most gaps are clarifiable rather than disqualifying.",
                "hard_gaps": [],
                "clarifiable_gaps": [
                    {
                        "gap_type": "clarifiable_gap",
                        "requirement": "AWS depth",
                        "details": "AWS usage is hinted but not described with scope.",
                        "impact": "Could reduce recruiter confidence.",
                        "evidence_status": "ambiguous",
                        "follow_up_hint": "Ask for specific AWS services and production scale.",
                    }
                ],
                "weak_evidence_areas": [],
            },
            "clarifying_questions": [
                {
                    "question": "Which AWS services have you used in production?",
                    "rationale": "Clarifies the cloud-platform requirement.",
                    "target_gaps": ["AWS depth"],
                    "priority": "high",
                }
            ],
            "resume_markdown": "# Resume\n\n## Experience\n- Built FastAPI services.\n",
        }
    )


class _FakeParseClient:
    def __init__(self, parsed_result: ResumeMarkdownGenerateResult) -> None:
        self.parsed_result = parsed_result
        self.calls: list[dict] = []

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_parsed=self.parsed_result)


class _FakeOpenAIClient:
    def __init__(self, parsed_result: ResumeMarkdownGenerateResult) -> None:
        self.responses = _FakeParseClient(parsed_result)


def test_assessment_agent_uses_structured_parse_and_returns_result():
    expected = _sample_result()
    client = _FakeOpenAIClient(expected)
    agent = ResumeAssessmentAgent(client=client, model="test-assessment-model")

    result = agent.generate_assessment(
        ResumeMarkdownGenerateRequest(
            job_description_markdown="# Job Description\nNeed FastAPI and AWS.",
            user_profile_markdown="# Profile\nBuilt APIs.",
        )
    )

    assert result == expected
    assert client.responses.calls[0]["model"] == "test-assessment-model"
    assert client.responses.calls[0]["text_format"] is ResumeMarkdownGenerateResult


def test_assessment_prompt_emphasizes_resume_rewrite_not_passthrough():
    prompt = _render_user_prompt(
        ResumeMarkdownGenerateRequest(
            job_description_markdown="# Job Description\nNeed FastAPI and AWS.",
            current_resume_markdown="# Resume\nBuilt APIs.",
        )
    )

    assert "Do not echo the current resume back unchanged." in prompt
    assert "Optimize for callback likelihood." in prompt
    assert "Never invent unsupported experience or outcomes." in prompt
    assert "- Max pages: Default to 2" in prompt


def test_assessment_agent_requires_api_key_without_injected_client(monkeypatch):
    monkeypatch.setattr(settings, "openai_api_key", None, raising=False)

    with pytest.raises(ResumeAssessmentAgentError):
        ResumeAssessmentAgent()


def test_assessment_runner_writes_json_and_resume_markdown(tmp_path):
    expected = _sample_result()
    client = _FakeOpenAIClient(expected)
    agent = ResumeAssessmentAgent(client=client)
    output_json = tmp_path / "assessment.json"
    output_resume = tmp_path / "resume.md"

    result = run_resume_assessment_and_write_outputs(
        ResumeMarkdownGenerateRequest(
            job_description_markdown="# Job Description\nNeed FastAPI and SQL.",
            user_profile_markdown="# Profile\nBuilt APIs.",
        ),
        output_json_path=str(output_json),
        output_resume_markdown_path=str(output_resume),
        agent=agent,
    )

    assert result == expected
    saved_json = json.loads(output_json.read_text(encoding="utf-8"))
    assert saved_json["fit_assessment"]["percentage_fit"] == 78
    assert output_resume.read_text(encoding="utf-8").startswith("# Resume")


def test_assessment_runner_rejects_directory_output_path(tmp_path):
    expected = _sample_result()
    client = _FakeOpenAIClient(expected)
    agent = ResumeAssessmentAgent(client=client)
    output_dir = tmp_path / "results"
    output_dir.mkdir()

    with pytest.raises(ValueError):
        run_resume_assessment_and_write_outputs(
            ResumeMarkdownGenerateRequest(
                job_description_markdown="# Job Description\nNeed FastAPI and SQL.",
                user_profile_markdown="# Profile\nBuilt APIs.",
            ),
            output_json_path=str(output_dir),
            output_resume_markdown_path=str(tmp_path / "resume.md"),
            agent=agent,
        )


def test_assessment_cli_reads_files_and_prints_json(tmp_path, monkeypatch, capsys):
    job_description = tmp_path / "job-description.md"
    user_profile = tmp_path / "profile.md"
    qa_json = tmp_path / "qa.json"
    constraints_json = tmp_path / "constraints.json"
    output_json = tmp_path / "result.json"
    output_resume = tmp_path / "tailored-resume.md"

    job_description.write_text("# Job Description\nNeed FastAPI and AWS.\n", encoding="utf-8")
    user_profile.write_text("# Profile\nBuilt API services.\n", encoding="utf-8")
    qa_json.write_text(
        json.dumps([{"question": "Have you used AWS Lambda?", "answer": "Yes, in production."}]),
        encoding="utf-8",
    )
    constraints_json.write_text(
        json.dumps({"section_order": ["Summary", "Experience"], "max_pages": 2, "tone": "concise"}),
        encoding="utf-8",
    )

    def fake_runner(request, *, output_json_path, output_resume_markdown_path):
        Path(output_json_path).write_text(json.dumps(_sample_result().model_dump()), encoding="utf-8")
        Path(output_resume_markdown_path).write_text(_sample_result().resume_markdown, encoding="utf-8")
        assert request.job_description_markdown.startswith("# Job Description")
        assert request.user_profile_markdown.startswith("# Profile")
        assert request.question_answers[0].question == "Have you used AWS Lambda?"
        assert request.constraints.max_pages == 2
        return _sample_result()

    monkeypatch.setattr(
        "app.agents.resume_builder.assessment_cli.run_resume_assessment_and_write_outputs",
        fake_runner,
    )

    exit_code = main(
        [
            "--job-description-file",
            str(job_description),
            "--user-profile-file",
            str(user_profile),
            "--qa-json-file",
            str(qa_json),
            "--constraints-json-file",
            str(constraints_json),
            "--output-json-path",
            str(output_json),
            "--output-resume-markdown-path",
            str(output_resume),
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out.strip())
    assert payload["fit_assessment"]["percentage_fit"] == 78
    assert output_json.exists()
    assert output_resume.exists()


def test_assessment_cli_fails_without_candidate_context(tmp_path, capsys):
    job_description = tmp_path / "job-description.md"
    output_json = tmp_path / "result.json"
    output_resume = tmp_path / "tailored-resume.md"
    job_description.write_text("# Job Description\nNeed FastAPI and AWS.\n", encoding="utf-8")

    exit_code = main(
        [
            "--job-description-file",
            str(job_description),
            "--output-json-path",
            str(output_json),
            "--output-resume-markdown-path",
            str(output_resume),
        ]
    )

    assert exit_code == 1
    assert "At least one candidate-context input is required" in capsys.readouterr().err
