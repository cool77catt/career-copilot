from app.agents.resume_builder.config import ResumeBuilderModelRegistry
from app.agents.resume_builder.contracts import (
    GapAssessment,
    GapItem,
    JobDescriptionNormalizeRequest,
    ResumeDocxRenderRequest,
    ResumeMarkdownGenerateRequest,
)
from app.core.config import settings


def test_job_description_request_requires_text_and_output_path():
    payload = JobDescriptionNormalizeRequest(
        raw_text="Senior backend engineer role with FastAPI and AWS requirements.",
        output_markdown_path="storage/resume-builder/job-description.md",
    )

    assert payload.raw_text.startswith("Senior backend engineer")
    assert payload.output_markdown_path.endswith("job-description.md")


def test_resume_markdown_request_requires_some_candidate_context():
    request = ResumeMarkdownGenerateRequest(
        job_description_markdown="# Job Description\nNeed FastAPI, SQL, and AWS.",
        user_profile_markdown="# Profile\nBuilt API platforms.",
    )

    assert request.user_profile_markdown == "# Profile\nBuilt API platforms."


def test_gap_assessment_validates_bucket_types():
    assessment = GapAssessment(
        summary="Candidate has some missing evidence.",
        hard_gaps=[
            GapItem(
                gap_type="hard_gap",
                requirement="5+ years people management",
                details="Only 2 years of direct management evidence provided.",
                impact="Could be disqualifying for management-heavy roles.",
                evidence_status="insufficient evidence",
            )
        ],
    )

    assert assessment.hard_gaps[0].gap_type == "hard_gap"


def test_docx_render_request_requires_template_and_output_paths():
    request = ResumeDocxRenderRequest(
        resume_markdown="# Resume\n## Experience\nBuilt hiring tools.",
        template_docx_path="fixtures/template.docx",
        output_docx_path="tmp/output.docx",
    )

    assert request.template_docx_path.endswith(".docx")
    assert request.output_docx_path.endswith(".docx")


def test_resume_builder_model_registry_reads_settings(monkeypatch):
    monkeypatch.setattr(settings, "openai_resume_builder_jd_model", "gpt-test-jd", raising=False)
    monkeypatch.setattr(settings, "openai_resume_builder_assessment_model", "gpt-test-assess", raising=False)
    monkeypatch.setattr(settings, "openai_resume_builder_docx_model", "gpt-test-docx", raising=False)

    registry = ResumeBuilderModelRegistry.from_settings()

    assert registry.job_description_model == "gpt-test-jd"
    assert registry.assessment_model == "gpt-test-assess"
    assert registry.docx_model == "gpt-test-docx"
