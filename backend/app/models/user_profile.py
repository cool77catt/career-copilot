from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    profile_markdown_path: Mapped[str] = mapped_column(String(500), nullable=False)
    linkedin_markdown_path: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    resume_markdown_path: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    follow_up_markdown_path: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    additional_info_markdown_path: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
