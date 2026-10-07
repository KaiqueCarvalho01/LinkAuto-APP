"""Database engine, SQLModel session factory and request-scoped session dependency."""

from typing import TYPE_CHECKING, Any

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session

from app.core.config import get_settings

if TYPE_CHECKING:
    from collections.abc import Generator


def enable_sqlite_foreign_keys(engine: Engine) -> Engine:
    """Turn on ``PRAGMA foreign_keys`` for every new connection of a SQLite engine.

    SQLite ignores FOREIGN KEY constraints, including ON DELETE CASCADE / SET NULL, unless
    each connection enables them. No-op for other databases. Returns the engine.
    """
    if engine.dialect.name != "sqlite":
        return engine

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection: Any, _record: object) -> None:  # noqa: ANN401
        # The pragma is a no-op inside a transaction, so set it before any BEGIN
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
        finally:
            cursor.close()

    return engine


def create_db_engine(database_url: str, **kwargs: Any) -> Engine:  # noqa: ANN401
    """Create an engine for the URL; SQLite gets cross-thread access and foreign keys."""
    if database_url.startswith("sqlite"):
        connect_args: dict[str, Any] = {"check_same_thread": False}
        connect_args.update(kwargs.pop("connect_args", {}))
        kwargs["connect_args"] = connect_args
    return enable_sqlite_foreign_keys(create_engine(database_url, **kwargs))


def get_engine() -> Engine:
    """Create an engine for DATABASE_URL."""
    return create_db_engine(get_settings().database_url)


def get_session_factory() -> sessionmaker[Session]:
    """Return a session factory (no autocommit, no autoflush) bound to a new engine."""
    return sessionmaker(class_=Session, autocommit=False, autoflush=False, bind=get_engine())


SessionLocal = get_session_factory()


def get_db() -> Generator[Session]:
    """Yield a database session and close it when the request finishes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
