import logging
from logging.config import dictConfig
from typing import Literal

import uvicorn.logging

default_formatter = {
    "()": uvicorn.logging.DefaultFormatter,
    "fmt": "%(asctime)s %(levelprefix)s [%(name)s] [%(filename)s:%(lineno)d] - %(message)s",
    "datefmt": "%Y-%m-%d %H:%M:%S",
    "use_colors": True,
}

access_formatter = {
    "()": uvicorn.logging.AccessFormatter,
    "fmt": "%(asctime)s %(levelprefix)s [%(name)s] [%(filename)s:%(lineno)d] - %(client_addr)s - '%(request_line)s' %(status_code)s",
    "datefmt": "%Y-%m-%d %H:%M:%S",
    "use_colors": True,
}

instrumented_formatter = {
    "()": uvicorn.logging.DefaultFormatter,
    "fmt": "%(asctime)s %(levelprefix)s [%(name)s] [%(filename)s:%(lineno)d] - %(message)s",
    "datefmt": "%Y-%m-%d %H:%M:%S",
    "use_colors": True,
}


def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "access": access_formatter,
                "default": default_formatter,
                "instrumented": instrumented_formatter,
            },
            "handlers": {
                "access": {
                    "formatter": "access",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
                "instrumented": {
                    "formatter": "instrumented",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                "sqlalchemy.engine": {
                    "level": "INFO",
                    "handlers": ["instrumented"],
                    "propagate": False,
                },
                "httpx": {
                    "level": "INFO",
                    "handlers": ["instrumented"],
                    "propagate": False,
                },
                "uvicorn.error": {
                    "level": "INFO",
                    "handlers": ["default"],
                    "propagate": False,
                },
                "uvicorn.access": {
                    "level": "INFO",
                    "handlers": ["access"],
                    "propagate": False,
                },
                "uvicorn": {
                    "level": "DEBUG",
                    "handlers": ["default"],
                    "propagate": True,
                },
                "gunicorn.error": {
                    "level": "INFO",
                    "handlers": ["default"],
                    "propagate": False,
                },
                "gunicorn.access": {
                    "level": "INFO",
                    "handlers": ["access"],
                    "propagate": False,
                },
                "gunicorn": {
                    "level": "INFO",
                    "handlers": ["default"],
                    "propagate": True,
                },
            },
            "root": {
                "level": "INFO",
                "handlers": ["default"],
            },
        }
    )


def get_handler(name: str) -> logging.Handler:
    handler = logging.getHandlerByName(name)
    assert handler is not None
    return handler


def get_logger(
    name: str,
    level: int = logging.INFO,
    handler: Literal["default", "instrumented"] = "instrumented",
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(get_handler(handler))
    logger.propagate = False
    return logger


configure_logging()
