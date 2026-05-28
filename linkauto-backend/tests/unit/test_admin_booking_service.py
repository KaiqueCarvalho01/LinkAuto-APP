import pytest

from app.domain.booking import BookingStatus
from app.models.booking import Booking
from app.models.user import (
    DetranStatus, InstructorProfile, StudentProfile, User, UserRole,
)
from app.services.admin_booking_service import AdminBookingService


def _seed_booking(db_session):
    inst = User(id="inst-admin", email="instadm@t.com", password_hash="h", roles=[UserRole.INSTRUTOR.value])
    inst_p = InstructorProfile(user_id="inst-admin", full_name="I", phone="1", city="C", state="SP", detran_status=DetranStatus.APROVADO)
    stu = User(id="stu-admin", email="stuadm@t.com", password_hash="h", roles=[UserRole.ALUNO.value])
    stu_p = StudentProfile(user_id="stu-admin", full_name="S", phone="2", city="C", state="SP")
    booking = Booking(
        student_id="stu-admin",
        instructor_id="inst-admin",
        status=BookingStatus.CANCELADA.value,
    )
    db_session.add_all([inst, inst_p, stu, stu_p, booking])
    db_session.flush()
    return booking


class TestAdminBookingOverride:
    def test_admin_overrides_terminal_to_terminal(self, db_session):
        booking = _seed_booking(db_session)
        service = AdminBookingService(db_session)

        result = service.override_status(
            booking.id,
            target_status="REALIZADA",
            reason="Correction by admin",
        )

        assert result.status == BookingStatus.REALIZADA.value

    def test_admin_override_rejects_non_terminal(self, db_session):
        booking = _seed_booking(db_session)
        service = AdminBookingService(db_session)

        with pytest.raises(ValueError, match="REALIZADA or CANCELADA"):
            service.override_status(booking.id, "CONFIRMADA", "invalid")
