"""ensure brand profile columns exist

Adds the brand-profile columns used by the Brand Agent
(tone_of_voice, target_audience, value_proposition, positioning) when they are
missing. Written idempotently so it is safe on databases that already created
the ``brands`` table outside of Alembic, and so fresh deploys converge to the
schema expected by the application models.

Revision ID: d5e6f7a8b9c0
Revises: c4d5e6f7a8b9
Create Date: 2026-06-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d5e6f7a8b9c0"
down_revision: Union[str, Sequence[str], None] = "c4d5e6f7a8b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_COLUMNS = {
    "tone_of_voice": sa.String(length=200),
    "target_audience": sa.Text(),
    "value_proposition": sa.Text(),
    "positioning": sa.Text(),
}


def _existing_columns() -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "brands" not in inspector.get_table_names():
        return set()
    return {col["name"] for col in inspector.get_columns("brands")}


def upgrade() -> None:
    existing = _existing_columns()
    if not existing:
        # No brands table yet (truly fresh DB): nothing to patch here. The
        # initial migration / model bootstrap is responsible for creating it.
        return
    for name, column_type in _COLUMNS.items():
        if name not in existing:
            op.add_column("brands", sa.Column(name, column_type, nullable=True))


def downgrade() -> None:
    # These columns are part of the core brand model; we intentionally do not
    # drop them on downgrade to avoid destroying brand data.
    pass
