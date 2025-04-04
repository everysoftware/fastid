"""empty message

Revision ID: bd54ebc87d2a
Revises: 7eb88ab78714
Create Date: 2024-09-09 17:44:43.516618

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bd54ebc87d2a"
down_revision: str | None = "7eb88ab78714"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "oidc_accounts",
        "account_id",
        existing_type=sa.VARCHAR(),
        nullable=False,
    )
    op.alter_column("users", "email", existing_type=sa.VARCHAR(length=320), nullable=True)
    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.VARCHAR(length=1024),
        nullable=True,
    )
    op.drop_index("users_email_idx", table_name="users")
    op.create_index(op.f("users_email_idx"), "users", ["email"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("users_email_idx"), table_name="users")
    op.create_index("users_email_idx", "users", ["email"], unique=True)
    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.VARCHAR(length=1024),
        nullable=False,
    )
    op.alter_column("users", "email", existing_type=sa.VARCHAR(length=320), nullable=False)
    op.alter_column(
        "oidc_accounts",
        "account_id",
        existing_type=sa.VARCHAR(),
        nullable=True,
    )
    # ### end Alembic commands ###
