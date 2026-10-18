"""Public endpoints never expose internal user IDs or e-mails (#76)."""

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from app.models import Booking, Review, Slot
from tests.factories import seed_instructor, seed_student

if TYPE_CHECKING:
    from fastapi.testclient import TestClient
    from sqlmodel import Session

INSTRUCTOR_ID = "01a1-instructor-internal-id"
REVIEWER_ID = "01a1-reviewer-internal-id"


def _seed(db_session: Session, *, reviewer_name: str | None) -> str:
    instructor = seed_instructor(db_session, INSTRUCTOR_ID, full_name="Ana", city="Mogi")
    reviewer = seed_student(db_session, REVIEWER_ID, full_name=reviewer_name)
    assert reviewer.user is not None
    reviewer.user.email = "secret.person@test.com"
    start = datetime.now(UTC) + timedelta(days=1)
    db_session.add(
        Slot(instructor_id=INSTRUCTOR_ID, starts_at=start, ends_at=start + timedelta(hours=1))
    )
    booking = Booking(student_id=REVIEWER_ID, instructor_id=INSTRUCTOR_ID, status="REALIZADA")
    db_session.add(booking)
    db_session.flush()
    db_session.add(
        Review(
            booking_id=booking.id,
            reviewer_id=REVIEWER_ID,
            reviewed_id=INSTRUCTOR_ID,
            rating=5,
            comment="Ótima aula",
        )
    )
    db_session.commit()
    return instructor.slug


def test_public_slots_do_not_expose_the_instructor_id(
    client: TestClient, db_session: Session
) -> None:
    slug = _seed(db_session, reviewer_name="Bia")

    resp = client.get(f"/api/v1/instructors/{slug}/slots")

    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] == 1
    assert set(resp.json()["data"][0]) == {"id", "starts_at", "ends_at", "status"}
    assert INSTRUCTOR_ID not in resp.text


def test_public_reviews_are_by_slug_and_free_of_internal_ids(
    client: TestClient, db_session: Session
) -> None:
    slug = _seed(db_session, reviewer_name="Bia")

    by_id = client.get(f"/api/v1/instructors/{INSTRUCTOR_ID}/reviews")
    by_slug = client.get(f"/api/v1/instructors/{slug}/reviews")

    assert by_id.status_code == 404
    assert by_slug.status_code == 200
    [review] = by_slug.json()["data"]
    assert review["reviewer"]["full_name"] == "Bia"
    assert review["reviewer"]["slug"].startswith("bia-")
    for internal in (INSTRUCTOR_ID, REVIEWER_ID, review.get("booking_id", "x-none")):
        assert internal not in by_slug.text


def test_nameless_reviewers_are_anonymous_not_their_email(
    client: TestClient, db_session: Session
) -> None:
    slug = _seed(db_session, reviewer_name=None)

    profile = client.get(f"/api/v1/instructors/{slug}/public").json()["data"]
    reviews = client.get(f"/api/v1/instructors/{slug}/reviews").json()["data"]

    for reviewer in (profile["reviews"][0]["reviewer"], reviews[0]["reviewer"]):
        assert reviewer["full_name"] == "Usuário LinkAuto"
        assert reviewer["slug"].startswith("aluno-")
    for text in (str(profile), str(reviews)):
        assert "secret.person" not in text
        assert REVIEWER_ID[:8] not in text
