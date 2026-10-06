"""Reviews between students and instructors after completed lessons."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from app.domain.booking import BookingStatus
from app.models.booking import Booking
from app.models.review import Review
from app.models.user import InstructorProfile
from app.services.notification_service import (
    NotificationEvent,
    NotificationPayload,
    NotificationService,
)

if TYPE_CHECKING:
    from sqlmodel import Session

logger = logging.getLogger(__name__)


class ReviewAccessError(ValueError):
    """Raised when the reviewer did not take part in the booking."""


class ReviewStateError(ValueError):
    """Raised when reviewing a booking that is not REALIZADA."""


class ReviewDuplicateError(ValueError):
    """Raised when the reviewer has already reviewed the booking."""


class ReviewService:
    """Create and list reviews exchanged between students and instructors."""

    def __init__(
        self,
        db: Session,
        notification_service: NotificationService | None = None,
    ) -> None:
        """Store the database session and optional notification service."""
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
        """Create a review of the other participant of a REALIZADA booking.

        Reviews of the instructor update their profile's rating average and count. The reviewed
        user is emailed when ``recipient_email`` is given.

        Raises:
            ValueError: If the booking does not exist.
            ReviewStateError: If the booking is not REALIZADA.
            ReviewAccessError: If the reviewer is not a participant of the booking.
            ReviewDuplicateError: If the reviewer already reviewed this booking.

        """
        # Fetch booking to check existence, status and access
        booking = self._db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            msg = f"Booking {booking_id} not found"
            raise ValueError(msg)

        # SC-004 / FR-019: creation only when booking status is REALIZADA
        if booking.status != BookingStatus.REALIZADA.value:
            logger.warning(
                "Validation failed: Booking %s status is %s, must be REALIZADA to review",
                booking_id,
                booking.status,
            )
            msg = "Reviews can only be submitted for completed bookings"
            raise ReviewStateError(msg)

        # Validate access control
        if reviewer_id not in (booking.student_id, booking.instructor_id):
            logger.warning(
                "Access denied: User %s is not authorized to review booking %s",
                reviewer_id,
                booking_id,
            )
            msg = "You are not a participant in this booking"
            raise ReviewAccessError(msg)

        # FR-020: enforce one review per reviewer-reviewed pair per booking
        existing = (
            self._db.query(Review)
            .filter(Review.booking_id == booking_id, Review.reviewer_id == reviewer_id)
            .first()
        )
        if existing:
            logger.warning(
                "Validation failed: User %s has already reviewed booking %s",
                reviewer_id,
                booking_id,
            )
            msg = "You have already submitted a review for this booking"
            raise ReviewDuplicateError(msg)

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
                    body=(
                        f"Você recebeu uma nova avaliação de {reviewer_id}: {rating} estrelas. "
                        f"Comentário: '{comment or ''}'"
                    ),
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
        """Return a page of reviews received by the instructor, newest first."""
        offset = (page - 1) * page_size
        return (
            self._db.query(Review)
            .filter(Review.reviewed_id == instructor_id)
            .order_by(Review.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )
