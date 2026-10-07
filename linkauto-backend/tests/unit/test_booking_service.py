from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import pytest

from app.domain.booking import BookingStatus
from app.models.slot import Slot, SlotStatus
from app.models.user import (
    DetranStatus,
    InstructorProfile,
    StudentProfile,
    User,
    UserRole,
)
from app.services.booking_service import (
    BookingAccessError,
    BookingNotFoundError,
    BookingService,
    PenalizedStudentError,
    SlotValidationError,
)
from app.services.notification_service import InMemoryEmailGateway, NotificationService
from app.services.penalty_service import PenaltyService

if TYPE_CHECKING:
    from sqlmodel import Session


def _seed_users(db_session: Session) -> None:
    instructor = User(
        id="inst-001", email="inst@test.com", password_hash="h", roles=[UserRole.INSTRUTOR.value]
    )
    inst_profile = InstructorProfile(
        user_id="inst-001",
        full_name="Inst",
        phone="1",
        city="C",
        state="SP",
        detran_status=DetranStatus.APROVADO,
    )
    student = User(
        id="stu-001", email="stu@test.com", password_hash="h", roles=[UserRole.ALUNO.value]
    )
    stu_profile = StudentProfile(
        user_id="stu-001", full_name="Stu", phone="2", city="C", state="SP"
    )
    db_session.add_all([instructor, inst_profile, student, stu_profile])
    db_session.flush()


def _create_consecutive_slots(
    db_session: Session, instructor_id: str, count: int = 2, base_offset_hours: int = 2
) -> list[Slot]:
    now = datetime.now(UTC)
    base = now + timedelta(hours=base_offset_hours)
    slots = []
    for i in range(count):
        s = Slot(
            instructor_id=instructor_id,
            starts_at=base + timedelta(hours=i),
            ends_at=base + timedelta(hours=i + 1),
            status=SlotStatus.DISPONIVEL.value,
        )
        db_session.add(s)
        slots.append(s)
    db_session.flush()
    return slots


class TestBookingServiceCreate:
    def test_creates_booking_with_2_consecutive_slots(self, db_session: Session) -> None:
        _seed_users(db_session)
        slots = _create_consecutive_slots(db_session, "inst-001", count=2)
        service = BookingService(db_session)

        booking = service.create_booking(
            student_id="stu-001",
            instructor_id="inst-001",
            slot_ids=[s.id for s in slots],
        )

        assert booking.status == BookingStatus.PENDENTE.value
        assert len(booking.slots) == 2
        for s in slots:
            db_session.refresh(s)
            assert s.status == SlotStatus.RESERVADO.value

    def test_rejects_less_than_2_slots(self, db_session: Session) -> None:
        _seed_users(db_session)
        slots = _create_consecutive_slots(db_session, "inst-001", count=1)
        service = BookingService(db_session)

        with pytest.raises(SlotValidationError, match="minimum 2"):
            service.create_booking("stu-001", "inst-001", [slots[0].id])

    def test_rejects_non_consecutive_slots(self, db_session: Session) -> None:
        _seed_users(db_session)
        now = datetime.now(UTC) + timedelta(hours=2)
        s1 = Slot(
            instructor_id="inst-001",
            starts_at=now,
            ends_at=now + timedelta(hours=1),
            status=SlotStatus.DISPONIVEL.value,
        )
        s2 = Slot(
            instructor_id="inst-001",
            starts_at=now + timedelta(hours=3),
            ends_at=now + timedelta(hours=4),
            status=SlotStatus.DISPONIVEL.value,
        )
        db_session.add_all([s1, s2])
        db_session.flush()
        service = BookingService(db_session)

        with pytest.raises(SlotValidationError, match="consecutive"):
            service.create_booking("stu-001", "inst-001", [s1.id, s2.id])

    def test_rejects_penalized_student(self, db_session: Session) -> None:
        _seed_users(db_session)

        PenaltyService(db_session).apply_penalty("stu-001", "test penalty")
        slots = _create_consecutive_slots(db_session, "inst-001")
        service = BookingService(db_session)

        with pytest.raises(PenalizedStudentError):
            service.create_booking("stu-001", "inst-001", [s.id for s in slots])


