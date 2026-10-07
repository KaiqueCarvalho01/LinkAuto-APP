"""SQLAlchemy engine, session factory and request-scoped session dependency."""

from typing import TYPE_CHECKING

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

if TYPE_CHECKING:
    from collections.abc import Generator


def get_engine() -> Engine:
    """Create an engine for DATABASE_URL, disabling the same-thread check for SQLite."""
    settings = get_settings()
    connect_args: dict[str, object] = {}
    if settings.database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(settings.database_url, connect_args=connect_args)


def get_session_factory() -> sessionmaker[Session]:
    """Return a session factory (no autocommit, no autoflush) bound to a new engine."""
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


SessionLocal = get_session_factory()


def get_db() -> Generator[Session]:
    """Yield a database session and close it when the request finishes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
