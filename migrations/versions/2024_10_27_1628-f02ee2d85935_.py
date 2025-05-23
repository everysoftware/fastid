"""empty message

Revision ID: f02ee2d85935
Revises: 523057551f5c
Create Date: 2024-10-27 16:28:42.694436

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "f02ee2d85935"
down_revision: str | None = "523057551f5c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "oauth_accounts",
        sa.Column("id", sa.Uuid(as_uuid=False), nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=False), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("account_id", sa.String(), nullable=False),
        sa.Column("access_token", sa.String(), nullable=True),
        sa.Column("expires_in", sa.BigInteger(), nullable=True),
        sa.Column("scope", sa.String(), nullable=True),
        sa.Column("id_token", sa.String(), nullable=True),
        sa.Column("refresh_token", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("first_name", sa.String(), nullable=True),
        sa.Column("last_name", sa.String(), nullable=True),
        sa.Column("display_name", sa.String(), nullable=True),
        sa.Column("picture", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("oauth_accounts_pkey")),
    )
    op.create_index(
        op.f("oauth_accounts_email_idx"),
        "oauth_accounts",
        ["email"],
        unique=False,
    )
    op.create_index(
        op.f("oauth_accounts_user_id_idx"),
        "oauth_accounts",
        ["user_id"],
        unique=False,
    )
    op.create_table(
        "oauth_clients",
        sa.Column("id", sa.Uuid(as_uuid=False), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("client_id", sa.String(), nullable=False),
        sa.Column("client_secret", sa.String(), nullable=False),
        sa.Column("redirect_uris", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("oauth_clients_pkey")),
    )
    op.drop_table("clients")
    op.drop_index("sso_accounts_email_idx", table_name="sso_accounts")
    op.drop_index("sso_accounts_user_id_idx", table_name="sso_accounts")
    op.drop_table("sso_accounts")
    op.add_column("users", sa.Column("new_email", sa.String(), nullable=True))
    op.alter_column("users", "first_name", existing_type=sa.VARCHAR(), nullable=False)
    op.create_index(op.f("users_new_email_idx"), "users", ["new_email"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("users_new_email_idx"), table_name="users")
    op.alter_column("users", "first_name", existing_type=sa.VARCHAR(), nullable=True)
    op.drop_column("users", "new_email")
    op.create_table(
        "sso_accounts",
        sa.Column("id", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column("user_id", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column("provider", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("account_id", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("access_token", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("expires_in", sa.BIGINT(), autoincrement=False, nullable=True),
        sa.Column("scope", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("id_token", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("refresh_token", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("email", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("first_name", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("last_name", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("display_name", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("picture", sa.VARCHAR(), autoincrement=False, nullable=True),
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
        sa.PrimaryKeyConstraint("id", name="sso_accounts_pkey"),
    )
    op.create_index("sso_accounts_user_id_idx", "sso_accounts", ["user_id"], unique=False)
    op.create_index("sso_accounts_email_idx", "sso_accounts", ["email"], unique=False)
    op.create_table(
        "clients",
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
        sa.PrimaryKeyConstraint("id", name="clients_pkey"),
    )
    op.drop_table("oauth_clients")
    op.drop_index(op.f("oauth_accounts_user_id_idx"), table_name="oauth_accounts")
    op.drop_index(op.f("oauth_accounts_email_idx"), table_name="oauth_accounts")
    op.drop_table("oauth_accounts")
    # ### end Alembic commands ###
