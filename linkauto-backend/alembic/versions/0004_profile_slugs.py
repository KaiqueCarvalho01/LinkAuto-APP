"""Add slug columns to instructor_profiles and student_profiles

Revision ID: 0004_profile_slugs
Revises: 0003_messages_reviews
Create Date: 2026-08-22
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_profile_slugs"
down_revision = "0003_messages_reviews"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("instructor_profiles", sa.Column("slug", sa.String(150), nullable=True))
    op.create_index("ix_instructor_profiles_slug", "instructor_profiles", ["slug"], unique=True)

    op.add_column("student_profiles", sa.Column("slug", sa.String(150), nullable=True))
    op.create_index("ix_student_profiles_slug", "student_profiles", ["slug"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_student_profiles_slug", table_name="student_profiles")
    op.drop_column("student_profiles", "slug")

    op.drop_index("ix_instructor_profiles_slug", table_name="instructor_profiles")
    op.drop_column("instructor_profiles", "slug")
