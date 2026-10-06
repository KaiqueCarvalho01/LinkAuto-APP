"""Review model for rating the other party of a booking."""

from sqlalchemy import Index, String, Text, UniqueConstraint
from sqlmodel import Field

from app.models.base import AuditUUIDBase


class Review(AuditUUIDBase, table=True):
    """Rating and optional comment left by one user about another for a booking.

    Each reviewer can review a given booking only once.
    """

    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint("booking_id", "reviewer_id", name="uq_reviews_booking_reviewer"),
        Index("ix_reviews_reviewed_rating", "reviewed_id", "rating"),
    )

    booking_id: str = Field(
        sa_type=String(36), foreign_key="bookings.id", ondelete="CASCADE", index=True
    )
    reviewer_id: str = Field(
        sa_type=String(36), foreign_key="users.id", ondelete="CASCADE", index=True
    )
    reviewed_id: str = Field(
        sa_type=String(36), foreign_key="users.id", ondelete="CASCADE", index=True
    )
    rating: int
    comment: str | None = Field(default=None, sa_type=Text)
