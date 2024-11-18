"""empty message

Revision ID: 446313a37068
Revises: 3282fde15451
Create Date: 2024-11-17 19:14:48.891033

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "446313a37068"
down_revision: Union[str, None] = "3282fde15451"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("apps", sa.Column("slug", sa.String(), nullable=False))
    op.create_unique_constraint(op.f("apps_slug_key"), "apps", ["slug"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f("apps_slug_key"), "apps", type_="unique")
    op.drop_column("apps", "slug")
    # ### end Alembic commands ###