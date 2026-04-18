"""foundation bootstrap

Revision ID: 0001_foundation
Revises:
Create Date: 2026-04-17 00:00:00.000000
"""

from collections.abc import Sequence

revision: str = "0001_foundation"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
