from typing import Any

import httpx

from app.oauthlib.base import (
    BaseOAuth2,
)
from app.oauthlib.exceptions import OAuth2Error
from app.oauthlib.schemas import OpenID, DiscoveryDocument


class GoogleOAuth(BaseOAuth2):
    discovery_url = (
        "https://accounts.google.com/.well-known/openid-configuration"
    )
    provider = "google"
    scope = ["openid", "email", "profile"]

    async def discover(self) -> DiscoveryDocument:
        async with httpx.AsyncClient() as session:
            response = await session.get(self.discovery_url)
            content = response.json()
            return DiscoveryDocument.model_validate(content)

    async def openid_from_response(
        self,
        response: dict[Any, Any],
    ) -> OpenID:
        if response.get("email_verified"):
            return OpenID(
                email=response.get("email"),
                provider=self.provider,
                id=response.get("sub"),
                first_name=response.get("given_name"),
                last_name=response.get("family_name"),
                display_name=response.get("name"),
                picture=response.get("picture"),
            )
        raise OAuth2Error(
            f"User {response.get('email')} is not verified with Google"
        )