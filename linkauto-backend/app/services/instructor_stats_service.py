"""Dashboard statistics for an instructor's bookings."""

from typing import TYPE_CHECKING

from sqlalchemy import func
from sqlmodel import col, select

from app.models.booking import Booking, BookingSlot
from app.schemas.instructor_stats import InstructorStatsResponse

if TYPE_CHECKING:
    from sqlmodel import Session


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
        total_lessons = self._db.exec(
            select(func.count(col(Booking.id))).where(
                col(Booking.instructor_id) == instructor_id,
                col(Booking.status) == "REALIZADA",
            )
        ).one()

        total_hours = self._db.exec(
            select(func.count(col(BookingSlot.id)))
            .join(Booking, col(BookingSlot.booking_id) == col(Booking.id))
            .where(
                col(Booking.instructor_id) == instructor_id,
                col(Booking.status) == "REALIZADA",
            )
        ).one()

        unique_students = self._db.exec(
            select(func.count(func.distinct(col(Booking.student_id)))).where(
                col(Booking.instructor_id) == instructor_id,
                col(Booking.status) != "CANCELADA",
            )
        ).one()

        pending_bookings = self._db.exec(
            select(func.count(col(Booking.id))).where(
                col(Booking.instructor_id) == instructor_id,
                col(Booking.status) == "PENDENTE",
            )
        ).one()

        return InstructorStatsResponse(
            total_lessons=total_lessons,
            total_hours=total_hours,
            unique_students=unique_students,
            pending_bookings=pending_bookings,
        )