class TestBookingServiceConfirm:
    def test_confirms_pending_booking(self, db_session: Session) -> None:
        _seed_users(db_session)
        slots = _create_consecutive_slots(db_session, "inst-001")
        service = BookingService(db_session)
        booking = service.create_booking("stu-001", "inst-001", [s.id for s in slots])

        confirmed = service.confirm_booking(booking.id, "inst-001")

        assert confirmed.status == BookingStatus.CONFIRMADA.value
        assert confirmed.confirmed_at is not None

    def test_confirm_missing_booking_raises_not_found(self, db_session: Session) -> None:
        service = BookingService(db_session)

        with pytest.raises(BookingNotFoundError):
            service.confirm_booking("does-not-exist", "inst-001")

    def test_confirm_by_other_instructor_raises_access_error(self, db_session: Session) -> None:
        _seed_users(db_session)
        slots = _create_consecutive_slots(db_session, "inst-001")
        service = BookingService(db_session)
        booking = service.create_booking("stu-001", "inst-001", [s.id for s in slots])

        with pytest.raises(BookingAccessError):
            service.confirm_booking(booking.id, "other-inst")

        assert booking.status == BookingStatus.PENDENTE.value


class TestBookingServiceCancel:
    def test_cancel_with_24h_notice_no_penalty(self, db_session: Session) -> None:
        _seed_users(db_session)
        slots = _create_consecutive_slots(db_session, "inst-001", base_offset_hours=48)
        service = BookingService(db_session)
        booking = service.create_booking("stu-001", "inst-001", [s.id for s in slots])
        service.confirm_booking(booking.id, "inst-001")

        cancelled = service.cancel_booking(booking.id, "stu-001", "ALUNO")

        assert cancelled.status == BookingStatus.CANCELADA.value

        assert PenaltyService(db_session).is_penalized("stu-001") is False

    def test_cancel_within_24h_applies_penalty(self, db_session: Session) -> None:
        _seed_users(db_session)
        slots = _create_consecutive_slots(db_session, "inst-001", base_offset_hours=2)
        service = BookingService(db_session)
        booking = service.create_booking("stu-001", "inst-001", [s.id for s in slots])
        service.confirm_booking(booking.id, "inst-001")

        cancelled = service.cancel_booking(booking.id, "stu-001", "ALUNO")

        assert cancelled.status == BookingStatus.CANCELADA.value

        assert PenaltyService(db_session).is_penalized("stu-001") is True


