import logging
import os

from uvicorn_worker import UvicornWorker


class MyUvicornWorker(UvicornWorker):  # type: ignore[misc]  # pragma: nocover
    ACCESS_LOG = os.getenv("FASTID_GUNICORN_ACCESS_LOG", "true").lower() in {"1", "true", "yes", "on"}
    CONFIG_KWARGS = {
        "loop": "uvloop",
        "http": "httptools",
        "proxy_headers": True,
        "forwarded_allow_ips": "*",
        "access_log": ACCESS_LOG,
    }

    async def _serve(self) -> None:
        # Loading the FastAPI app configures logging after init_process, so
        # disable the logger immediately before Uvicorn starts serving.
        if not self.ACCESS_LOG:
            logging.getLogger("uvicorn.access").disabled = True
        await super()._serve()
