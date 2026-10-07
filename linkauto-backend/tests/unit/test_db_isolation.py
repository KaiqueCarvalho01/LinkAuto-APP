import warnings
from typing import TYPE_CHECKING

import pytest
from sqlalchemy.exc import IntegrityError, SAWarning
from sqlmodel import select

from app.models import User
from tests.conftest_db import isolated_session

if TYPE_CHECKING:
    from sqlalchemy import Engine


def test_committed_and_rolled_back_work_is_discarded_after_the_session(
    test_engine: Engine,
) -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error", SAWarning)
        with isolated_session(test_engine) as session:
            session.add(User(id="iso-1", email="iso-1@test.com", password_hash="x"))
            session.commit()

            session.add(User(id="iso-2", email="iso-1@test.com", password_hash="x"))
            with pytest.raises(IntegrityError):
                session.commit()
            session.rollback()

            # Committed work stays visible inside the test after the session's rollback
            assert session.get(User, "iso-1") is not None

    with isolated_session(test_engine) as session:
        assert session.exec(select(User).where(User.id == "iso-1")).first() is None
