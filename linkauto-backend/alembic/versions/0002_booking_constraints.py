"""Add Slot, Booking, BookingSlot, StudentPenalty tables

Revision ID: 0002_booking
Revises: 0001_foundation
Create Date: 2026-05-27
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_booking"
down_revision = "0001_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "slots",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("instructor_id", sa.String(36), sa.ForeignKey("instructor_profiles.user_id"), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="DISPONIVEL"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_slots_instructor_id", "slots", ["instructor_id"])
    op.create_index("ix_slots_instructor_starts", "slots", ["instructor_id", "starts_at"])

    op.create_table(
        "bookings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("student_id", sa.String(36), sa.ForeignKey("student_profiles.user_id"), nullable=False),
        sa.Column("instructor_id", sa.String(36), sa.ForeignKey("instructor_profiles.user_id"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="PENDENTE"),
        sa.Column("location_description", sa.Text, nullable=True),
        sa.Column("latitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("longitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_by", sa.String(20), nullable=True),
        sa.Column("cancellation_reason", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_bookings_student_id", "bookings", ["student_id"])
    op.create_index("ix_bookings_instructor_id", "bookings", ["instructor_id"])
    op.create_index("ix_bookings_student_status", "bookings", ["student_id", "status"])
    op.create_index("ix_bookings_instructor_status", "bookings", ["instructor_id", "status"])

    op.create_table(
        "booking_slots",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("booking_id", sa.String(36), sa.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("slot_id", sa.String(36), sa.ForeignKey("slots.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_booking_slots_unique", "booking_slots", ["booking_id", "slot_id"], unique=True)

    op.create_table(
        "student_penalties",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("student_id", sa.String(36), sa.ForeignKey("student_profiles.user_id"), nullable=False),
        sa.Column("blocked_until", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_student_penalties_student_id", "student_penalties", ["student_id"])


def downgrade() -> None:
    op.drop_table("student_penalties")
    op.drop_table("booking_slots")
    op.drop_table("bookings")
    op.drop_table("slots")
