import logging
from logging.config import dictConfig
from typing import Any, Literal


class LogProvider:
    def __init__(self, config: dict[str, Any]) -> None:
        dictConfig(config)

    def logger(
        self,
        name: str,
        handler: Literal["default", "instrumented"] = "instrumented",
    ) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.addHandler(self.handler(handler))
        logger.propagate = False
        return logger

    @staticmethod
    def handler(name: str) -> logging.Handler:
        handler = logging.getHandlerByName(name)
        assert handler is not None
        return handler
