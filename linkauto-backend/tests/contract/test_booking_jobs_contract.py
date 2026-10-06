from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import pytest

from app.core.config import get_settings
from app.core.security import create_access_token
from app.models.booking import Booking, BookingSlot
from app.models.slot import Slot, SlotStatus
from app.models.user import DetranStatus, InstructorProfile, StudentProfile, User, UserRole

if TYPE_CHECKING:
    from fastapi.testclient import TestClient
    from sqlmodel import Session

JOB_SUMMARY_KEYS = {"processed", "booking_ids", "failed", "failed_booking_ids"}


@pytest.fixture
def admin_headers() -> dict[str, str]:
    token = create_access_token("admin-1", get_settings(), roles=[UserRole.ADMIN.value])
    return {"Authorization": f"Bearer {token}"}


def _seed_booking(
    db_session: Session,
    *,
    status: str,
    starts_in: timedelta,
    created_ago: timedelta = timedelta(0),
) -> str:
    db_session.add_all(
        [
            User(id="job-inst", email="jobinst@t.com", password_hash="h", roles=["INSTRUTOR"]),
            User(id="job-stu", email="jobstu@t.com", password_hash="h", roles=["ALUNO"]),
        ]
    )
    db_session.flush()
    db_session.add_all(
        [
            InstructorProfile(
                user_id="job-inst", full_name="I", detran_status=DetranStatus.APROVADO
            ),
            StudentProfile(user_id="job-stu", full_name="S"),
        ]
    )
    start = datetime.now(UTC) + starts_in
    slots = [
        Slot(
            instructor_id="job-inst",
            starts_at=start + timedelta(hours=i),
            ends_at=start + timedelta(hours=i + 1),
            status=SlotStatus.RESERVADO.value,
        )
        for i in range(2)
    ]
    db_session.add_all(slots)
    db_session.flush()
    booking = Booking(
        id="job-booking",
        student_id="job-stu",
        instructor_id="job-inst",
        status=status,
        created_at=datetime.now(UTC) - created_ago,
    )
    db_session.add(booking)
    db_session.flush()
    db_session.add_all(BookingSlot(booking_id=booking.id, slot_id=slot.id) for slot in slots)
    db_session.commit()
    return booking.id


def test_booking_timeout_cancels_expired_pending_bookings(
    client: TestClient, db_session: Session, admin_headers: dict[str, str]
) -> None:
    booking_id = _seed_booking(
        db_session, status="PENDENTE", starts_in=timedelta(days=2), created_ago=timedelta(days=2)
    )

    resp = client.post("/api/v1/jobs/booking-timeout", headers=admin_headers)

    assert resp.status_code == 200
    assert resp.json()["data"] == {
        "processed": 1,
        "booking_ids": [booking_id],
        "failed": 0,
        "failed_booking_ids": [],
    }
    db_session.expire_all()
    booking = db_session.get(Booking, booking_id)
    assert booking is not None
    assert booking.status == "CANCELADA"


def test_booking_completion_reports_completed_bookings(
    client: TestClient, db_session: Session, admin_headers: dict[str, str]
) -> None:
    booking_id = _seed_booking(db_session, status="CONFIRMADA", starts_in=-timedelta(hours=5))

    resp = client.post("/api/v1/jobs/booking-completion", headers=admin_headers)

    assert resp.status_code == 200
    assert resp.json()["data"] == {
        "processed": 1,
        "booking_ids": [booking_id],
        "failed": 0,
        "failed_booking_ids": [],
    }
    db_session.expire_all()
    booking = db_session.get(Booking, booking_id)
    assert booking is not None
    assert booking.status == "REALIZADA"


@pytest.mark.parametrize("job", ["booking-timeout", "booking-completion", "booking-reminder"])
def test_jobs_share_the_summary_shape(
    client: TestClient, admin_headers: dict[str, str], job: str
) -> None:
    resp = client.post(f"/api/v1/jobs/{job}", headers=admin_headers)

    assert resp.status_code == 200
    assert set(resp.json()["data"]) == JOB_SUMMARY_KEYS


@pytest.mark.parametrize("job", ["booking-timeout", "booking-completion", "booking-reminder"])
def test_jobs_require_admin(client: TestClient, job: str) -> None:
    token = create_access_token("stu-1", get_settings(), roles=[UserRole.ALUNO.value])

    resp = client.post(f"/api/v1/jobs/{job}", headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 403
