"""
Test can find forgotten downgrade methods, undeleted data types in downgrade
methods, typos and many other errors.

Does not require any maintenance - you just add it once to check 80% of typos
and mistakes in migrations forever.
"""

import pytest
from alembic.command import downgrade, upgrade

from tests.conftest import alembic_cfg, revisions_dir


def get_revisions():
    """Get revisions for stairway test."""
    # Get & sort migrations, from first to last
    revisions = list(revisions_dir.walk_revisions("base", "heads"))
    revisions.reverse()
    return revisions


@pytest.mark.db
@pytest.mark.parametrize("revision", get_revisions())
def test_migrations_stairway(revision):
    """Stairway tests."""
    upgrade(alembic_cfg, revision.revision)

    # We need -1 for downgrading first migration (its down_revision is None)
    downgrade(alembic_cfg, revision.down_revision or "-1")
    upgrade(alembic_cfg, revision.revision)
