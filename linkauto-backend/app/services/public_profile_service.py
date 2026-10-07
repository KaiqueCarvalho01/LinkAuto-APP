"""Public, slug-addressed instructor and student profiles with their received reviews."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.core.slug import generate_profile_slug
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
    from sqlalchemy.orm import Session


class PublicProfileService:
    """Build public profile responses, generating missing profile slugs on demand."""

    def __init__(self, db: Session) -> None:
        """Store the DB session used for profile and review queries."""
        self._db = db

    def _ensure_instructor_slug(self, prof: InstructorProfile) -> str:
        if not prof.slug:
            slug = generate_profile_slug(prof.full_name, prof.city, default_prefix="instrutor")
            prof.slug = slug
            self._db.flush()
            return slug
        return prof.slug

    def _ensure_student_slug(self, prof: StudentProfile) -> str:
        if not prof.slug:
            slug = generate_profile_slug(prof.full_name, prof.city, default_prefix="aluno")
            prof.slug = slug
            self._db.flush()
            return slug
        return prof.slug

    def _get_reviewer_author(self, reviewer_id: str) -> PublicReviewAuthor:
        # Check student profile first
        stud = self._db.query(StudentProfile).filter(StudentProfile.user_id == reviewer_id).first()
        if stud and stud.full_name:
            slug = self._ensure_student_slug(stud)
            return PublicReviewAuthor(
                id=slug,
                slug=slug,
                full_name=stud.full_name,
                avatar_url=stud.avatar_url,
            )

        # Check instructor profile
        inst = (
            self._db.query(InstructorProfile)
            .filter(InstructorProfile.user_id == reviewer_id)
            .first()
        )
        if inst and inst.full_name:
            slug = self._ensure_instructor_slug(inst)
            return PublicReviewAuthor(
                id=slug,
                slug=slug,
                full_name=inst.full_name,
                avatar_url=inst.avatar_url,
            )

        # Fallback
        user = self._db.query(User).filter(User.id == reviewer_id).first()
        name = user.email.split("@")[0] if user and user.email else "Usuário LinkAuto"
        fallback_slug = f"usuario-{reviewer_id[:8]}"
        return PublicReviewAuthor(
            id=fallback_slug, slug=fallback_slug, full_name=name, avatar_url=None
        )

    def get_public_instructor(self, slug: str) -> PublicInstructorProfileResponse:
        """Return the public profile and reviews of an active, DETRAN-approved instructor.

        Lookup is by slug only (raw user IDs are not accepted). Raises ``ValueError`` if no
        active, approved instructor matches.
        """
        # STRICT: Lookup strictly by slug. Raw UUIDs are rejected with 404
        prof = (
            self._db.query(InstructorProfile)
            .filter(
                InstructorProfile.slug == slug,
                InstructorProfile.detran_status == DetranStatus.APROVADO.value,
                InstructorProfile.is_active.is_(True),
            )
            .first()
        )
        if not prof:
            msg = "Instructor not found or not approved"
            raise ValueError(msg)

        user = (
            self._db.query(User).filter(User.id == prof.user_id, User.is_active.is_(True)).first()
        )
        if not user:
            msg = "Instructor not found or not approved"
            raise ValueError(msg)

        raw_reviews = (
            self._db.query(Review)
            .filter(Review.reviewed_id == prof.user_id)
            .order_by(Review.created_at.desc())
            .all()
        )

        review_items: list[PublicReviewItem] = []
        for r in raw_reviews:
            author = self._get_reviewer_author(r.reviewer_id)
            created_at_str = (
                r.created_at.isoformat().replace("+00:00", "Z")
                if hasattr(r, "created_at") and r.created_at
                else ""
            )
            review_items.append(
                PublicReviewItem(
                    id=r.id,
                    reviewer=author,
                    rating=r.rating,
                    comment=r.comment,
                    created_at=created_at_str,
                )
            )

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
        prof = self._db.query(StudentProfile).filter(StudentProfile.slug == slug).first()
        if not prof:
            msg = "Student not found"
            raise ValueError(msg)

        user = (
            self._db.query(User).filter(User.id == prof.user_id, User.is_active.is_(True)).first()
        )
        if not user:
            msg = "Student not found"
            raise ValueError(msg)

        completed_lessons = (
            self._db.query(Booking)
            .filter(Booking.student_id == prof.user_id, Booking.status == "REALIZADA")
            .count()
        )

        raw_reviews = (
            self._db.query(Review)
            .filter(Review.reviewed_id == prof.user_id)
            .order_by(Review.created_at.desc())
            .all()
        )

        review_items: list[PublicReviewItem] = []
        total_rating = 0
        for r in raw_reviews:
            total_rating += r.rating
            author = self._get_reviewer_author(r.reviewer_id)
            created_at_str = (
                r.created_at.isoformat().replace("+00:00", "Z")
                if hasattr(r, "created_at") and r.created_at
                else ""
            )
            review_items.append(
                PublicReviewItem(
                    id=r.id,
                    reviewer=author,
                    rating=r.rating,
                    comment=r.comment,
                    created_at=created_at_str,
                )
            )

        rating_count = len(raw_reviews)
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
