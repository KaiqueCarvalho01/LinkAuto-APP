"""Alembic migrations apply cleanly and stay in sync with the SQLAlchemy models."""

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, create_engine, inspect

from app.models import Base

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def database_url(tmp_path: Path) -> str:
    return f"sqlite:///{tmp_path / 'migrations.db'}"


@pytest.fixture
def alembic_config(database_url: str) -> Config:
    """Load the same configuration the `alembic` CLI uses, pointed at a scratch database."""
    config = Config(PROJECT_ROOT / "alembic.ini", toml_file=PROJECT_ROOT / "pyproject.toml")
    config.set_main_option("sqlalchemy.url", database_url)
    return config


@pytest.fixture
def engine(database_url: str) -> Engine:
    return create_engine(database_url)


def test_single_head(alembic_config: Config) -> None:
    assert len(ScriptDirectory.from_config(alembic_config).get_heads()) == 1


def test_upgrade_head_creates_every_model_table(alembic_config: Config, engine: Engine) -> None:
    command.upgrade(alembic_config, "head")

    tables = set(inspect(engine).get_table_names())
    assert set(Base.metadata.tables) <= tables


def test_migrations_match_models(alembic_config: Config) -> None:
    """Fails when a model changes without a matching migration (`alembic check`)."""
    command.upgrade(alembic_config, "head")

    command.check(alembic_config)


def test_downgrade_base_then_upgrade_again(alembic_config: Config, engine: Engine) -> None:
    command.upgrade(alembic_config, "head")

    command.downgrade(alembic_config, "base")
    assert set(inspect(engine).get_table_names()) == {"alembic_version"}

    command.upgrade(alembic_config, "head")
    assert set(Base.metadata.tables) <= set(inspect(engine).get_table_names())


def test_review_unique_constraint_on_reviewer(alembic_config: Config, engine: Engine) -> None:
    """A user may review a booking only once (uq_reviews_booking_reviewer)."""
    command.upgrade(alembic_config, "head")

    constraints = inspect(engine).get_unique_constraints("reviews")
    assert {"booking_id", "reviewer_id"} in [set(uq["column_names"]) for uq in constraints]


def test_booking_slot_belongs_to_one_booking(alembic_config: Config, engine: Engine) -> None:
    """booking_slots.slot_id is unique: a slot belongs to at most one booking."""
    command.upgrade(alembic_config, "head")

    constraints = inspect(engine).get_unique_constraints("booking_slots")
    assert ["slot_id"] in [uq["column_names"] for uq in constraints]
