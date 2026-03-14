import json
from pathlib import Path

from app.agents.profile_report_agent.agent import ProfileReportAgent
from app.core.config import settings


def _auth_headers(client):
    response = client.post(
        "/auth/login",
        json={"email": "chris77carl@gmail.com", "password": "default"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_update_profile_with_all_sections_creates_markdown(client):
    headers = _auth_headers(client)

    response = client.post(
        "/profile/update",
        files={
            "linkedin_profile": ("linkedin.pdf", b"LinkedIn summary with leadership and growth impact", "application/pdf"),
            "resume": ("resume.pdf", b"Resume highlights with Python, SQL and FastAPI", "application/pdf"),
        },
        data={
            "follow_up_answers": json.dumps(
                {
                    "Have you led teams, projects, or cross-functional initiatives?": "Yes, led a 6-person squad.",
                }
            ),
            "additional_information": "Interested in startup and growth-stage product roles.",
        },
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()

    assert body["has_linkedin_profile"] is True
    assert body["has_resume"] is True
    assert body["additional_information"] == "Interested in startup and growth-stage product roles."
    assert body["profile_markdown_path"].endswith("profile.md")
    assert "## LinkedIn Profile Input" in body["content"]
    assert "## Resume Input" in body["content"]
    assert "## Follow-up Questions and Answers" in body["content"]
    assert "## Additional Information" in body["content"]
    assert "section_markdown_paths" in body

    profile_path = Path(body["profile_markdown_path"])
    assert profile_path.exists()
    assert "LinkedIn Profile Input" in profile_path.read_text(encoding="utf-8")

    section_paths = body["section_markdown_paths"]
    linkedin_path = Path(section_paths["linkedin_profile"])
    resume_path = Path(section_paths["resume"])
    follow_up_path = Path(section_paths["follow_up_answers"])
    additional_info_path = Path(section_paths["additional_information"])

    assert linkedin_path.exists()
    assert resume_path.exists()
    assert follow_up_path.exists()
    assert additional_info_path.exists()

    assert "LinkedIn summary with leadership and growth impact" in linkedin_path.read_text(encoding="utf-8")
    assert "Resume highlights with Python, SQL and FastAPI" in resume_path.read_text(encoding="utf-8")
    assert "Yes, led a 6-person squad." in follow_up_path.read_text(encoding="utf-8")
    assert "Interested in startup and growth-stage product roles." in additional_info_path.read_text(encoding="utf-8")


def test_follow_up_answers_are_returned_and_persisted(client):
    headers = _auth_headers(client)

    first = client.post(
        "/profile/update",
        files={
            "linkedin_profile": ("linkedin.pdf", b"Profile content", "application/pdf"),
        },
        data={
            "follow_up_answers": json.dumps(
                {
                    "Which technical tools, platforms, or skills should be emphasized for your target roles?": "Python, SQL, AWS",
                }
            ),
            "additional_information": "Remote-first preference",
        },
        headers=headers,
    )
    assert first.status_code == 200

    second = client.get("/profile", headers=headers)
    assert second.status_code == 200
    body = second.json()

    assert "follow_up_answers" in body
    assert body["follow_up_answers"][
        "Which technical tools, platforms, or skills should be emphasized for your target roles?"
    ] == "Python, SQL, AWS"


def test_update_profile_allows_additional_info_only(client):
    headers = _auth_headers(client)

    response = client.post(
        "/profile/update",
        data={
            "follow_up_answers": json.dumps({}),
            "additional_information": "Extra context without replacing files.",
        },
        headers=headers,
    )
    assert response.status_code == 200

    body = response.json()
    assert body["additional_information"] == "Extra context without replacing files."
    assert "Extra context without replacing files." in body["content"]


def test_update_profile_generates_revisioned_profile_reports(client, monkeypatch):
    headers = _auth_headers(client)
    monkeypatch.setattr(settings, "openai_api_key", "test-api-key", raising=False)
    monkeypatch.setattr(
        ProfileReportAgent,
        "generate_report",
        lambda self, payload: (
            "## Executive Summary\n"
            "Generated profile report for testing.\n\n"
            "## Candidate Snapshot\n"
            "Candidate has measurable outcomes."
        ),
    )

    first = client.post(
        "/profile/update",
        data={
            "follow_up_answers": json.dumps({}),
            "additional_information": "First profile update",
        },
        headers=headers,
    )
    assert first.status_code == 200

    first_profile = client.get("/profile", headers=headers)
    assert first_profile.status_code == 200
    first_body = first_profile.json()
    assert first_body["profile_report_latest_path"]
    assert len(first_body["profile_report_revision_paths"]) == 1

    latest_path = Path(first_body["profile_report_latest_path"])
    assert latest_path.exists()
    assert "Generated profile report for testing." in latest_path.read_text(encoding="utf-8")

    second = client.post(
        "/profile/update",
        data={
            "follow_up_answers": json.dumps({}),
            "additional_information": "Second profile update",
        },
        headers=headers,
    )
    assert second.status_code == 200

    second_profile = client.get("/profile", headers=headers)
    assert second_profile.status_code == 200
    second_body = second_profile.json()
    assert second_body["profile_report_latest_path"]
    assert len(second_body["profile_report_revision_paths"]) == 2
