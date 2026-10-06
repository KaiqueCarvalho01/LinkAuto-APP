"""Schemas for public instructor and student profile pages."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class PublicReviewAuthor(BaseModel):
    """Public identity of a review author; ``id`` is the public slug, not the user ID."""

    model_config = ConfigDict(extra="forbid")

    id: str
    slug: str
    full_name: str
    avatar_url: str | None = None


class PublicReviewItem(BaseModel):
    """Review shown on a public profile, with its author, 1-5 rating and ISO creation time."""

    model_config = ConfigDict(extra="forbid")

    id: str
    reviewer: PublicReviewAuthor
    rating: int
    comment: str | None = None
    created_at: str


class PublicInstructorProfileResponse(BaseModel):
    """Public profile of an active, DETRAN-approved instructor, looked up by slug.

    ``id`` is the slug. Includes listing details, aggregated rating and received reviews.
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    slug: str
    full_name: str
    avatar_url: str | None = None
    city: str | None = None
    state: str | None = None
    bio: str | None = None
    specialties: list[str] = []
    price_per_hour: float | None = None
    rating_avg: float = 5.0
    rating_count: int = 0
    detran_approved: bool = True
    reviews: list[PublicReviewItem] = []


class PublicStudentProfileResponse(BaseModel):
    """Public profile of an active student, looked up by slug.

    ``id`` is the slug. Includes license category, rating from received reviews, number of
    completed lessons and the reviews themselves.
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    slug: str
    full_name: str
    avatar_url: str | None = None
    city: str | None = None
    state: str | None = None
    license_type: str | None = None
    rating_avg: float = 5.0
    rating_count: int = 0
    completed_lessons_count: int = 0
    reviews: list[PublicReviewItem] = []
