"""durable webhooks

Revision ID: 7f3c0d2f18a1
Revises: bfa61bae871d
Create Date: 2026-07-17 17:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "7f3c0d2f18a1"
down_revision: str | None = "bfa61bae871d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

webhook_type = sa.Enum(
    "user_registration",
    "user_login",
    "user_update_profile",
    "user_change_email",
    "user_change_password",
    "user_delete",
    name="webhooktype",
    native_enum=False,
)
delivery_status = sa.Enum(
    "pending",
    "processing",
    "succeeded",
    "exhausted",
    "cancelled",
    name="webhookdeliverystatus",
    native_enum=False,
)


def upgrade() -> None:
    op.add_column("webhooks", sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False))
    op.add_column("webhooks", sa.Column("disabled_at", sa.DateTime(), nullable=True))
    op.add_column("webhooks", sa.Column("disabled_reason", sa.String(), nullable=True))
    op.add_column("webhooks_version", sa.Column("is_active", sa.Boolean(), nullable=True))
    op.add_column("webhooks_version", sa.Column("disabled_at", sa.DateTime(), nullable=True))
    op.add_column("webhooks_version", sa.Column("disabled_reason", sa.String(), nullable=True))

    op.add_column("webhook_events", sa.Column("event_id", sa.Uuid(), nullable=True))
    op.add_column("webhook_events", sa.Column("event_type", webhook_type, nullable=True))
    op.add_column("webhook_events", sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column("webhook_events", sa.Column("status", delivery_status, nullable=True))
    op.add_column("webhook_events", sa.Column("attempt_count", sa.BigInteger(), server_default="0", nullable=False))
    op.add_column("webhook_events", sa.Column("next_attempt_at", sa.DateTime(), nullable=True))
    op.add_column("webhook_events", sa.Column("leased_until", sa.DateTime(), nullable=True))
    op.add_column("webhook_events", sa.Column("completed_at", sa.DateTime(), nullable=True))
    op.add_column("webhook_events", sa.Column("error", sa.String(), nullable=True))
    op.alter_column("webhook_events", "request", existing_type=postgresql.JSONB(), nullable=True)
    op.alter_column("webhook_events", "status_code", existing_type=sa.BigInteger(), nullable=True)
    op.alter_column("webhook_events", "response", existing_type=postgresql.JSONB(), nullable=True)

    op.execute(
        """
        UPDATE webhook_events AS delivery
        SET event_id = delivery.id,
            event_type = endpoint.type,
            payload = COALESCE(delivery.request -> 'body', '{}'::jsonb),
            status = CASE
                WHEN delivery.status_code BETWEEN 200 AND 299 THEN 'succeeded'
                ELSE 'exhausted'
            END,
            attempt_count = 1,
            next_attempt_at = delivery.created_at,
            completed_at = delivery.updated_at,
            error = CASE WHEN delivery.status_code = 0 THEN delivery.response ->> 'error' ELSE NULL END
        FROM webhooks AS endpoint
        WHERE endpoint.id = delivery.webhook_id
        """
    )
    op.alter_column("webhook_events", "event_id", nullable=False)
    op.alter_column("webhook_events", "event_type", nullable=False)
    op.alter_column("webhook_events", "payload", nullable=False)
    op.alter_column("webhook_events", "status", nullable=False)
    op.alter_column("webhook_events", "next_attempt_at", nullable=False)

    op.create_index(op.f("webhook_events_event_id_idx"), "webhook_events", ["event_id"])
    op.create_index(op.f("webhook_events_status_idx"), "webhook_events", ["status"])
    op.create_index(op.f("webhook_events_next_attempt_at_idx"), "webhook_events", ["next_attempt_at"])
    op.create_index(op.f("webhook_events_leased_until_idx"), "webhook_events", ["leased_until"])

    op.create_table(
        "webhook_attempts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("delivery_id", sa.Uuid(), nullable=False),
        sa.Column("attempt_number", sa.BigInteger(), nullable=False),
        sa.Column("timestamp", sa.BigInteger(), nullable=False),
        sa.Column("request", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status_code", sa.BigInteger(), nullable=True),
        sa.Column("response", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("error", sa.String(), nullable=True),
        sa.Column("duration_ms", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["delivery_id"], ["webhook_events.id"], name=op.f("webhook_attempts_delivery_id_fkey")),
        sa.PrimaryKeyConstraint("id", name=op.f("webhook_attempts_pkey")),
        sa.UniqueConstraint("delivery_id", "attempt_number", name=op.f("webhook_attempts_delivery_id_key")),
    )
    op.create_index(op.f("webhook_attempts_delivery_id_idx"), "webhook_attempts", ["delivery_id"])
    op.execute(
        """
        INSERT INTO webhook_attempts (
            id, delivery_id, attempt_number, timestamp, request, status_code,
            response, error, duration_ms, created_at, updated_at
        )
        SELECT id, id, 1, EXTRACT(EPOCH FROM created_at)::bigint, request,
               status_code, response, error, 0, created_at, updated_at
        FROM webhook_events
        """
    )


def downgrade() -> None:
    op.drop_index(op.f("webhook_attempts_delivery_id_idx"), table_name="webhook_attempts")
    op.drop_table("webhook_attempts")
    op.execute(
        """
        UPDATE webhook_events
        SET request = COALESCE(request, jsonb_build_object('headers', '{}'::jsonb, 'body', payload)),
            status_code = COALESCE(status_code, 0),
            response = COALESCE(response, jsonb_build_object('error', COALESCE(error, 'not delivered')))
        """
    )
    op.alter_column("webhook_events", "response", existing_type=postgresql.JSONB(), nullable=False)
    op.alter_column("webhook_events", "status_code", existing_type=sa.BigInteger(), nullable=False)
    op.alter_column("webhook_events", "request", existing_type=postgresql.JSONB(), nullable=False)
    op.drop_index(op.f("webhook_events_leased_until_idx"), table_name="webhook_events")
    op.drop_index(op.f("webhook_events_next_attempt_at_idx"), table_name="webhook_events")
    op.drop_index(op.f("webhook_events_status_idx"), table_name="webhook_events")
    op.drop_index(op.f("webhook_events_event_id_idx"), table_name="webhook_events")
    for column in (
        "error",
        "completed_at",
        "leased_until",
        "next_attempt_at",
        "attempt_count",
        "status",
        "payload",
        "event_type",
        "event_id",
    ):
        op.drop_column("webhook_events", column)
    for table in ("webhooks_version", "webhooks"):
        op.drop_column(table, "disabled_reason")
        op.drop_column(table, "disabled_at")
        op.drop_column(table, "is_active")
