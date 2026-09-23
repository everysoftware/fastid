"""add webhook delivery lease ownership token

Revision ID: c4e8a1f2d3b7
Revises: 5b2c8d7e9f10
Create Date: 2026-09-23 12:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c4e8a1f2d3b7"
down_revision: str | None = "5b2c8d7e9f10"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("webhook_deliveries", sa.Column("lease_token", sa.Uuid(), nullable=True))
    op.create_index(op.f("webhook_deliveries_lease_token_idx"), "webhook_deliveries", ["lease_token"])


def downgrade() -> None:
    op.drop_index(op.f("webhook_deliveries_lease_token_idx"), table_name="webhook_deliveries")
    op.drop_column("webhook_deliveries", "lease_token")
