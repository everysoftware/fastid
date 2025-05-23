"""
Test can find forgotten downgrade methods, undeleted data types in downgrade
methods, typos and many other errors.

Does not require any maintenance - you just add it once to check 80% of typos
and mistakes in migrations forever.
"""

import pytest
from alembic.command import downgrade, upgrade
from alembic.script import Script, ScriptDirectory

from tests.dependencies import alembic_config
from tests.utils.alembic import alembic_config_from_url


def get_revisions() -> list[Script]:
    """Get revisions for stairway test."""
    # Create Alembic configuration object
    # (we don't need database for getting revisions list)
    config = alembic_config_from_url()
    # Get directory object with Alembic migrations
    revisions_dir = ScriptDirectory.from_config(config)
    revisions_dir.get_current_head()
    # Get & sort migrations, from first to last
    revisions = list(revisions_dir.walk_revisions("base", "heads"))
    revisions.reverse()
    return revisions


@pytest.mark.parametrize("revision", get_revisions())
def test_migrations_stairway(revision: Script) -> None:
    """Stairway tests."""
    upgrade(alembic_config, revision.revision)

    # We need -1 for downgrading first migration (its down_revision is None)
    downgrade(alembic_config, revision.down_revision or "-1")  # type: ignore[arg-type]
    upgrade(alembic_config, revision.revision)
