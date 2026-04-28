from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url

from app.core.config import Settings
from app.models import Base
import app.models  # noqa: F401


def _sqlite_file_from_url(database_url: str) -> Path | None:
    url = make_url(database_url)
    if not url.drivername.startswith("sqlite"):
        return None

    database = url.database
    if not database or database == ":memory:":
        return None

    sqlite_path = Path(database)
    if not sqlite_path.is_absolute():
        sqlite_path = Path.cwd() / sqlite_path

    return sqlite_path


def initialize_sqlite_dev_database(settings: Settings) -> None:
    if settings.app_env.lower() != "development":
        return

    sqlite_file = _sqlite_file_from_url(settings.database_url)
    if sqlite_file is None:
        return

    sqlite_file.parent.mkdir(parents=True, exist_ok=True)

    if settings.reset_sqlite_on_startup and sqlite_file.exists():
        sqlite_file.unlink()

    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        future=True,
    )
    try:
        Base.metadata.create_all(bind=engine)
    finally:
        engine.dispose()
