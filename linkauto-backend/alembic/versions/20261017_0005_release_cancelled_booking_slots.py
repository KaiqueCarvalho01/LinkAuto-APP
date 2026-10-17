"""Let slots freed by a cancellation be booked again.

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-17

booking_slots.slot_id was unique, so the links kept by a cancelled booking blocked any new
booking of its freed slots (#69). Links now get ``released_at`` when the booking is
cancelled, and slot_id is only unique among unreleased links (partial unique index). Links of
bookings that are already cancelled are released here.
"""

from typing import TYPE_CHECKING

import sqlalchemy as sa
from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0005"
down_revision: str | Sequence[str] | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ACTIVE_LINK = sa.text("released_at IS NULL")
# Migration 0001 created the unique constraint without a name. PostgreSQL named it after the
# table and column; on SQLite, batch mode needs a naming convention to find it.
POSTGRES_UNIQUE_SLOT = "booking_slots_slot_id_key"
SQLITE_NAMING = {"uq": "uq_%(table_name)s_%(column_0_name)s"}
SQLITE_UNIQUE_SLOT = "uq_booking_slots_slot_id"


def upgrade() -> None:
    sqlite = op.get_bind().dialect.name == "sqlite"
    with op.batch_alter_table(
        "booking_slots", schema=None, naming_convention=SQLITE_NAMING if sqlite else None
    ) as batch_op:
        batch_op.add_column(sa.Column("released_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.drop_constraint(
            SQLITE_UNIQUE_SLOT if sqlite else POSTGRES_UNIQUE_SLOT, type_="unique"
        )

    op.execute(
        sa.text(
            "UPDATE booking_slots SET released_at = CURRENT_TIMESTAMP "
            "WHERE booking_id IN (SELECT id FROM bookings WHERE status = 'CANCELADA')"
        )
    )

    with op.batch_alter_table("booking_slots", schema=None) as batch_op:
        batch_op.create_index(
            "uq_booking_slots_active_slot",
            ["slot_id"],
            unique=True,
            sqlite_where=ACTIVE_LINK,
            postgresql_where=ACTIVE_LINK,
        )


def downgrade() -> None:
    # Fails if a slot was booked again after a cancellation: one of its links must go first
    sqlite = op.get_bind().dialect.name == "sqlite"
    with op.batch_alter_table("booking_slots", schema=None) as batch_op:
        batch_op.drop_index(
            "uq_booking_slots_active_slot",
            sqlite_where=ACTIVE_LINK,
            postgresql_where=ACTIVE_LINK,
        )

    with op.batch_alter_table(
        "booking_slots", schema=None, naming_convention=SQLITE_NAMING if sqlite else None
    ) as batch_op:
        batch_op.create_unique_constraint(
            SQLITE_UNIQUE_SLOT if sqlite else POSTGRES_UNIQUE_SLOT, ["slot_id"]
        )
        batch_op.drop_column("released_at")
