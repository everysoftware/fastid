from typing import Annotated

from fastapi import Depends, Request

from fastid.auth.config import auth_settings
from fastid.core.config import CoreSettings
from fastid.core.dependencies import get_core_settings


def get_server_url(
    request: Request,
    settings: CoreSettings = Depends(get_core_settings),
) -> str:
    if auth_settings.server_url is not None:
        return auth_settings.server_url.rstrip("/")
    if settings.behind_proxy:
        forwarded_host = request.headers.get("X-Forwarded-Host")
        forwarded_proto = request.headers.get("X-Forwarded-Proto", "http")
        if forwarded_host:
            return f"{forwarded_proto}://{forwarded_host}"
    base_url = str(request.base_url).rstrip("/")
    root_path = str(request.scope.get("root_path", "")).rstrip("/")
    if root_path and base_url.endswith(root_path):
        return base_url[: -len(root_path)]
    return base_url


ServerURLDep = Annotated[str, Depends(get_server_url)]
