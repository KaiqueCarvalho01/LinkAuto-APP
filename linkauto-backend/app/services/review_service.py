from __future__ import annotations

import logging
from sqlalchemy.orm import Session

from app.domain.booking import BookingStatus
from app.models.booking import Booking
from app.models.user import InstructorProfile
from app.models.review import Review
from app.services.notification_service import NotificationService, NotificationPayload, NotificationEvent

logger = logging.getLogger(__name__)


class ReviewAccessError(ValueError):
    pass


class ReviewStateError(ValueError):
    pass


class ReviewDuplicateError(ValueError):
    pass


class ReviewService:
    def __init__(
        self,
        db: Session,
        notification_service: NotificationService | None = None,
    ) -> None:
        self._db = db
        self._notification_service = notification_service

    def create_review(
        self,
        booking_id: str,
        reviewer_id: str,
        rating: int,
        comment: str | None = None,
        recipient_email: str | None = None,
    ) -> Review:
        # Fetch booking to check existence, status and access
        booking = self._db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise ValueError(f"Booking {booking_id} not found")

        # SC-004 / FR-019: creation only when booking status is REALIZADA
        if booking.status != BookingStatus.REALIZADA.value:
            logger.warning(
                f"Validation failed: Booking {booking_id} status is {booking.status}, must be REALIZADA to review"
            )
            raise ReviewStateError("Reviews can only be submitted for completed bookings")

        # Validate access control
        if reviewer_id not in (booking.student_id, booking.instructor_id):
            logger.warning(
                f"Access denied: User {reviewer_id} is not authorized to review booking {booking_id}"
            )
            raise ReviewAccessError("You are not a participant in this booking")

        # FR-020: enforce one review per reviewer-reviewed pair per booking
        existing = (
            self._db.query(Review)
            .filter(Review.booking_id == booking_id, Review.reviewer_id == reviewer_id)
            .first()
        )
        if existing:
            logger.warning(
                f"Validation failed: User {reviewer_id} has already reviewed booking {booking_id}"
            )
            raise ReviewDuplicateError("You have already submitted a review for this booking")

        # Determine reviewed user id (the other participant)
        reviewed_id = (
            booking.instructor_id if reviewer_id == booking.student_id else booking.student_id
        )

        # Create review
        review = Review(
            booking_id=booking_id,
            reviewer_id=reviewer_id,
            reviewed_id=reviewed_id,
            rating=rating,
            comment=comment,
        )
        self._db.add(review)
        self._db.flush()

        # If reviewed is the instructor, update their average rating and count on InstructorProfile
        if reviewed_id == booking.instructor_id:
            profile = (
                self._db.query(InstructorProfile)
                .filter(InstructorProfile.user_id == reviewed_id)
                .first()
            )
            if profile:
                current_count = profile.rating_count
                current_avg = float(profile.rating_avg)
                
                new_count = current_count + 1
                new_avg = ((current_avg * current_count) + rating) / new_count
                
                profile.rating_count = new_count
                profile.rating_avg = new_avg
                self._db.flush()

        # Dispatch e-mail notification
        if self._notification_service and recipient_email:
            self._notification_service.dispatch(
                NotificationPayload(
                    event=NotificationEvent.NEW_REVIEW_RECEIVED,
                    subject="Nova avaliação recebida",
                    body=f"Você recebeu uma nova avaliação de {reviewer_id}: {rating} estrelas. Comentário: '{comment or ''}'",
                    recipients=[recipient_email],
                )
            )

        return review

    def list_instructor_reviews(
        self,
        instructor_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> list[Review]:
        offset = (page - 1) * page_size
        return (
            self._db.query(Review)
            .filter(Review.reviewed_id == instructor_id)
            .order_by(Review.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )
