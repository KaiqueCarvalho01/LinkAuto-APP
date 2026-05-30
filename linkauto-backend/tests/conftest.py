import pytest

from tests.conftest_db import *  # noqa: F401, F403
from app.services.us1_store import get_identity_store


@pytest.fixture(autouse=True)
def reset_identity_store():
    store = get_identity_store()
    store.reset()
    yield
    store.reset()
