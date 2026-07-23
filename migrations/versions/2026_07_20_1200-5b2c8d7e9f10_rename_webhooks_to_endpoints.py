"""rename webhooks to endpoints

Revision ID: 5b2c8d7e9f10
Revises: a4e1d2c3b5f6
Create Date: 2026-07-20 12:00:00
"""

from collections.abc import Sequence

from alembic import op

revision: str = "5b2c8d7e9f10"
down_revision: str | None = "a4e1d2c3b5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

UPGRADE_RENAMES = (
    "ALTER TABLE webhook_endpoints RENAME CONSTRAINT webhooks_pkey TO webhook_endpoints_pkey",
    "ALTER TABLE webhook_endpoints RENAME CONSTRAINT webhooks_app_id_fkey TO webhook_endpoints_app_id_fkey",
    "ALTER INDEX webhooks_app_id_idx RENAME TO webhook_endpoints_app_id_idx",
    "ALTER TABLE webhook_endpoints_version RENAME CONSTRAINT webhooks_version_pkey TO webhook_endpoints_version_pkey",
    "ALTER INDEX webhooks_version_app_id_idx RENAME TO webhook_endpoints_version_app_id_idx",
    "ALTER INDEX webhooks_version_end_transaction_id_idx RENAME TO webhook_endpoints_version_end_transaction_id_idx",
    "ALTER INDEX webhooks_version_operation_type_idx RENAME TO webhook_endpoints_version_operation_type_idx",
    "ALTER INDEX webhooks_version_transaction_id_idx RENAME TO webhook_endpoints_version_transaction_id_idx",
    "ALTER TABLE webhook_deliveries RENAME CONSTRAINT webhook_deliveries_webhook_id_fkey "
    "TO webhook_deliveries_endpoint_id_fkey",
    "ALTER INDEX webhook_deliveries_webhook_id_idx RENAME TO webhook_deliveries_endpoint_id_idx",
)

DOWNGRADE_RENAMES = (
    "ALTER INDEX webhook_deliveries_endpoint_id_idx RENAME TO webhook_deliveries_webhook_id_idx",
    "ALTER TABLE webhook_deliveries RENAME CONSTRAINT webhook_deliveries_endpoint_id_fkey "
    "TO webhook_deliveries_webhook_id_fkey",
    "ALTER INDEX webhook_endpoints_version_transaction_id_idx RENAME TO webhooks_version_transaction_id_idx",
    "ALTER INDEX webhook_endpoints_version_operation_type_idx RENAME TO webhooks_version_operation_type_idx",
    "ALTER INDEX webhook_endpoints_version_end_transaction_id_idx RENAME TO webhooks_version_end_transaction_id_idx",
    "ALTER INDEX webhook_endpoints_version_app_id_idx RENAME TO webhooks_version_app_id_idx",
    "ALTER TABLE webhook_endpoints_version RENAME CONSTRAINT webhook_endpoints_version_pkey TO webhooks_version_pkey",
    "ALTER INDEX webhook_endpoints_app_id_idx RENAME TO webhooks_app_id_idx",
    "ALTER TABLE webhook_endpoints RENAME CONSTRAINT webhook_endpoints_app_id_fkey TO webhooks_app_id_fkey",
    "ALTER TABLE webhook_endpoints RENAME CONSTRAINT webhook_endpoints_pkey TO webhooks_pkey",
)


def upgrade() -> None:
    op.rename_table("webhooks", "webhook_endpoints")
    op.rename_table("webhooks_version", "webhook_endpoints_version")
    op.alter_column("webhook_deliveries", "webhook_id", new_column_name="endpoint_id")
    for statement in UPGRADE_RENAMES:
        op.execute(statement)


def downgrade() -> None:
    for statement in DOWNGRADE_RENAMES:
        op.execute(statement)
    op.alter_column("webhook_deliveries", "endpoint_id", new_column_name="webhook_id")
    op.rename_table("webhook_endpoints_version", "webhooks_version")
    op.rename_table("webhook_endpoints", "webhooks")
