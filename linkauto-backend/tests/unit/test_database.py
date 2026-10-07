from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import pytest
from sqlalchemy import delete, text
from sqlalchemy.exc import IntegrityError
from sqlmodel import col

from app.core.database import create_db_engine
from app.models import InstructorProfile, Slot, User

if TYPE_CHECKING:
    from pathlib import Path

    from sqlmodel import Session

_NOW = datetime.now(UTC) + timedelta(days=1)
_LATER = _NOW + timedelta(hours=1)


def test_get_db_yields_valid_session(db_session: Session) -> None:
    """get_db dependency must yield a functional database session."""
    result = db_session.connection().execute(text("SELECT 1"))
    assert result.scalar() == 1


def test_get_db_session_is_isolated(db_session: Session) -> None:
    """Each test gets a clean, isolated session via transaction rollback."""
    result = db_session.connection().execute(text("SELECT 1"))
    assert result.scalar() == 1


def test_sqlite_enforces_foreign_keys(db_session: Session) -> None:
    """SQLite ignores FOREIGN KEY constraints unless PRAGMA foreign_keys is ON (#25)."""
    assert db_session.connection().execute(text("PRAGMA foreign_keys")).scalar() == 1

    db_session.add(Slot(instructor_id="missing-instructor", starts_at=_NOW, ends_at=_LATER))
    with pytest.raises(IntegrityError, match="FOREIGN KEY"):
        db_session.flush()


def test_app_engine_enables_foreign_keys_for_sqlite(tmp_path: Path) -> None:
    engine = create_db_engine(f"sqlite:///{tmp_path / 'fk.db'}")
    with engine.connect() as connection:
        assert connection.execute(text("PRAGMA foreign_keys")).scalar() == 1
    engine.dispose()


def test_on_delete_cascade_runs_on_sqlite(db_session: Session) -> None:
    user = User(email="cascade@x.com", password_hash="h", roles=["INSTRUTOR"])
    db_session.add(user)
    db_session.flush()
    db_session.add(InstructorProfile(user_id=user.id))
    db_session.flush()

    # Core DELETE bypasses ORM cascades, so only the database's ON DELETE CASCADE applies
    db_session.exec(delete(User).where(col(User.id) == user.id))
    db_session.expire_all()

    assert db_session.get(InstructorProfile, user.id) is None
