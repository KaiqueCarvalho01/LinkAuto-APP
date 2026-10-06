from datetime import UTC, datetime

from pydantic import BaseModel

from app.schemas.datetime import UtcDateTime


class MockSchema(BaseModel):
    timestamp: UtcDateTime


def test_datetime_serializes_with_utc_z() -> None:
    """Any datetime returned by the API must be serialized as ISO 8601 ending in Z."""
    dt = datetime(2026, 5, 28, 12, 0, 0, tzinfo=UTC)
    schema = MockSchema(timestamp=dt)
    json_data = schema.model_dump(mode="json")

    assert json_data["timestamp"] == "2026-05-28T12:00:00Z"


def test_naive_datetime_interpreted_as_utc_and_serializes_with_z() -> None:
    """Naive datetimes should be assumed as UTC and serialized ending in Z."""
    dt = datetime(2026, 5, 28, 12, 0, 0)  # noqa: DTZ001 - naive on purpose
    schema = MockSchema(timestamp=dt)
    json_data = schema.model_dump(mode="json")

    assert json_data["timestamp"] == "2026-05-28T12:00:00Z"
