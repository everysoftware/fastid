from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)

from app.db.config import db_settings


class DBHelper:
    def __init__(self, url: URL | str, *, echo: bool = False) -> None:
        self.url = url
        self.echo = echo

        self.engine = create_async_engine(
            self.url,
            echo=self.echo,
            pool_pre_ping=True,
        )
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)


db = DBHelper(db_settings.url, echo=db_settings.echo)
engine = db.engine
session_factory = db.session_factory
