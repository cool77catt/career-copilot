from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.user_repository import create_user, get_user_by_email


def seed_default_user(db: Session) -> None:
    if not settings.seed_default_user:
        return

    existing = get_user_by_email(db, settings.default_user_email)
    if existing:
        return

    create_user(
        db,
        name=settings.default_user_name,
        email=settings.default_user_email,
        password_hash=get_password_hash(settings.default_user_password),
    )
