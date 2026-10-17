from datetime import timedelta
from typing import TYPE_CHECKING

from sqlmodel import select

from app.models import PasswordResetToken, RefreshToken
from app.models.base import utc_now
from app.services.refresh_token_repository import RefreshTokenRepository
from app.services.token_cleanup_service import TokenCleanupService
from tests.factories import seed_student

if TYPE_CHECKING:
    from sqlmodel import Session


def _refresh(db: Session, jti: str, expires_in: timedelta) -> None:
    RefreshTokenRepository(db).record(jti=jti, user_id="stu-1", expires_at=utc_now() + expires_in)


def _reset(db: Session, token_hash: str, expires_in: timedelta) -> None:
    db.add(
        PasswordResetToken(
            user_id="stu-1", token_hash=token_hash, expires_at=utc_now() + expires_in
        )
    )
    db.flush()


def test_deletes_only_tokens_past_the_grace_period(db_session: Session) -> None:
    seed_student(db_session, "stu-1")
    _refresh(db_session, "long-expired", -timedelta(days=2))
    _refresh(db_session, "just-expired", -timedelta(hours=1))
    _refresh(db_session, "valid", timedelta(days=7))
    _reset(db_session, "a" * 64, -timedelta(days=2))
    _reset(db_session, "b" * 64, -timedelta(minutes=5))

    result = TokenCleanupService(db_session).run()

    assert (result.refresh_tokens_deleted, result.password_reset_tokens_deleted) == (1, 1)
    remaining = {t.jti for t in db_session.exec(select(RefreshToken)).all()}
    # Just-expired tokens stay, so presenting one again still triggers reuse detection
    assert remaining == {"just-expired", "valid"}
    assert [t.token_hash for t in db_session.exec(select(PasswordResetToken)).all()] == ["b" * 64]


def test_running_twice_is_harmless(db_session: Session) -> None:
    seed_student(db_session, "stu-1")
    _refresh(db_session, "long-expired", -timedelta(days=2))
    service = TokenCleanupService(db_session)

    assert service.run().refresh_tokens_deleted == 1
    assert service.run().refresh_tokens_deleted == 0
