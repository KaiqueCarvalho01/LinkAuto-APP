"""Reviews between students and instructors after completed lessons."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from sqlalchemy import func
from sqlmodel import col, select

from app.domain.booking import BookingStatus
from app.models.booking import Booking
from app.models.review import Review
from app.models.user import InstructorProfile
from app.services.booking_notifier import BookingNotifier

if TYPE_CHECKING:
    from sqlmodel import Session

    from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


def refresh_instructor_rating(db: Session, instructor_id: str) -> None:
    """Recompute an instructor's cached rating from the reviews they received as instructor.

    Only reviews of REALIZADA bookings count (a booking an admin later cancels drops out).
    The profile row is locked first (``SELECT ... FOR UPDATE`` on PostgreSQL), so two
    reviews saved at the same time can't overwrite each other's count: the second waits,
    then recomputes with both.
    """
    profile = db.exec(
        select(InstructorProfile)
        .where(col(InstructorProfile.user_id) == instructor_id)
        .with_for_update()
    ).first()
    if profile is None:
        return
    average, count = db.exec(
        select(func.avg(Review.rating), func.count(col(Review.id)))
        .join(Booking, col(Booking.id) == col(Review.booking_id))
        .where(
            col(Review.reviewed_id) == instructor_id,
            col(Booking.instructor_id) == instructor_id,
            col(Booking.status) == BookingStatus.REALIZADA.value,
        )
    ).one()
    profile.rating_count = count
    profile.rating_avg = float(average or 0.0)
    db.flush()


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
        self._notifier = BookingNotifier(db, notification_service)

    def create_review(
        self,
        booking_id: str,
        reviewer_id: str,
        rating: int,
        comment: str | None = None,
    ) -> Review:
        """Create a review of the other participant of a REALIZADA booking.

        Reviews of the instructor update their profile's rating average and count. The reviewed
        user is notified by e-mail.

        Raises:
            ValueError: If the booking does not exist.
            ReviewStateError: If the booking is not REALIZADA.
            ReviewAccessError: If the reviewer is not a participant of the booking.
            ReviewDuplicateError: If the reviewer already reviewed this booking.

        """
        # Fetch booking to check existence, status and access
        booking = self._db.exec(select(Booking).where(col(Booking.id) == booking_id)).first()
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
        existing = self._db.exec(
            select(Review).where(
                col(Review.booking_id) == booking_id, col(Review.reviewer_id) == reviewer_id
            )
        ).first()
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

        # Reviews of the instructor feed their cached rating average (search and profile)
        if reviewed_id == booking.instructor_id:
            refresh_instructor_rating(self._db, reviewed_id)

        # E-mail the reviewed participant
        self._notifier.review_received(
            booking, reviewer_id=reviewer_id, rating=rating, comment=comment
        )

        return review
