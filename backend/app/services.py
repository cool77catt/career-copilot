from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User


def seed_default_user(db: Session) -> None:
    if not settings.seed_default_user:
        return

    existing = db.query(User).filter(User.email == settings.default_user_email).first()
    if existing:
        return

    user = User(
        name=settings.default_user_name,
        email=settings.default_user_email,
        password_hash=get_password_hash(settings.default_user_password),
    )
    db.add(user)
    db.commit()
