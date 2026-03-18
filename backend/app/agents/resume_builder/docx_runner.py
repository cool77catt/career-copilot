from __future__ import annotations

from app.agents.resume_builder.contracts import ResumeDocxRenderRequest, ResumeDocxRenderResult
from app.agents.resume_builder.docx_renderer import ResumeDocxRenderer


def run_resume_docx_renderer(
    request: ResumeDocxRenderRequest,
    *,
    renderer: ResumeDocxRenderer | None = None,
) -> ResumeDocxRenderResult:
    renderer_instance = renderer or ResumeDocxRenderer()
    return renderer_instance.render(request)
