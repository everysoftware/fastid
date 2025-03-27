"""empty message

Revision ID: 3282fde15451
Revises: f02ee2d85935
Create Date: 2024-11-13 01:05:57.727313

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "3282fde15451"
down_revision: str | None = "f02ee2d85935"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "apps",
        sa.Column("id", sa.Uuid(as_uuid=False), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("client_id", sa.String(), nullable=False),
        sa.Column("client_secret", sa.String(), nullable=False),
        sa.Column("redirect_uris", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("apps_pkey")),
    )
    op.drop_table("oauth_clients")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "oauth_clients",
        sa.Column("id", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column("name", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("client_id", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("client_secret", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("redirect_uris", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("is_active", sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="oauth_clients_pkey"),
    )
    op.drop_table("apps")
    # ### end Alembic commands ###
