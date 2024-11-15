from uvicorn_worker import UvicornWorker


class MyUvicornWorker(UvicornWorker):  # type: ignore[misc]
    pass
