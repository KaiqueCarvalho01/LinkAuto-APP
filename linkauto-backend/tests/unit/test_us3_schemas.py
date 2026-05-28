from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas.booking_message import BookingMessageCreateRequest, MessageResource
from app.schemas.review import ReviewCreateRequest, ReviewResource


class TestBookingMessageSchemas:
    def test_message_create_valid(self):
        req = BookingMessageCreateRequest(content="Olá, tudo bem?")
        assert req.content == "Olá, tudo bem?"

    def test_message_create_rejects_empty(self):
        with pytest.raises(ValidationError):
            BookingMessageCreateRequest(content="")

    def test_message_resource_serialization(self):
        dt = datetime(2026, 5, 28, 15, 30, 0, tzinfo=timezone.utc)
        res = MessageResource(
            id="msg-uuid-placeholder",
            booking_id="booking-uuid-placeholder",
            sender_id="sender-uuid-placeholder",
            content="Olá!",
            created_at=dt,
        )
        json_data = res.model_dump(mode="json")
        assert json_data["id"] == "msg-uuid-placeholder"
        assert json_data["created_at"] == "2026-05-28T15:30:00Z"


class TestReviewSchemas:
    def test_review_create_valid(self):
        req = ReviewCreateRequest(rating=5, comment="Excelente aula!")
        assert req.rating == 5
        assert req.comment == "Excelente aula!"

    def test_review_create_rejects_invalid_rating(self):
        with pytest.raises(ValidationError):
            ReviewCreateRequest(rating=0)
        with pytest.raises(ValidationError):
            ReviewCreateRequest(rating=6)

    def test_review_create_rejects_too_long_comment(self):
        with pytest.raises(ValidationError):
            ReviewCreateRequest(rating=5, comment="A" * 1001)

    def test_review_resource_serialization(self):
        dt = datetime(2026, 5, 28, 15, 30, 0, tzinfo=timezone.utc)
        res = ReviewResource(
            id="rev-uuid-placeholder",
            booking_id="booking-uuid-placeholder",
            reviewer_id="reviewer-uuid-placeholder",
            reviewed_id="reviewed-uuid-placeholder",
            rating=5,
            comment="Ótimo",
            created_at=dt,
            updated_at=dt,
        )
        json_data = res.model_dump(mode="json")
        assert json_data["rating"] == 5
        assert json_data["created_at"] == "2026-05-28T15:30:00Z"
