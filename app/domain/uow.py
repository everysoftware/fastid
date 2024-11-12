from __future__ import annotations

import abc
from abc import ABC
from typing import Self, Any

from app.apps.repositories import IAppRepository
from app.auth.repositories import IUserRepository
from app.social_login.repositories import IOAuthAccountRepository


class IUnitOfWork(ABC):
    users: IUserRepository
    oauth_accounts: IOAuthAccountRepository
    apps: IAppRepository

    @abc.abstractmethod
    async def begin(self) -> None: ...

    @property
    @abc.abstractmethod
    def is_active(self) -> bool: ...

    @abc.abstractmethod
    async def commit(self) -> None: ...

    @abc.abstractmethod
    async def rollback(self) -> None: ...

    @abc.abstractmethod
    async def close(self) -> None: ...

    async def __aenter__(self) -> Self:
        await self.begin()
        return self

    async def __aexit__(
        self, exc_type: Any, exc_value: Any, traceback: Any
    ) -> None:
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
        await self.close()
