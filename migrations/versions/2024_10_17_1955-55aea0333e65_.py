"""empty message

Revision ID: 55aea0333e65
Revises: 9d66ac80082e
Create Date: 2024-10-17 19:55:02.571419

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "55aea0333e65"
down_revision: Union[str, None] = "9d66ac80082e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("apps_user_id_idx", table_name="apps")
    op.drop_column("apps", "user_id")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "apps",
        sa.Column("user_id", sa.UUID(), autoincrement=False, nullable=False),
    )
    op.create_index("apps_user_id_idx", "apps", ["user_id"], unique=False)
    # ### end Alembic commands ###
