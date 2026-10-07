from typing import TYPE_CHECKING

import pytest

from app.core.rate_limit import limiter
from app.services.identity_repository import IdentityRepository
from tests.conftest_db import *  # noqa: F403

if TYPE_CHECKING:
    from sqlmodel import Session


@pytest.fixture(autouse=True)
def reset_limiter_global() -> None:
    limiter.reset()


@pytest.fixture
def identity_repository(db_session: Session) -> IdentityRepository:
    return IdentityRepository(db_session)
