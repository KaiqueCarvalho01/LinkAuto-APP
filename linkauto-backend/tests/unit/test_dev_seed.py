from sqlalchemy import func
from sqlmodel import Session, col, select

from app.core.dev_db import seed_dev_data
from app.models import InstructorProfile, Review


def test_seeded_instructor_ratings_match_the_seeded_reviews(db_session: Session) -> None:
    seed_dev_data(db_session)

    profiles = db_session.exec(select(InstructorProfile)).all()
    assert profiles
    for profile in profiles:
        average, count = db_session.exec(
            select(func.avg(Review.rating), func.count(col(Review.id))).where(
                col(Review.reviewed_id) == profile.user_id
            )
        ).one()
        assert profile.rating_count == count, profile.full_name
        assert profile.rating_avg == float(average or 0.0), profile.full_name


def test_seeding_twice_keeps_ratings_consistent(db_session: Session) -> None:
    seed_dev_data(db_session)
    seed_dev_data(db_session)

    total = db_session.exec(select(func.sum(InstructorProfile.rating_count))).one()
    reviews = db_session.exec(select(func.count(col(Review.id)))).one()
    assert total == reviews
