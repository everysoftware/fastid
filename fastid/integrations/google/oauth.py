from typing import Any

from fastid.auth.schemas import OpenID, ProviderMeta
from fastid.integrations.base.oauth import OAuth2Client
from fastid.integrations.exceptions import IntegrationError


class GoogleSSO(OAuth2Client):
    default_meta = ProviderMeta(
        name="google", title="Google", server_url="https://accounts.google.com", scope=["openid", "email", "profile"]
    )

    async def convert_userinfo(
        self,
        response: dict[str, Any],
    ) -> OpenID:
        if response.get("email_verified"):
            return OpenID(
                email=response.get("email"),
                id=response.get("sub"),
                first_name=response.get("given_name"),
                last_name=response.get("family_name"),
                display_name=response.get("name"),
                picture=response.get("picture"),
            )
        msg = f"User {response.get('email')} is not verified with Google"
        raise IntegrationError(msg)
