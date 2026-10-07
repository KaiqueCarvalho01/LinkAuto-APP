"""GET /users/public-instructors exposes only public-safe fields, keyed by slug (#14)."""

from typing import TYPE_CHECKING

from app.models import DetranStatus
from tests.factories import seed_instructor

if TYPE_CHECKING:
    from fastapi.testclient import TestClient
    from sqlmodel import Session

PUBLIC_KEYS = {
    "id",
    "slug",
    "full_name",
    "avatar_url",
    "city",
    "state",
    "bio",
    "specialties",
    "price_per_hour",
    "rating_avg",
    "rating_count",
    "latitude",
    "longitude",
    "action_radius_km",
}


def test_public_instructors_do_not_leak_private_data(
    client: TestClient, db_session: Session
) -> None:
    seed_instructor(
        db_session,
        "4d0e7d2c-0000-7000-8000-000000000001",
        slug="leaky-c-1a2b",
        full_name="Leaky",
        phone="19999990000",
        city="C",
        state="SP",
        price_per_hour=70,
    )
    db_session.commit()

    resp = client.get("/api/v1/users/public-instructors")

    assert resp.status_code == 200
    items = resp.json()["data"]
    assert len(items) == 1
    item = items[0]
    assert set(item) == PUBLIC_KEYS
    assert item["id"] == item["slug"] == "leaky-c-1a2b"
    assert item["price_per_hour"] == 70.0
    raw = resp.text
    for secret in ("4d0e7d2c-0000-7000-8000-000000000001", "@seed.test", "19999990000"):
        assert secret not in raw
    for private_field in ("email", "phone", "detran_status", "is_active", "instructor_profile"):
        assert private_field not in raw


def test_public_instructors_generate_missing_slugs(client: TestClient, db_session: Session) -> None:
    seed_instructor(db_session, "inst-no-slug", full_name="Sem Slug", city="Mogi Mirim")
    db_session.commit()

    item = client.get("/api/v1/users/public-instructors").json()["data"][0]

    assert item["slug"].startswith("sem-slug-mogi-mirim-")
    assert "inst-no-slug" not in item["slug"]


def test_public_instructors_hide_pending_and_inactive(
    client: TestClient, db_session: Session
) -> None:
    seed_instructor(db_session, "pending", slug="p-1", detran_status=DetranStatus.PENDENTE)
    seed_instructor(db_session, "paused", slug="p-2", is_active=False)
    db_session.commit()

    assert client.get("/api/v1/users/public-instructors").json()["data"] == []


def test_booking_exposes_instructor_public_summary_to_participants(
    client: TestClient, db_session: Session
) -> None:
    from datetime import UTC, datetime, timedelta  # noqa: PLC0415

    from app.models import Slot  # noqa: PLC0415
    from tests.factories import auth_headers, seed_student  # noqa: PLC0415

    seed_instructor(
        db_session, "inst-b", slug="camila-x-1", full_name="Camila", city="Mogi", state="SP"
    )
    student = seed_student(db_session, "stu-b")
    start = datetime.now(UTC) + timedelta(days=2)
    slots = [
        Slot(
            instructor_id="inst-b",
            starts_at=start + timedelta(hours=i),
            ends_at=start + timedelta(hours=i + 1),
        )
        for i in range(2)
    ]
    db_session.add_all(slots)
    db_session.commit()

    resp = client.post(
        "/api/v1/bookings",
        json={"instructor_id": "camila-x-1", "slot_ids": [s.id for s in slots]},
        headers=auth_headers(student.user),
    )

    assert resp.status_code == 201
    assert resp.json()["data"]["instructor"] == {
        "slug": "camila-x-1",
        "full_name": "Camila",
        "avatar_url": None,
        "city": "Mogi",
        "state": "SP",
    }
