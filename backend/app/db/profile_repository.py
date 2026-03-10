from sqlalchemy.orm import Session

from app.models.user_profile import UserProfile


def get_profile_by_user_id(db: Session, user_id: int) -> UserProfile | None:
    return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()


def create_profile(
    db: Session,
    user_id: int,
    profile_markdown_path: str,
    linkedin_markdown_path: str,
    resume_markdown_path: str,
    follow_up_markdown_path: str,
    additional_info_markdown_path: str,
) -> UserProfile:
    profile = UserProfile(
        user_id=user_id,
        profile_markdown_path=profile_markdown_path,
        linkedin_markdown_path=linkedin_markdown_path,
        resume_markdown_path=resume_markdown_path,
        follow_up_markdown_path=follow_up_markdown_path,
        additional_info_markdown_path=additional_info_markdown_path,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def save_profile(db: Session, profile: UserProfile) -> UserProfile:
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile
