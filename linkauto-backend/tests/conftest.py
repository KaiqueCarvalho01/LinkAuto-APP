import os
from typing import TYPE_CHECKING, cast

import pytest

from app.core.config import Settings, get_settings
from app.core.rate_limit import limiter
from app.services.dependencies import get_notification_service
from app.services.identity_repository import IdentityRepository
from app.services.notification_service import InMemoryEmailGateway, NotificationService
from tests.conftest_db import *  # noqa: F403

TEST_JWT_SECRET = "test-only-jwt-secret-0123456789abcdef"

# Ensure unit tests are deterministic and isolated from developer-specific local .env
Settings.model_config["env_file"] = None
# A test-only key long enough for HS256 (the development default is too short for PyJWT)
os.environ.setdefault("JWT_SECRET", TEST_JWT_SECRET)
get_settings.cache_clear()

if TYPE_CHECKING:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from sqlmodel import Session


@pytest.fixture(autouse=True)
def reset_limiter_global() -> None:
    limiter.reset()


@pytest.fixture
def identity_repository(db_session: Session) -> IdentityRepository:
    return IdentityRepository(db_session)


@pytest.fixture
def email_outbox(client: TestClient) -> InMemoryEmailGateway:
    """Capture the e-mails the API sends through ``client``."""
    gateway = InMemoryEmailGateway()
    app = cast("FastAPI", client.app)
    app.dependency_overrides[get_notification_service] = lambda: NotificationService(gateway)
    return gateway
