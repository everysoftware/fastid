from typing import Any

from fastid.auth.schemas import DiscoveryDocument, OAuth2Callback, OpenID, ProviderMeta
from fastid.integrations.base.oauth import OAuth2Client
from fastid.integrations.exceptions import UserinfoError
from fastid.integrations.schemas import UserinfoResponse


class VKSSO(OAuth2Client):
    default_use_pkce = True
    pkce_challenge_method = "s256"
    use_client_secret = False
    default_meta = ProviderMeta(
        name="vk",
        title="VK",
        discovery=DiscoveryDocument(
            authorization_endpoint="https://id.vk.com/authorize",
            token_endpoint="https://id.vk.com/oauth2/auth",  # noqa: S106
            userinfo_endpoint="https://id.vk.com/oauth2/user_info",
        ),
        scope=["email"],
    )

    def _prepare_token_request(
        self,
        callback: OAuth2Callback,
        *,
        body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        body = body or {}
        if callback.device_id is not None:
            body["device_id"] = callback.device_id
        return super()._prepare_token_request(callback, body=body, headers=headers)

    async def userinfo(self) -> UserinfoResponse:
        assert self.discovery.userinfo_endpoint is not None
        response = await self.client.post(
            self.discovery.userinfo_endpoint,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "client_id": self.client_id,
                "access_token": self.token.access_token,
            },
        )
        content = response.json()
        user = content.get("user")
        if response.is_error or not user:
            msg = "Getting userinfo failed: %s"
            raise UserinfoError(msg, content)

        userinfo = await self.convert_userinfo(user)
        return UserinfoResponse(userinfo=userinfo, userinfo_raw=content)

    async def convert_userinfo(self, response: dict[str, Any]) -> OpenID:
        first_name = response.get("first_name")
        last_name = response.get("last_name")
        return OpenID(
            id=str(response["user_id"]),
            email=response.get("email"),
            first_name=first_name,
            last_name=last_name,
            display_name=" ".join(filter(None, (first_name, last_name))) or None,
            picture=response.get("avatar"),
        )
