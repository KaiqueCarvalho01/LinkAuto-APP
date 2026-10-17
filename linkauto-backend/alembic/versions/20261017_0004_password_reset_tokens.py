"""Password reset tokens.

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-17

Single-use password reset tokens, stored as SHA-256 hashes with an expiry, e-mailed to the
user or issued by an admin while e-mail is disabled (#52).
"""

from typing import TYPE_CHECKING

import sqlalchemy as sa
from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0004"
down_revision: str | Sequence[str] | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "password_reset_tokens",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("issued_by", sa.String(length=36), nullable=True),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("password_reset_tokens", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_password_reset_tokens_token_hash"), ["token_hash"], unique=True
        )
        batch_op.create_index(
            batch_op.f("ix_password_reset_tokens_user_id"), ["user_id"], unique=False
        )


def downgrade() -> None:
    with op.batch_alter_table("password_reset_tokens", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_password_reset_tokens_user_id"))
        batch_op.drop_index(batch_op.f("ix_password_reset_tokens_token_hash"))

    op.drop_table("password_reset_tokens")
