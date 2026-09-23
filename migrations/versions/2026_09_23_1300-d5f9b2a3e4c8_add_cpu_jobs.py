"""add durable cpu jobs

Revision ID: d5f9b2a3e4c8
Revises: c4e8a1f2d3b7
Create Date: 2026-09-23 13:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "d5f9b2a3e4c8"
down_revision: str | None = "c4e8a1f2d3b7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

job_status = sa.Enum(
    "pending",
    "processing",
    "succeeded",
    "failed",
    "cancelled",
    name="cpujobstatus",
    native_enum=False,
)


def upgrade() -> None:
    op.create_table(
        "cpu_jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", job_status, server_default="pending", nullable=False),
        sa.Column("priority", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("attempt_count", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("max_attempts", sa.BigInteger(), server_default="3", nullable=False),
        sa.Column("next_attempt_at", sa.DateTime(), nullable=False),
        sa.Column("leased_until", sa.DateTime(), nullable=True),
        sa.Column("lease_token", sa.Uuid(), nullable=True),
        sa.Column("heartbeat_at", sa.DateTime(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("error", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("cpu_jobs_pkey")),
    )
    for column in ("kind", "status", "priority", "next_attempt_at", "leased_until", "lease_token"):
        op.create_index(op.f(f"cpu_jobs_{column}_idx"), "cpu_jobs", [column])


def downgrade() -> None:
    op.drop_table("cpu_jobs")
