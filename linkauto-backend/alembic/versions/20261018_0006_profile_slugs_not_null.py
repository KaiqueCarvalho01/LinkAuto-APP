"""Every profile has a stored public slug.

Revision ID: 0006
Revises: 0005
Create Date: 2026-10-18

Slugs were generated lazily by GET routes that never committed them, so most student
profiles had none and their public pages returned 404 (#72). Profiles now get a slug when
they are created; this backfills the missing ones and makes the column NOT NULL.
"""

import re
import secrets
import unicodedata
from typing import TYPE_CHECKING

import sqlalchemy as sa
from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "0006"
down_revision: str | Sequence[str] | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Same format as app.core.slug.generate_profile_slug, copied so the migration never changes
PROFILES = {"student_profiles": "aluno", "instructor_profiles": "instrutor"}


def _slug(full_name: str | None, city: str | None, prefix: str) -> str:
    text = " ".join(part.strip() for part in (full_name, city) if part and part.strip())
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    base = re.sub(r"[-\s]+", "-", text).strip("-") or prefix
    return f"{base}-{secrets.token_hex(2)}"


def upgrade() -> None:
    bind = op.get_bind()
    for table, prefix in PROFILES.items():
        profiles = sa.table(
            table,
            sa.column("user_id", sa.String),
            sa.column("slug", sa.String),
            sa.column("full_name", sa.String),
            sa.column("city", sa.String),
        )
        taken = {row.slug for row in bind.execute(sa.select(profiles.c.slug)) if row.slug}
        missing = bind.execute(
            sa.select(profiles.c.user_id, profiles.c.full_name, profiles.c.city).where(
                profiles.c.slug.is_(None)
            )
        ).all()
        for row in missing:
            slug = _slug(row.full_name, row.city, prefix)
            while slug in taken:
                slug = _slug(row.full_name, row.city, prefix)
            taken.add(slug)
            bind.execute(
                profiles.update().where(profiles.c.user_id == row.user_id).values(slug=slug)
            )
        with op.batch_alter_table(table, schema=None) as batch_op:
            batch_op.alter_column("slug", existing_type=sa.String(length=150), nullable=False)


def downgrade() -> None:
    for table in PROFILES:
        with op.batch_alter_table(table, schema=None) as batch_op:
            batch_op.alter_column("slug", existing_type=sa.String(length=150), nullable=True)
