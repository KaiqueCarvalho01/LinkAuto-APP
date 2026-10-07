from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Connection, Engine, event
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session

from app.core.database import create_db_engine, get_db
from app.main import create_app
from app.models.base import Base

if TYPE_CHECKING:
    from collections.abc import Iterator


def create_test_engine() -> Engine:
    """Return an in-memory SQLite engine whose savepoints nest inside real transactions."""
    # Same engine setup as the app (incl. PRAGMA foreign_keys=ON); one shared in-memory DB
    engine = create_db_engine("sqlite:///:memory:")

    # pysqlite's legacy transaction mode never emits BEGIN before a SAVEPOINT, so the
    # savepoint would become the outermost transaction and RELEASE would commit it. Let
    # SQLAlchemy emit BEGIN itself so savepoints nest inside the per-test transaction:
    # https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#serializable-isolation-savepoints-transactional-ddl
    @event.listens_for(engine, "connect")
    def _disable_pysqlite_begin(dbapi_connection: Any, _record: object) -> None:  # noqa: ANN401
        dbapi_connection.isolation_level = None

    @event.listens_for(engine, "begin")
    def _emit_begin(conn: Connection) -> None:
        conn.exec_driver_sql("BEGIN")

    Base.metadata.create_all(bind=engine)
    return engine


@contextmanager
def isolated_session(engine: Engine) -> Iterator[Session]:
    """Yield a session whose work is always rolled back, even if it commits or rolls back."""
    connection = engine.connect()
    transaction = connection.begin()
    # The session works inside a SAVEPOINT, so its own commit()/rollback() (e.g. after an
    # expected IntegrityError) never ends the outer transaction that isolates the test.
    session_factory = sessionmaker(
        class_=Session, bind=connection, join_transaction_mode="create_savepoint"
    )
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="session")
def test_engine() -> Iterator[Engine]:
    engine = create_test_engine()
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(test_engine: Engine) -> Iterator[Session]:
    with isolated_session(test_engine) as session:
        yield session


@pytest.fixture
def client(db_session: Session) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_db] = lambda: db_session
    return TestClient(app)
