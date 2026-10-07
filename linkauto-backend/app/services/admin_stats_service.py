"""Platform-wide statistics for the admin dashboard."""

from typing import TYPE_CHECKING

from sqlalchemy import func

from app.models.booking import Booking
from app.models.user import DetranStatus, InstructorProfile, StudentProfile
from app.schemas.admin_stats import AdminStatsResponse

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AdminStatsService:
    """Aggregate instructor, student and booking counts for admins."""

    def __init__(self, db: Session) -> None:
        """Store the DB session used for the aggregate queries."""
        self._db = db

    def get_stats(self) -> AdminStatsResponse:
        """Return total instructors (also by DETRAN status), students and bookings."""
        total_instructors = self._db.query(func.count(InstructorProfile.user_id)).scalar() or 0
        pending_instructors = (
            self._db.query(func.count(InstructorProfile.user_id))
            .filter(InstructorProfile.detran_status == DetranStatus.PENDENTE.value)
            .scalar()
            or 0
        )
        approved_instructors = (
            self._db.query(func.count(InstructorProfile.user_id))
            .filter(InstructorProfile.detran_status == DetranStatus.APROVADO.value)
            .scalar()
            or 0
        )
        rejected_instructors = (
            self._db.query(func.count(InstructorProfile.user_id))
            .filter(InstructorProfile.detran_status == DetranStatus.REJEITADO.value)
            .scalar()
            or 0
        )
        total_students = self._db.query(func.count(StudentProfile.user_id)).scalar() or 0
        total_bookings = self._db.query(func.count(Booking.id)).scalar() or 0

        return AdminStatsResponse(
            total_instructors=total_instructors,
            pending_instructors=pending_instructors,
            approved_instructors=approved_instructors,
            rejected_instructors=rejected_instructors,
            total_students=total_students,
            total_bookings=total_bookings,
        )
