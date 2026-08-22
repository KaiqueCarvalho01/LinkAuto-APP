from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.booking import Booking, BookingSlot
from app.schemas.instructor_stats import InstructorStatsResponse


class InstructorStatsService:
    def __init__(self, db: Session):
        self._db = db

    def get_stats(self, instructor_id: str) -> InstructorStatsResponse:
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
