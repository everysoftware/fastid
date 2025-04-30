from abc import ABC, abstractmethod
from typing import Any


class Specification(ABC):
    @abstractmethod
    def apply(self, *args: Any, **kwargs: Any) -> Any: ...
