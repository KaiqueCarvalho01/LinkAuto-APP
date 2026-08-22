from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.review import Review
from app.models.user import DetranStatus, InstructorProfile, StudentProfile, User
from app.schemas.public_profile import (
    PublicInstructorProfileResponse,
    PublicReviewAuthor,
    PublicReviewItem,
    PublicStudentProfileResponse,
)


class PublicProfileService:
    def __init__(self, db: Session):
        self._db = db

    def _get_reviewer_author(self, reviewer_id: str) -> PublicReviewAuthor:
        # Check student profile first
        stud = self._db.query(StudentProfile).filter(StudentProfile.user_id == reviewer_id).first()
        if stud and stud.full_name:
            return PublicReviewAuthor(
                id=reviewer_id,
                full_name=stud.full_name,
                avatar_url=stud.avatar_url,
            )

        # Check instructor profile
        inst = self._db.query(InstructorProfile).filter(InstructorProfile.user_id == reviewer_id).first()
        if inst and inst.full_name:
            return PublicReviewAuthor(
                id=reviewer_id,
                full_name=inst.full_name,
                avatar_url=inst.avatar_url,
            )

        # Fallback to user email prefix or generic label
        user = self._db.query(User).filter(User.id == reviewer_id).first()
        name = user.email.split("@")[0] if user and user.email else "Usuário LinkAuto"
        return PublicReviewAuthor(id=reviewer_id, full_name=name, avatar_url=None)

    def get_public_instructor(self, instructor_id: str) -> PublicInstructorProfileResponse:
        user = (
            self._db.query(User)
            .filter(User.id == instructor_id, User.is_active.is_(True))
            .first()
        )
        if not user:
            raise ValueError("Instructor not found or not approved")

        prof = (
            self._db.query(InstructorProfile)
            .filter(
                InstructorProfile.user_id == instructor_id,
                InstructorProfile.detran_status == DetranStatus.APROVADO.value,
                InstructorProfile.is_active.is_(True),
            )
            .first()
        )
        if not prof:
            raise ValueError("Instructor not found or not approved")

        raw_reviews = (
            self._db.query(Review)
            .filter(Review.reviewed_id == instructor_id)
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
            id=prof.user_id,
            full_name=prof.full_name or "Instrutor",
            avatar_url=prof.avatar_url,
            city=prof.city,
            state=prof.state,
            bio=prof.bio,
            specialties=prof.specialties or [],
            price_per_hour=float(prof.price_per_hour) if prof.price_per_hour is not None else None,
            rating_avg=float(prof.rating_avg) if prof.rating_avg is not None else 5.0,
            rating_count=prof.rating_count,
            detran_approved=True,
            reviews=review_items,
        )

    def get_public_student(self, student_id: str) -> PublicStudentProfileResponse:
        user = (
            self._db.query(User)
            .filter(User.id == student_id, User.is_active.is_(True))
            .first()
        )
        if not user:
            raise ValueError("Student not found")

        prof = (
            self._db.query(StudentProfile)
            .filter(StudentProfile.user_id == student_id)
            .first()
        )
        if not prof:
            raise ValueError("Student not found")

        completed_lessons = (
            self._db.query(Booking)
            .filter(Booking.student_id == student_id, Booking.status == "REALIZADA")
            .count()
        )

        raw_reviews = (
            self._db.query(Review)
            .filter(Review.reviewed_id == student_id)
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
            id=prof.user_id,
            full_name=prof.full_name or "Aluno",
            avatar_url=prof.avatar_url,
            city=prof.city,
            state=prof.state,
            license_type=prof.license_type.value if hasattr(prof.license_type, "value") else (str(prof.license_type) if prof.license_type else None),
            rating_avg=rating_avg,
            rating_count=rating_count,
            completed_lessons_count=completed_lessons,
            reviews=review_items,
        )