class TestBookingServiceNotifications:
    def test_create_booking_dispatches_notification(self, db_session: Session) -> None:

        gateway = InMemoryEmailGateway()
        notification_svc = NotificationService(email_gateway=gateway)

        _seed_users(db_session)
        slots = _create_consecutive_slots(db_session, "inst-001")
        service = BookingService(db_session, notification_service=notification_svc)

        service.create_booking("stu-001", "inst-001", [s.id for s in slots])

        # Verify new pending booking notification sent to instructor
        assert len(gateway.sent_messages) == 1
        email = gateway.sent_messages[0]
        assert email["recipients"] == ["inst@test.com"]
        assert "pendente" in email["body"]

    def test_confirm_booking_dispatches_notification(self, db_session: Session) -> None:

        gateway = InMemoryEmailGateway()
        notification_svc = NotificationService(email_gateway=gateway)

        _seed_users(db_session)
        slots = _create_consecutive_slots(db_session, "inst-001")
        service = BookingService(db_session, notification_service=notification_svc)

        booking = service.create_booking("stu-001", "inst-001", [s.id for s in slots])
        gateway.sent_messages.clear()  # Clear create_booking notification

        service.confirm_booking(booking.id, "inst-001")

        # Verify confirmation notification sent to student
        assert len(gateway.sent_messages) == 1
        email = gateway.sent_messages[0]
        assert email["recipients"] == ["stu@test.com"]
        assert "confirmada" in email["body"]

    def test_cancel_booking_dispatches_notification(self, db_session: Session) -> None:

        gateway = InMemoryEmailGateway()
        notification_svc = NotificationService(email_gateway=gateway)

        _seed_users(db_session)
        slots = _create_consecutive_slots(db_session, "inst-001", base_offset_hours=48)
        service = BookingService(db_session, notification_service=notification_svc)

        booking = service.create_booking("stu-001", "inst-001", [s.id for s in slots])
        service.confirm_booking(booking.id, "inst-001")
        gateway.sent_messages.clear()

        service.cancel_booking(booking.id, "stu-001", "ALUNO", reason="Preciso cancelar")

        # Verify cancel notification sent to instructor
        assert len(gateway.sent_messages) == 1
        email = gateway.sent_messages[0]
        assert email["recipients"] == ["inst@test.com"]
        assert "cancelado" in email["body"]
        assert "Preciso cancelar" in email["body"]

    @pytest.mark.parametrize(
        ("cancelled_by", "user_id", "expected_recipients"),
        [
            ("ALUNO", "stu-001", ["inst@test.com"]),
            ("INSTRUTOR", "inst-001", ["stu@test.com"]),
            ("SISTEMA", "system", ["stu@test.com", "inst@test.com"]),
        ],
    )
    def test_cancel_booking_notifies_the_other_party(
        self,
        db_session: Session,
        cancelled_by: str,
        user_id: str,
        expected_recipients: list[str],
    ) -> None:
        gateway = InMemoryEmailGateway()
        _seed_users(db_session)
        slots = _create_consecutive_slots(db_session, "inst-001", base_offset_hours=48)
        service = BookingService(db_session, notification_service=NotificationService(gateway))
        booking = service.create_booking("stu-001", "inst-001", [s.id for s in slots])
        gateway.sent_messages.clear()

        service.cancel_booking(booking.id, user_id, cancelled_by)

        assert [m["recipients"] for m in gateway.sent_messages] == [expected_recipients]


class TestBookingServiceCancelAuthorization:
    def test_rejects_student_who_is_not_the_booking_student(self, db_session: Session) -> None:
        _seed_users(db_session)
        slots = _create_consecutive_slots(db_session, "inst-001", base_offset_hours=48)
        service = BookingService(db_session)
        booking = service.create_booking("stu-001", "inst-001", [s.id for s in slots])

        with pytest.raises(BookingAccessError):
            service.cancel_booking(booking.id, "intruder", "ALUNO")

        assert booking.status == BookingStatus.PENDENTE.value

    def test_rejects_instructor_who_is_not_the_booking_instructor(
        self, db_session: Session
    ) -> None:
        _seed_users(db_session)
        slots = _create_consecutive_slots(db_session, "inst-001", base_offset_hours=48)
        service = BookingService(db_session)
        booking = service.create_booking("stu-001", "inst-001", [s.id for s in slots])

        with pytest.raises(BookingAccessError):
            service.cancel_booking(booking.id, "other-inst", "INSTRUTOR")

        assert booking.status == BookingStatus.PENDENTE.value

    def test_booking_instructor_can_cancel(self, db_session: Session) -> None:
        _seed_users(db_session)
        slots = _create_consecutive_slots(db_session, "inst-001", base_offset_hours=48)
        service = BookingService(db_session)
        booking = service.create_booking("stu-001", "inst-001", [s.id for s in slots])

        cancelled = service.cancel_booking(booking.id, "inst-001", "INSTRUTOR")

        assert cancelled.status == BookingStatus.CANCELADA.value
