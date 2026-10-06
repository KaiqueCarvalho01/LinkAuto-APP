"""Alembic migration environment wired to the application settings and model metadata."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core import get_settings
from app.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

# Tests (and other callers) may pass an explicit URL; otherwise use the app settings.
if not config.get_main_option("sqlalchemy.url"):
    config.set_main_option("sqlalchemy.url", get_settings().database_url)

target_metadata = Base.metadata


def include_name(name: str | None, type_: str, _parent_names: object) -> bool:
    """Compare only tables owned by the app.

    Ignores e.g. PostGIS' ``spatial_ref_sys`` so autogenerate never tries to drop it.
    """
    if type_ == "table":
        return name in target_metadata.tables
    return True


CONFIGURE_OPTS = {
    "target_metadata": target_metadata,
    "include_name": include_name,
    # SQLite cannot ALTER most constraints; batch mode recreates the table instead.
    "render_as_batch": True,
}


def run_migrations_offline() -> None:
    """Run migrations in offline mode, emitting SQL with literal binds instead of connecting."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        **CONFIGURE_OPTS,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in online mode against a live database connection (no pooling)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, **CONFIGURE_OPTS)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
