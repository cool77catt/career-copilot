import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.agents.resume_builder.contracts import JobDescriptionNormalizeRequest
from app.agents.resume_builder.jd_to_markdown_agent import (
    JobDescriptionMarkdownAgent,
    JobDescriptionMarkdownAgentError,
)
from app.agents.resume_builder.jd_to_markdown_cli import main
from app.agents.resume_builder.jd_to_markdown_runner import run_job_description_normalizer
from app.core.config import settings


class _FakeResponsesClient:
    def __init__(self, output_text: str) -> None:
        self.output_text = output_text
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_text=self.output_text)


class _FakeOpenAIClient:
    def __init__(self, output_text: str) -> None:
        self.responses = _FakeResponsesClient(output_text)


def test_jd_agent_uses_openai_sdk_client_and_returns_markdown():
    client = _FakeOpenAIClient("# Job Description\n\n## Responsibilities\n- Build APIs")
    agent = JobDescriptionMarkdownAgent(client=client, model="test-model")

    result = agent.generate_markdown(
        JobDescriptionNormalizeRequest(
            raw_text="Build APIs and own backend services.",
            output_markdown_path="storage/jd.md",
        )
    )

    assert result.output_markdown_path == "storage/jd.md"
    assert result.markdown_content.startswith("# Job Description")
    assert client.responses.calls[0]["model"] == "test-model"


def test_jd_agent_requires_api_key_without_injected_client(monkeypatch):
    monkeypatch.setattr(settings, "openai_api_key", None, raising=False)

    with pytest.raises(JobDescriptionMarkdownAgentError):
        JobDescriptionMarkdownAgent()


def test_runner_writes_markdown_file(tmp_path):
    output_path = tmp_path / "job-description.md"
    client = _FakeOpenAIClient("# Job Description\n\n## Qualifications\n- FastAPI")
    agent = JobDescriptionMarkdownAgent(client=client)

    result = run_job_description_normalizer(
        JobDescriptionNormalizeRequest(
            raw_text="Need FastAPI experience.",
            output_markdown_path=str(output_path),
        ),
        agent=agent,
    )

    assert result.output_markdown_path == str(output_path)
    assert output_path.read_text(encoding="utf-8") == result.markdown_content


def test_runner_rejects_directory_output_path(tmp_path):
    output_dir = tmp_path / "output-dir"
    output_dir.mkdir()
    client = _FakeOpenAIClient("# Job Description")
    agent = JobDescriptionMarkdownAgent(client=client)

    with pytest.raises(ValueError):
        run_job_description_normalizer(
            JobDescriptionNormalizeRequest(
                raw_text="Some job description text.",
                output_markdown_path=str(output_dir),
            ),
            agent=agent,
        )


def test_cli_returns_error_when_input_file_is_missing(tmp_path, capsys):
    input_path = tmp_path / "missing-job.txt"
    output_path = tmp_path / "job.md"

    exit_code = main(
        [
            "--input-file",
            str(input_path),
            "--output-path",
            str(output_path),
        ]
    )

    assert exit_code == 1
    stderr = capsys.readouterr().err
    assert "JD normalization failed" in stderr


def test_cli_with_mocked_runner_prints_machine_readable_json(tmp_path, monkeypatch, capsys):
    input_path = tmp_path / "job.txt"
    output_path = tmp_path / "job.md"
    input_path.write_text("Need Python and SQL.", encoding="utf-8")

    def fake_runner(request: JobDescriptionNormalizeRequest):
        output = Path(request.output_markdown_path)
        output.write_text("# Job Description\n", encoding="utf-8")
        return {
            "output_markdown_path": request.output_markdown_path,
            "markdown_content": "# Job Description\n",
        }

    monkeypatch.setattr(
        "app.agents.resume_builder.jd_to_markdown_cli.run_job_description_normalizer",
        lambda request: SimpleNamespace(model_dump=lambda: fake_runner(request)),
    )

    exit_code = main(
        [
            "--input-file",
            str(input_path),
            "--output-path",
            str(output_path),
        ]
    )

    assert exit_code == 0
    stdout = capsys.readouterr().out.strip()
    payload = json.loads(stdout)
    assert payload["output_markdown_path"] == str(output_path)
    assert payload["markdown_content"].startswith("# Job Description")


def test_cli_requires_input_file_argument():
    with pytest.raises(SystemExit) as exc_info:
        main(["--output-path", "out.md"])

    assert exc_info.value.code == 2
