"""Add BookingMessage and Review tables

Revision ID: 0003_messages_reviews
Revises: 0002_booking
Create Date: 2026-05-28
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_messages_reviews"
down_revision = "0002_booking"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add reminder_sent column to bookings table
    op.add_column("bookings", sa.Column("reminder_sent", sa.Boolean(), nullable=False, server_default=sa.text("false")))

    op.create_table(
        "booking_messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("booking_id", sa.String(36), sa.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sender_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_booking_messages_booking_id", "booking_messages", ["booking_id"])
    op.create_index("ix_booking_messages_booking_created", "booking_messages", ["booking_id", "created_at"])

    op.create_table(
        "reviews",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("booking_id", sa.String(36), sa.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reviewer_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reviewed_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rating", sa.Integer, nullable=False),
        sa.Column("comment", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("booking_id", "reviewer_id", name="uq_reviews_booking_reviewer"),
    )
    op.create_index("ix_reviews_booking_id", "reviews", ["booking_id"])
    op.create_index("ix_reviews_reviewed_id", "reviews", ["reviewed_id"])
    op.create_index("ix_reviews_reviewed_rating", "reviews", ["reviewed_id", "rating"])


def downgrade() -> None:
    op.drop_table("reviews")
    op.drop_table("booking_messages")
    op.drop_column("bookings", "reminder_sent")
