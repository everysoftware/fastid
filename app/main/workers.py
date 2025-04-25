from uvicorn_worker import UvicornWorker


class MyUvicornWorker(UvicornWorker):  # type: ignore[misc]  # pragma: nocover
    CONFIG_KWARGS = {"proxy_headers": True, "forwarded_allow_ips": "*"}
