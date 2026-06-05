from typing import Any

from fastid.auth.schemas import DiscoveryDocument, OpenID, ProviderMeta
from fastid.integrations.base.oauth import OAuth2Client


class YandexSSO(OAuth2Client):
    default_meta = ProviderMeta(
        name="yandex",
        title="Yandex",
        discovery=DiscoveryDocument(
            authorization_endpoint="https://oauth.yandex.ru/authorize",
            token_endpoint="https://oauth.yandex.ru/token",  # noqa: S106
            userinfo_endpoint="https://login.yandex.ru/info",
        ),
        scope=["login:email", "login:info", "login:avatar"],
    )
    avatar_url = "https://avatars.yandex.net/get-yapic"

    async def convert_userinfo(
        self,
        response: dict[str, Any],
    ) -> OpenID:
        picture = None
        if (avatar_id := response.get("default_avatar_id")) is not None:
            picture = f"{self.avatar_url}/{avatar_id}/islands-200"
        return OpenID(
            email=response.get("default_email"),
            display_name=response.get("display_name"),
            id=response.get("id"),
            first_name=response.get("first_name"),
            last_name=response.get("last_name"),
            picture=picture,
        )
