from pathlib import Path

import alembic
from alembic.script import ScriptDirectory

parent_dir = Path(__file__).resolve().parent.parent
alembic_cfg = alembic.config.Config(str(parent_dir.joinpath("alembic.ini")))
alembic_cfg.set_main_option("script_location", str(parent_dir.joinpath("alembic")))

# Create Alembic configuration object
# (we don't need database for getting revisions list)
# Get directory object with Alembic migrations
revisions_dir = ScriptDirectory.from_config(alembic_cfg)
