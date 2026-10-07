"""Booking status overrides audit trail.

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-07

Stores who forced a booking's status, when, from which status and why (#13).
"""

from typing import TYPE_CHECKING

import sqlalchemy as sa
from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0002"
down_revision: str | Sequence[str] | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "booking_status_overrides",
        sa.Column("booking_id", sa.String(length=36), nullable=False),
        sa.Column("admin_id", sa.String(length=36), nullable=False),
        sa.Column("from_status", sa.String(length=20), nullable=False),
        sa.Column("to_status", sa.String(length=20), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("booking_status_overrides", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_booking_status_overrides_admin_id"), ["admin_id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_booking_status_overrides_booking_id"), ["booking_id"], unique=False
        )


def downgrade() -> None:
    with op.batch_alter_table("booking_status_overrides", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_booking_status_overrides_booking_id"))
        batch_op.drop_index(batch_op.f("ix_booking_status_overrides_admin_id"))

    op.drop_table("booking_status_overrides")
