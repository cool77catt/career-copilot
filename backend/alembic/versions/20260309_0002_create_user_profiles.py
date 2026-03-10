"""create user_profiles table

Revision ID: 20260309_0002
Revises: 20260306_0001
Create Date: 2026-03-09 10:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260309_0002"
down_revision = "20260306_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("profile_markdown_path", sa.String(length=500), nullable=False),
        sa.Column("linkedin_markdown_path", sa.String(length=500), nullable=False, server_default=""),
        sa.Column("resume_markdown_path", sa.String(length=500), nullable=False, server_default=""),
        sa.Column("follow_up_markdown_path", sa.String(length=500), nullable=False, server_default=""),
        sa.Column("additional_info_markdown_path", sa.String(length=500), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_user_profiles_user_id", "user_profiles", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_user_profiles_user_id", table_name="user_profiles")
    op.drop_table("user_profiles")
