"""rename webhook events to deliveries

Revision ID: a4e1d2c3b5f6
Revises: 7f3c0d2f18a1
Create Date: 2026-07-17 18:00:00
"""

from collections.abc import Sequence

from alembic import op

revision: str = "a4e1d2c3b5f6"
down_revision: str | None = "7f3c0d2f18a1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

OLD_TABLE = "webhook_events"
NEW_TABLE = "webhook_deliveries"
INDEX_COLUMNS = ("webhook_id", "event_id", "status", "next_attempt_at", "leased_until")


def upgrade() -> None:
    op.rename_table(OLD_TABLE, NEW_TABLE)
    op.execute(f"ALTER TABLE {NEW_TABLE} RENAME CONSTRAINT {OLD_TABLE}_pkey TO {NEW_TABLE}_pkey")
    op.execute(
        f"ALTER TABLE {NEW_TABLE} " f"RENAME CONSTRAINT {OLD_TABLE}_webhook_id_fkey TO {NEW_TABLE}_webhook_id_fkey"
    )
    for column in INDEX_COLUMNS:
        op.execute(f"ALTER INDEX {OLD_TABLE}_{column}_idx RENAME TO {NEW_TABLE}_{column}_idx")


def downgrade() -> None:
    op.rename_table(NEW_TABLE, OLD_TABLE)
    op.execute(f"ALTER TABLE {OLD_TABLE} RENAME CONSTRAINT {NEW_TABLE}_pkey TO {OLD_TABLE}_pkey")
    op.execute(
        f"ALTER TABLE {OLD_TABLE} " f"RENAME CONSTRAINT {NEW_TABLE}_webhook_id_fkey TO {OLD_TABLE}_webhook_id_fkey"
    )
    for column in INDEX_COLUMNS:
        op.execute(f"ALTER INDEX {NEW_TABLE}_{column}_idx RENAME TO {OLD_TABLE}_{column}_idx")
