from typing import TYPE_CHECKING

import pytest

from app.core.rate_limit import limiter
from app.services.us1_store import get_identity_store
from tests.conftest_db import *  # noqa: F403

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.fixture(autouse=True)
def reset_identity_store() -> Iterator[None]:
    store = get_identity_store()
    store.reset()
    yield
    store.reset()


@pytest.fixture(autouse=True)
def reset_limiter_global() -> None:
    limiter.reset()
