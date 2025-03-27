"""empty message

Revision ID: 5ee810fadd8e
Revises: 590f147f3dca
Create Date: 2024-09-05 20:30:09.308466

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5ee810fadd8e"
down_revision: str | None = "590f147f3dca"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "oidc_accounts",
        sa.Column("id", sa.Uuid(as_uuid=False), nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=False), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("access_token", sa.String(), nullable=False),
        sa.Column("id_token", sa.String(), nullable=True),
        sa.Column("refresh_token", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("first_name", sa.String(), nullable=True),
        sa.Column("last_name", sa.String(), nullable=True),
        sa.Column("display_name", sa.String(), nullable=True),
        sa.Column("picture", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("oidc_accounts_pkey")),
    )
    op.create_index(
        op.f("oidc_accounts_email_idx"),
        "oidc_accounts",
        ["email"],
        unique=False,
    )
    op.create_index(
        op.f("oidc_accounts_user_id_idx"),
        "oidc_accounts",
        ["user_id"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("oidc_accounts_user_id_idx"), table_name="oidc_accounts")
    op.drop_index(op.f("oidc_accounts_email_idx"), table_name="oidc_accounts")
    op.drop_table("oidc_accounts")
    # ### end Alembic commands ###
