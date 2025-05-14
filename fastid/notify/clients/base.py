from abc import ABC, abstractmethod
from typing import Any, Self

from fastid.notify.clients.schemas import Notification


class NotificationClient(ABC):
    @abstractmethod
    async def send(self, notification: Notification) -> None: ...

    @abstractmethod
    async def __aenter__(self) -> Self: ...

    @abstractmethod
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None: ...
