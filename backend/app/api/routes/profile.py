from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.db.profile_repository import create_profile, get_profile_by_user_id, save_profile
from app.db.session import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.user_profile import UserProfile
from app.profile_service import (
    build_profile_paths,
    derive_follow_up_questions,
    extract_text_from_upload,
    parse_follow_up_answers,
    read_follow_up_answers,
    read_section_markdown,
    render_follow_up_answers_markdown,
    render_profile_markdown_v2,
    render_section_markdown,
    write_profile_markdown,
)
from app.schemas.profile import ProfileResponse

router = APIRouter(prefix="/profile", tags=["profile"])


def _get_or_create_profile(db: Session, user: User) -> UserProfile:
    profile = get_profile_by_user_id(db, user.id)
    if profile:
        paths = build_profile_paths(user.id)
        if not profile.linkedin_markdown_path:
            profile.linkedin_markdown_path = paths["linkedin"]
        if not profile.resume_markdown_path:
            profile.resume_markdown_path = paths["resume"]
        if not profile.follow_up_markdown_path:
            profile.follow_up_markdown_path = paths["follow_up"]
        if not profile.additional_info_markdown_path:
            profile.additional_info_markdown_path = paths["additional_info"]
        if not profile.profile_markdown_path:
            profile.profile_markdown_path = paths["profile"]
        save_profile(db, profile)
        return profile

    paths = build_profile_paths(user.id)
    return create_profile(
        db,
        user_id=user.id,
        profile_markdown_path=paths["profile"],
        linkedin_markdown_path=paths["linkedin"],
        resume_markdown_path=paths["resume"],
        follow_up_markdown_path=paths["follow_up"],
        additional_info_markdown_path=paths["additional_info"],
    )


def _build_profile_response(profile: UserProfile) -> ProfileResponse:
    linkedin_context = read_section_markdown(profile.linkedin_markdown_path)
    resume_context = read_section_markdown(profile.resume_markdown_path)
    additional_information = read_section_markdown(profile.additional_info_markdown_path)
    follow_up_answers = read_follow_up_answers(profile.follow_up_markdown_path)

    questions = derive_follow_up_questions(
        f"{linkedin_context}\n{resume_context}",
        additional_information,
        follow_up_answers,
    )

    for question in questions:
        follow_up_answers.setdefault(question, "")

    content = render_profile_markdown_v2(
        linkedin_context,
        resume_context,
        questions,
        follow_up_answers,
        additional_information,
    )
    write_profile_markdown(profile.profile_markdown_path, content)

    return ProfileResponse(
        profile_markdown_path=profile.profile_markdown_path,
        section_markdown_paths={
            "linkedin_profile": profile.linkedin_markdown_path,
            "resume": profile.resume_markdown_path,
            "follow_up_answers": profile.follow_up_markdown_path,
            "additional_information": profile.additional_info_markdown_path,
        },
        content=content,
        follow_up_questions=questions,
        follow_up_answers=follow_up_answers,
        additional_information=additional_information,
        has_linkedin_profile=bool(linkedin_context.strip()),
        has_resume=bool(resume_context.strip()),
        updated_at=profile.updated_at,
    )


@router.post("/update", response_model=ProfileResponse)
async def update_profile(
    linkedin_profile: UploadFile | None = File(default=None),
    resume: UploadFile | None = File(default=None),
    follow_up_answers: str | None = Form(default=None),
    additional_information: str | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = _get_or_create_profile(db, current_user)

    linkedin_context = read_section_markdown(profile.linkedin_markdown_path)
    resume_context = read_section_markdown(profile.resume_markdown_path)
    answers = read_follow_up_answers(profile.follow_up_markdown_path)
    existing_additional_information = read_section_markdown(profile.additional_info_markdown_path)

    if linkedin_profile is not None:
        payload = await linkedin_profile.read()
        linkedin_context = extract_text_from_upload(linkedin_profile.filename or "linkedin.pdf", payload)

    if resume is not None:
        payload = await resume.read()
        resume_context = extract_text_from_upload(resume.filename or "resume.pdf", payload)

    if follow_up_answers is not None:
        answers.update(parse_follow_up_answers(follow_up_answers))

    merged_context = f"{linkedin_context}\n{resume_context}"
    next_additional_information = (
        additional_information.strip() if additional_information is not None else existing_additional_information
    )
    questions = derive_follow_up_questions(merged_context, next_additional_information, answers)
    for question in questions:
        answers.setdefault(question, "")

    write_profile_markdown(
        profile.linkedin_markdown_path,
        render_section_markdown("LinkedIn Profile", linkedin_context),
    )
    write_profile_markdown(
        profile.resume_markdown_path,
        render_section_markdown("Resume", resume_context),
    )
    write_profile_markdown(
        profile.follow_up_markdown_path,
        render_follow_up_answers_markdown(questions, answers),
    )
    write_profile_markdown(
        profile.additional_info_markdown_path,
        render_section_markdown("Additional Information", next_additional_information),
    )
    write_profile_markdown(
        profile.profile_markdown_path,
        render_profile_markdown_v2(
            linkedin_context,
            resume_context,
            questions,
            answers,
            next_additional_information,
        ),
    )

    profile.updated_at = datetime.now(timezone.utc)
    save_profile(db, profile)

    return _build_profile_response(profile)


@router.get("", response_model=ProfileResponse)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = _get_or_create_profile(db, current_user)
    return _build_profile_response(profile)
