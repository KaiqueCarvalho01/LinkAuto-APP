"""Initial schema.

Revision ID: 0001
Revises:
Create Date: 2026-10-06

Baseline generated from the SQLAlchemy models. Replaces revisions 0001-0004, which
never applied cleanly to an empty database (users/profile tables were never created).
"""

from typing import TYPE_CHECKING

import sqlalchemy as sa
from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("roles", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_users_email"), ["email"], unique=True)

    op.create_table(
        "instructor_profiles",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("slug", sa.String(length=150), nullable=True),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=30), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("state", sa.String(length=120), nullable=True),
        sa.Column("bio", sa.String(length=2000), nullable=True),
        sa.Column("specialties", sa.JSON(), nullable=False),
        sa.Column("price_per_hour", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("avatar_url", sa.String(length=500), nullable=True),
        sa.Column(
            "detran_status",
            sa.Enum("PENDENTE", "APROVADO", "REJEITADO", name="detranstatus"),
            nullable=False,
        ),
        sa.Column("action_radius_km", sa.Integer(), nullable=False),
        sa.Column("latitude", sa.Double(), nullable=True),
        sa.Column("longitude", sa.Double(), nullable=True),
        sa.Column("rating_avg", sa.Double(), nullable=False),
        sa.Column("rating_count", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )
    with op.batch_alter_table("instructor_profiles", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_instructor_profiles_detran_status"), ["detran_status"], unique=False
        )
        batch_op.create_index(batch_op.f("ix_instructor_profiles_slug"), ["slug"], unique=True)

    op.create_table(
        "student_profiles",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("slug", sa.String(length=150), nullable=True),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=30), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("state", sa.String(length=120), nullable=True),
        sa.Column(
            "license_type",
            sa.Enum("NENHUMA", "A", "B", "AB", "C", "D", "E", "EM_PROCESSO", name="licensetype"),
            nullable=False,
        ),
        sa.Column("avatar_url", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )
    with op.batch_alter_table("student_profiles", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_student_profiles_slug"), ["slug"], unique=True)

    op.create_table(
        "bookings",
        sa.Column("student_id", sa.String(length=36), nullable=False),
        sa.Column("instructor_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("location_description", sa.Text(), nullable=True),
        sa.Column("latitude", sa.Numeric(precision=10, scale=7), nullable=True),
        sa.Column("longitude", sa.Numeric(precision=10, scale=7), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_by", sa.String(length=20), nullable=True),
        sa.Column("cancellation_reason", sa.Text(), nullable=True),
        sa.Column("reminder_sent", sa.Boolean(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["instructor_id"], ["instructor_profiles.user_id"]),
        sa.ForeignKeyConstraint(["student_id"], ["student_profiles.user_id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("bookings", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_bookings_instructor_id"), ["instructor_id"], unique=False
        )
        batch_op.create_index(
            "ix_bookings_instructor_status", ["instructor_id", "status"], unique=False
        )
        batch_op.create_index(batch_op.f("ix_bookings_student_id"), ["student_id"], unique=False)
        batch_op.create_index("ix_bookings_student_status", ["student_id", "status"], unique=False)

    op.create_table(
        "instructor_documents",
        sa.Column("instructor_id", sa.String(length=36), nullable=False),
        sa.Column("reviewed_by", sa.String(length=36), nullable=True),
        sa.Column("detran_credential_url", sa.String(length=500), nullable=True),
        sa.Column("criminal_record_url", sa.String(length=500), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_status", sa.String(length=20), nullable=False),
        sa.Column("review_reason", sa.String(length=500), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["instructor_id"], ["instructor_profiles.user_id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("instructor_documents", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_instructor_documents_instructor_id"), ["instructor_id"], unique=False
        )

    op.create_table(
        "slots",
        sa.Column("instructor_id", sa.String(length=36), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["instructor_id"], ["instructor_profiles.user_id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("slots", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_slots_instructor_id"), ["instructor_id"], unique=False)
        batch_op.create_index(
            "ix_slots_instructor_starts", ["instructor_id", "starts_at"], unique=False
        )

    op.create_table(
        "student_penalties",
        sa.Column("student_id", sa.String(length=36), nullable=False),
        sa.Column("blocked_until", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["student_id"], ["student_profiles.user_id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("student_penalties", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_student_penalties_student_id"), ["student_id"], unique=False
        )

    op.create_table(
        "booking_messages",
        sa.Column("booking_id", sa.String(length=36), nullable=False),
        sa.Column("sender_id", sa.String(length=36), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sender_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("booking_messages", schema=None) as batch_op:
        batch_op.create_index(
            "ix_booking_messages_booking_created", ["booking_id", "created_at"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_booking_messages_booking_id"), ["booking_id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_booking_messages_sender_id"), ["sender_id"], unique=False
        )

    op.create_table(
        "booking_slots",
        sa.Column("booking_id", sa.String(length=36), nullable=False),
        sa.Column("slot_id", sa.String(length=36), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["slot_id"], ["slots.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slot_id"),
    )
    with op.batch_alter_table("booking_slots", schema=None) as batch_op:
        batch_op.create_index("ix_booking_slots_unique", ["booking_id", "slot_id"], unique=True)

    op.create_table(
        "reviews",
        sa.Column("booking_id", sa.String(length=36), nullable=False),
        sa.Column("reviewer_id", sa.String(length=36), nullable=False),
        sa.Column("reviewed_id", sa.String(length=36), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewed_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewer_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("booking_id", "reviewer_id", name="uq_reviews_booking_reviewer"),
    )
    with op.batch_alter_table("reviews", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_reviews_booking_id"), ["booking_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_reviews_reviewed_id"), ["reviewed_id"], unique=False)
        batch_op.create_index("ix_reviews_reviewed_rating", ["reviewed_id", "rating"], unique=False)
        batch_op.create_index(batch_op.f("ix_reviews_reviewer_id"), ["reviewer_id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("reviews", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_reviews_reviewer_id"))
        batch_op.drop_index("ix_reviews_reviewed_rating")
        batch_op.drop_index(batch_op.f("ix_reviews_reviewed_id"))
        batch_op.drop_index(batch_op.f("ix_reviews_booking_id"))

    op.drop_table("reviews")
    with op.batch_alter_table("booking_slots", schema=None) as batch_op:
        batch_op.drop_index("ix_booking_slots_unique")

    op.drop_table("booking_slots")
    with op.batch_alter_table("booking_messages", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_booking_messages_sender_id"))
        batch_op.drop_index(batch_op.f("ix_booking_messages_booking_id"))
        batch_op.drop_index("ix_booking_messages_booking_created")

    op.drop_table("booking_messages")
    with op.batch_alter_table("student_penalties", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_student_penalties_student_id"))

    op.drop_table("student_penalties")
    with op.batch_alter_table("slots", schema=None) as batch_op:
        batch_op.drop_index("ix_slots_instructor_starts")
        batch_op.drop_index(batch_op.f("ix_slots_instructor_id"))

    op.drop_table("slots")
    with op.batch_alter_table("instructor_documents", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_instructor_documents_instructor_id"))

    op.drop_table("instructor_documents")
    with op.batch_alter_table("bookings", schema=None) as batch_op:
        batch_op.drop_index("ix_bookings_student_status")
        batch_op.drop_index(batch_op.f("ix_bookings_student_id"))
        batch_op.drop_index("ix_bookings_instructor_status")
        batch_op.drop_index(batch_op.f("ix_bookings_instructor_id"))

    op.drop_table("bookings")
    with op.batch_alter_table("student_profiles", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_student_profiles_slug"))

    op.drop_table("student_profiles")
    with op.batch_alter_table("instructor_profiles", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_instructor_profiles_slug"))
        batch_op.drop_index(batch_op.f("ix_instructor_profiles_detran_status"))

    op.drop_table("instructor_profiles")
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_users_email"))

    op.drop_table("users")

    # Native enum types (PostgreSQL) outlive their tables; no-op on SQLite.
    sa.Enum(name="licensetype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="detranstatus").drop(op.get_bind(), checkfirst=True)
