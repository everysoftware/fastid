import logging


class LoggerFactory:
    def __init__(self) -> None:
        self.level = logging.INFO
        self.handler = logging.getHandlerByName("default")

    def create(self, name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(self.level)
        if self.handler:
            logger.addHandler(self.handler)
        logger.propagate = False
        return logger


logger_factory = LoggerFactory()
