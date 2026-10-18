"""Concurrent slot creation can't produce overlapping slots on PostgreSQL (#75).

Needs a real PostgreSQL (SQLite runs one write at a time, so the race can't happen there):
set LINKAUTO_POSTGRES_TEST_URL, e.g. postgresql+psycopg://postgres:pg@localhost:5432/linkauto.
The tables are created and dropped by the test.
"""

import os
import threading
from datetime import UTC, datetime, timedelta

import pytest
from sqlmodel import Session, col, select

from app.core.database import create_db_engine
from app.models import Base, InstructorProfile, Slot, User
from app.services.slot_service import SlotOverlapError, SlotService

POSTGRES_URL = os.environ.get("LINKAUTO_POSTGRES_TEST_URL")

pytestmark = pytest.mark.skipif(
    not POSTGRES_URL, reason="set LINKAUTO_POSTGRES_TEST_URL to run PostgreSQL tests"
)


def test_concurrent_overlapping_slots_are_serialized() -> None:
    assert POSTGRES_URL is not None
    engine = create_db_engine(POSTGRES_URL)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    try:
        with Session(engine) as setup:
            setup.add(User(id="inst", email="inst@t.com", password_hash="h", roles=["INSTRUTOR"]))
            setup.flush()
            setup.add(InstructorProfile(user_id="inst"))
            setup.commit()

        start = datetime.now(UTC).replace(microsecond=0) + timedelta(days=1)
        first_inserted = threading.Event()
        second_result: list[str] = []

        def create_overlapping() -> None:
            first_inserted.wait()
            with Session(engine) as second:
                try:
                    SlotService(second).create_slot(
                        "inst", start + timedelta(minutes=30), start + timedelta(minutes=90)
                    )
                    second.commit()
                    second_result.append("created")
                except SlotOverlapError:
                    second_result.append("overlap")

        other = threading.Thread(target=create_overlapping)
        other.start()
        with Session(engine) as first:
            SlotService(first).create_slot("inst", start, start + timedelta(hours=1))
            first_inserted.set()
            # Keep the transaction (and the lock) open while the other request runs
            other.join(timeout=2)
            first.commit()
        other.join(timeout=10)

        with Session(engine) as check:
            slots = check.exec(select(Slot).where(col(Slot.instructor_id) == "inst")).all()
        assert second_result == ["overlap"]
        assert len(slots) == 1
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()
