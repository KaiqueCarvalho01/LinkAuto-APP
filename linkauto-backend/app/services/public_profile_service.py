"""Public, slug-addressed instructor and student profiles with their received reviews."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import func
from sqlmodel import col, select

from app.models.booking import Booking
from app.models.review import Review
from app.models.user import DetranStatus, InstructorProfile, StudentProfile, User
from app.schemas.public_profile import (
    PublicInstructorProfileResponse,
    PublicReviewAuthor,
    PublicReviewItem,
    PublicStudentProfileResponse,
)

if TYPE_CHECKING:
    from sqlmodel import Session


ANONYMOUS_NAME = "Usuário LinkAuto"
ANONYMOUS_SLUG = "usuario-linkauto"


class PublicProfileService:
    """Build public profile responses (profiles are addressed by their stored slugs)."""

    def __init__(self, db: Session) -> None:
        """Store the DB session used for profile and review queries."""
        self._db = db

    def _get_reviewer_author(self, reviewer_id: str) -> PublicReviewAuthor:
        # Check student profile first
        stud = self._db.exec(
            select(StudentProfile).where(col(StudentProfile.user_id) == reviewer_id)
        ).first()
        if stud and stud.full_name:
            slug = stud.slug
            return PublicReviewAuthor(
                id=slug,
                slug=slug,
                full_name=stud.full_name,
                avatar_url=stud.avatar_url,
            )

        # Check instructor profile
        inst = self._db.exec(
            select(InstructorProfile).where(col(InstructorProfile.user_id) == reviewer_id)
        ).first()
        if inst and inst.full_name:
            slug = inst.slug
            return PublicReviewAuthor(
                id=slug,
                slug=slug,
                full_name=inst.full_name,
                avatar_url=inst.avatar_url,
            )

        # No name on either profile: never fall back to the e-mail or the internal ID
        slug = (stud.slug if stud else None) or (inst.slug if inst else None) or ANONYMOUS_SLUG
        return PublicReviewAuthor(id=slug, slug=slug, full_name=ANONYMOUS_NAME, avatar_url=None)

    def _review_items(
        self, reviewed_id: str, *, offset: int = 0, limit: int | None = None
    ) -> list[PublicReviewItem]:
        """Return the public view of the reviews a user received, newest first."""
        stmt = (
            select(Review)
            .where(col(Review.reviewed_id) == reviewed_id)
            .order_by(col(Review.created_at).desc())
            .offset(offset)
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        return [
            PublicReviewItem(
                id=review.id,
                reviewer=self._get_reviewer_author(review.reviewer_id),
                rating=review.rating,
                comment=review.comment,
                created_at=review.created_at.isoformat().replace("+00:00", "Z"),
            )
            for review in self._db.exec(stmt).all()
        ]

    def list_instructor_reviews(
        self, slug: str, *, page: int = 1, page_size: int = 20
    ) -> list[PublicReviewItem]:
        """Return a page of the public reviews of an active, DETRAN-approved instructor.

        Lookup is by slug only, like the public profile. Raises ``ValueError`` if no active,
        approved instructor matches.
        """
        prof = self._find_public_instructor(slug)
        return self._review_items(prof.user_id, offset=(page - 1) * page_size, limit=page_size)

    def _find_public_instructor(self, slug: str) -> InstructorProfile:
        # STRICT: lookup by slug only; raw user IDs are rejected (404)
        prof = self._db.exec(
            select(InstructorProfile)
            .join(User, col(User.id) == col(InstructorProfile.user_id))
            .where(
                col(InstructorProfile.slug) == slug,
                col(InstructorProfile.detran_status) == DetranStatus.APROVADO.value,
                col(InstructorProfile.is_active).is_(True),
                col(User.is_active).is_(True),
            )
        ).first()
        if not prof:
            msg = "Instructor not found or not approved"
            raise ValueError(msg)
        return prof

    def get_public_instructor(self, slug: str) -> PublicInstructorProfileResponse:
        """Return the public profile and reviews of an active, DETRAN-approved instructor.

        Lookup is by slug only (raw user IDs are not accepted). Raises ``ValueError`` if no
        active, approved instructor matches.
        """
        prof = self._find_public_instructor(slug)
        review_items = self._review_items(prof.user_id)

        return PublicInstructorProfileResponse(
            id=slug,
            slug=slug,
            full_name=prof.full_name or "Instrutor",
            avatar_url=prof.avatar_url,
            city=prof.city,
            state=prof.state,
            bio=prof.bio,
            specialties=prof.specialties or [],
            price_per_hour=float(prof.price_per_hour) if prof.price_per_hour is not None else None,
            rating_avg=prof.rating_avg,
            rating_count=prof.rating_count,
            detran_approved=True,
            reviews=review_items,
        )

    def get_public_student(self, slug: str) -> PublicStudentProfileResponse:
        """Return an active student's public profile, completed lessons and reviews.

        Lookup is by slug only. The rating average is computed from the student's reviews
        (5.0 when there are none). Raises ``ValueError`` if no active student matches.
        """
        # STRICT: Lookup strictly by slug. Raw UUIDs are rejected with 404
        prof = self._db.exec(select(StudentProfile).where(col(StudentProfile.slug) == slug)).first()
        if not prof:
            msg = "Student not found"
            raise ValueError(msg)

        user = self._db.exec(
            select(User).where(col(User.id) == prof.user_id, col(User.is_active).is_(True))
        ).first()
        if not user:
            msg = "Student not found"
            raise ValueError(msg)

        completed_lessons = self._db.exec(
            select(func.count())
            .select_from(Booking)
            .where(col(Booking.student_id) == prof.user_id, col(Booking.status) == "REALIZADA")
        ).one()

        review_items = self._review_items(prof.user_id)
        total_rating = sum(item.rating for item in review_items)

        rating_count = len(review_items)
        rating_avg = round(total_rating / rating_count, 1) if rating_count > 0 else 5.0

        return PublicStudentProfileResponse(
            id=slug,
            slug=slug,
            full_name=prof.full_name or "Aluno",
            avatar_url=prof.avatar_url,
            city=prof.city,
            state=prof.state,
            license_type=prof.license_type.value
            if hasattr(prof.license_type, "value")
            else (str(prof.license_type) if prof.license_type else None),
            rating_avg=rating_avg,
            rating_count=rating_count,
            completed_lessons_count=completed_lessons,
            reviews=review_items,
        )
