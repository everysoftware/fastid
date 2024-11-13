from typing import Annotated

from fastapi import Depends
from pydantic import AnyHttpUrl

from app.apps.exceptions import InvalidRedirectURI
from app.apps.models import App
from app.apps.schemas import AppDTO
from app.apps.service import AppUseCases

AppsDep = Annotated[AppUseCases, Depends()]


async def get_oauth_client(service: AppsDep, client_id: str) -> App:
    return await service.get_one(client_id)


async def valid_redirect_uri(
    client: Annotated[AppDTO, Depends(get_oauth_client)],
    redirect_uri: AnyHttpUrl,
) -> AnyHttpUrl:
    if redirect_uri.host not in {uri.host for uri in client.redirect_uris}:
        raise InvalidRedirectURI()
    return redirect_uri
