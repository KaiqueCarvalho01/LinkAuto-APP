"""Dashboard statistics for an instructor's bookings."""

from typing import TYPE_CHECKING

from sqlalchemy import func

from app.models.booking import Booking, BookingSlot
from app.schemas.instructor_stats import InstructorStatsResponse

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class InstructorStatsService:
    """Aggregate booking counts for an instructor's dashboard."""

    def __init__(self, db: Session) -> None:
        """Store the DB session used for the aggregate queries."""
        self._db = db

    def get_stats(self, instructor_id: str) -> InstructorStatsResponse:
        """Return the instructor's lesson, hour, student and pending-booking counts.

        Lessons and hours count only REALIZADA bookings (one hour per booked slot), unique
        students exclude CANCELADA bookings, and pending counts PENDENTE bookings.
        """
        total_lessons = (
            self._db.query(func.count(Booking.id))
            .filter(
                Booking.instructor_id == instructor_id,
                Booking.status == "REALIZADA",
            )
            .scalar()
            or 0
        )

        total_hours = (
            self._db.query(func.count(BookingSlot.id))
            .join(Booking, BookingSlot.booking_id == Booking.id)
            .filter(
                Booking.instructor_id == instructor_id,
                Booking.status == "REALIZADA",
            )
            .scalar()
            or 0
        )

        unique_students = (
            self._db.query(func.count(func.distinct(Booking.student_id)))
            .filter(
                Booking.instructor_id == instructor_id,
                Booking.status != "CANCELADA",
            )
            .scalar()
            or 0
        )

        pending_bookings = (
            self._db.query(func.count(Booking.id))
            .filter(
                Booking.instructor_id == instructor_id,
                Booking.status == "PENDENTE",
            )
            .scalar()
            or 0
        )

        return InstructorStatsResponse(
            total_lessons=total_lessons,
            total_hours=total_hours,
            unique_students=unique_students,
            pending_bookings=pending_bookings,
        )
