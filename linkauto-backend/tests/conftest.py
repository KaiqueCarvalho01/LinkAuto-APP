from typing import TYPE_CHECKING

import pytest

from app.core.config import Settings, get_settings
from app.core.rate_limit import limiter
from app.services.identity_repository import IdentityRepository
from tests.conftest_db import *  # noqa: F403

# Ensure unit tests are deterministic and isolated from developer-specific local .env
Settings.model_config["env_file"] = None
get_settings.cache_clear()

if TYPE_CHECKING:
    from sqlmodel import Session


@pytest.fixture(autouse=True)
def reset_limiter_global() -> None:
    limiter.reset()


@pytest.fixture
def identity_repository(db_session: Session) -> IdentityRepository:
    return IdentityRepository(db_session)
