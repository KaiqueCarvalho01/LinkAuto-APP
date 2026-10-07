from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import pytest
from sqlmodel import col, select

from app.core.config import get_settings
from app.core.security import create_access_token
from app.domain.booking import BookingStatus
from app.models.booking import Booking, BookingSlot, BookingStatusOverride, CancelledBy
from app.models.slot import Slot, SlotStatus
from app.models.user import (
    DetranStatus,
    InstructorProfile,
    StudentProfile,
    User,
    UserRole,
)
from app.services.admin_booking_service import AdminBookingService
from app.services.booking_service import BookingNotFoundError
from app.services.notification_service import InMemoryEmailGateway, NotificationService

if TYPE_CHECKING:
    from fastapi.testclient import TestClient
    from sqlmodel import Session


def _seed_booking(db_session: Session, status: BookingStatus = BookingStatus.CANCELADA) -> Booking:
    inst = User(
        id="inst-admin", email="instadm@t.com", password_hash="h", roles=[UserRole.INSTRUTOR.value]
    )
    inst_p = InstructorProfile(
        user_id="inst-admin",
        full_name="I",
        phone="1",
        city="C",
        state="SP",
        detran_status=DetranStatus.APROVADO,
    )
    stu = User(
        id="stu-admin", email="stuadm@t.com", password_hash="h", roles=[UserRole.ALUNO.value]
    )
    stu_p = StudentProfile(user_id="stu-admin", full_name="S", phone="2", city="C", state="SP")
    booking = Booking(
        student_id="stu-admin",
        instructor_id="inst-admin",
        status=status.value,
    )
    db_session.add_all([inst, stu])
    db_session.flush()
    db_session.add_all([inst_p, stu_p])
    db_session.flush()
    db_session.add(booking)
    db_session.flush()
    return booking


def _reserve_future_slots(db_session: Session, booking: Booking) -> list[Slot]:
    start = datetime.now(UTC) + timedelta(days=2)
    slots = [
        Slot(
            instructor_id=booking.instructor_id,
            starts_at=start + timedelta(hours=i),
            ends_at=start + timedelta(hours=i + 1),
            status=SlotStatus.RESERVADO.value,
        )
        for i in range(2)
    ]
    db_session.add_all(slots)
    db_session.flush()
    db_session.add_all(BookingSlot(booking_id=booking.id, slot_id=s.id) for s in slots)
    db_session.flush()
    db_session.refresh(booking)
    return slots


class TestAdminBookingOverride:
    def test_admin_overrides_terminal_to_terminal(self, db_session: Session) -> None:
        booking = _seed_booking(db_session)
        service = AdminBookingService(db_session)

        result = service.override_status(
            booking.id,
            target_status="REALIZADA",
            reason="Correction by admin",
            admin_id="admin-1",
        )

        assert result.status == BookingStatus.REALIZADA.value

    def test_admin_override_rejects_non_terminal(self, db_session: Session) -> None:
        booking = _seed_booking(db_session)
        service = AdminBookingService(db_session)

        with pytest.raises(ValueError, match="REALIZADA or CANCELADA"):
            service.override_status(booking.id, "CONFIRMADA", "invalid", admin_id="admin-1")

    def test_admin_override_missing_booking_raises_not_found(self, db_session: Session) -> None:
        service = AdminBookingService(db_session)

        with pytest.raises(BookingNotFoundError):
            service.override_status("missing", "CANCELADA", "fraude", admin_id="admin-1")

    def test_override_records_audit_entry(self, db_session: Session) -> None:
        booking = _seed_booking(db_session, BookingStatus.CANCELADA)
        service = AdminBookingService(db_session)

        service.override_status(booking.id, "REALIZADA", "Aula ocorreu", admin_id="admin-1")

        entries = db_session.exec(
            select(BookingStatusOverride).where(col(BookingStatusOverride.booking_id) == booking.id)
        ).all()
        assert len(entries) == 1
        entry = entries[0]
        assert entry.admin_id == "admin-1"
        assert entry.from_status == BookingStatus.CANCELADA.value
        assert entry.to_status == BookingStatus.REALIZADA.value
        assert entry.reason == "Aula ocorreu"
        assert entry.created_at is not None

    def test_override_to_cancelada_sets_cancellation_fields(self, db_session: Session) -> None:
        booking = _seed_booking(db_session, BookingStatus.CONFIRMADA)
        service = AdminBookingService(db_session)

        result = service.override_status(
            booking.id, "CANCELADA", "Fraude confirmada", admin_id="admin-1"
        )

        assert result.status == BookingStatus.CANCELADA.value
        assert result.cancelled_by == CancelledBy.ADMIN.value
        assert result.cancellation_reason == "Fraude confirmada"
        assert result.cancelled_at is not None

    def test_override_to_cancelada_releases_future_slots_and_notifies(
        self, db_session: Session
    ) -> None:
        booking = _seed_booking(db_session, BookingStatus.CONFIRMADA)
        slots = _reserve_future_slots(db_session, booking)
        gateway = InMemoryEmailGateway()
        service = AdminBookingService(db_session, notification_service=NotificationService(gateway))

        service.override_status(booking.id, "CANCELADA", "Fraude confirmada", admin_id="admin-1")

        for slot in slots:
            db_session.refresh(slot)
            assert slot.status == SlotStatus.DISPONIVEL.value
        assert [m["recipients"] for m in gateway.sent_messages] == [
            ["stuadm@t.com", "instadm@t.com"]
        ]
        assert "Fraude confirmada" in gateway.sent_messages[0]["body"]

    def test_override_from_cancelada_to_realizada_clears_cancellation_fields(
        self, db_session: Session
    ) -> None:
        booking = _seed_booking(db_session, BookingStatus.CANCELADA)
        booking.cancelled_at = datetime.now(UTC)
        booking.cancelled_by = CancelledBy.SISTEMA.value
        booking.cancellation_reason = "timeout"
        db_session.flush()
        service = AdminBookingService(db_session)

        result = service.override_status(booking.id, "REALIZADA", "Aula ocorreu", admin_id="a")

        assert result.cancelled_at is None
        assert result.cancelled_by is None
        assert result.cancellation_reason is None


def test_override_endpoint_persists_reason_and_admin(
    client: TestClient, db_session: Session
) -> None:
    booking = _seed_booking(db_session, BookingStatus.CONFIRMADA)
    token = create_access_token("admin-42", settings=get_settings(), roles=["ADMIN"])

    resp = client.patch(
        f"/api/v1/admin/bookings/{booking.id}/override-status",
        json={"status": "CANCELADA", "reason": "Fraude confirmada"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["cancellation_reason"] == "Fraude confirmada"
    assert data["cancelled_by"] == "ADMIN"
    assert data["cancelled_at"] is not None
    entry = db_session.exec(
        select(BookingStatusOverride).where(col(BookingStatusOverride.booking_id) == booking.id)
    ).one()
    assert entry.admin_id == "admin-42"


def test_override_endpoint_missing_booking_returns_404(client: TestClient) -> None:
    token = create_access_token("admin-42", settings=get_settings(), roles=["ADMIN"])

    resp = client.patch(
        "/api/v1/admin/bookings/missing/override-status",
        json={"status": "CANCELADA", "reason": "Fraude"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 404
