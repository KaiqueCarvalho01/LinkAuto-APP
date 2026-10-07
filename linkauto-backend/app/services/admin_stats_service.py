"""Platform-wide statistics for the admin dashboard."""

from typing import TYPE_CHECKING

from sqlalchemy import func
from sqlmodel import col, select

from app.models.booking import Booking
from app.models.user import DetranStatus, InstructorProfile, StudentProfile
from app.schemas.admin_stats import AdminStatsResponse

if TYPE_CHECKING:
    from sqlmodel import Session


class AdminStatsService:
    """Aggregate instructor, student and booking counts for admins."""

    def __init__(self, db: Session) -> None:
        """Store the DB session used for the aggregate queries."""
        self._db = db

    def get_stats(self) -> AdminStatsResponse:
        """Return total instructors (also by DETRAN status), students and bookings."""
        total_instructors = self._db.exec(select(func.count(col(InstructorProfile.user_id)))).one()
        pending_instructors = self._db.exec(
            select(func.count(col(InstructorProfile.user_id))).where(
                col(InstructorProfile.detran_status) == DetranStatus.PENDENTE.value
            )
        ).one()
        approved_instructors = self._db.exec(
            select(func.count(col(InstructorProfile.user_id))).where(
                col(InstructorProfile.detran_status) == DetranStatus.APROVADO.value
            )
        ).one()
        rejected_instructors = self._db.exec(
            select(func.count(col(InstructorProfile.user_id))).where(
                col(InstructorProfile.detran_status) == DetranStatus.REJEITADO.value
            )
        ).one()
        total_students = self._db.exec(select(func.count(col(StudentProfile.user_id)))).one()
        total_bookings = self._db.exec(select(func.count(col(Booking.id)))).one()

        return AdminStatsResponse(
            total_instructors=total_instructors,
            pending_instructors=pending_instructors,
            approved_instructors=approved_instructors,
            rejected_instructors=rejected_instructors,
            total_students=total_students,
            total_bookings=total_bookings,
        )
