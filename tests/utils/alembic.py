"""Alembic utils for tests."""

from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace

from alembic.config import Config
from sqlalchemy import URL

PROJECT_PATH = Path(__file__).parent.parent.parent.resolve()


def make_alembic_config(cmd_opts: Namespace | SimpleNamespace, base_path: str = str(PROJECT_PATH)) -> Config:
    """Make alembic config for stairway integration tests."""
    # Replace path to alembic.ini file to absolute
    if not Path(cmd_opts.config).is_absolute():
        cmd_opts.config = str(Path(base_path) / Path(cmd_opts.config))

    config = Config(
        file_=cmd_opts.config,
        ini_section=cmd_opts.name,
        cmd_opts=cmd_opts,  # type: ignore[arg-type]
    )

    # Replace path to alembic folder to absolute
    alembic_location = config.get_main_option("script_location")
    assert alembic_location is not None
    if not Path(alembic_location).is_absolute():
        config.set_main_option("script_location", str(Path(base_path) / Path(alembic_location)))
    if cmd_opts.pg_url:
        config.set_main_option("sqlalchemy.url", cmd_opts.pg_url)

    return config


def alembic_config_from_url(pg_url: URL | str | None = None) -> Config:
    """Provides Python object, representing alembic.ini file."""
    if isinstance(pg_url, URL):
        pg_url = pg_url.render_as_string(hide_password=False)
    cmd_options = SimpleNamespace(
        config="alembic.ini",  # Config file name
        name="alembic",  # Name of section in .ini file to use for Alembic config
        pg_url=pg_url,  # DB URI
        raiseerr=True,  # Raise a full stack trace on error
        x=None,  # Additional arguments consumed by custom env.py scripts
    )
    return make_alembic_config(cmd_options)
