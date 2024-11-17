"""empty message

Revision ID: 523057551f5c
Revises: 55aea0333e65
Create Date: 2024-10-17 20:21:09.898681

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "523057551f5c"
down_revision: Union[str, None] = "55aea0333e65"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "clients",
        sa.Column("id", sa.Uuid(as_uuid=False), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("client_id", sa.String(), nullable=False),
        sa.Column("client_secret", sa.String(), nullable=False),
        sa.Column("redirect_uris", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("clients_pkey")),
    )
    op.drop_table("apps")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "apps",
        sa.Column("id", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column("name", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("secret", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column(
            "redirect_uris", sa.VARCHAR(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "is_active", sa.BOOLEAN(), autoincrement=False, nullable=False
        ),
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
        sa.PrimaryKeyConstraint("id", name="apps_pkey"),
    )
    op.drop_table("clients")
    # ### end Alembic commands ###
