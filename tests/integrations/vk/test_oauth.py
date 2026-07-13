import json
from urllib.parse import parse_qs, urlparse

from fastid.auth.schemas import OAuth2Callback
from fastid.integrations.utils import generate_pkce_challenge, generate_pkce_verifier
from fastid.integrations.vk.oauth import VKSSO


async def test_pkce_enabled_by_default() -> None:
    client = VKSSO("client-id", "client-secret", "https://example.com/callback")

    login_url = await client.login_url(state="random-state-with-at-least-32-bytes")
    params = parse_qs(urlparse(login_url).query)

    state = "random-state-with-at-least-32-bytes"
    verifier = generate_pkce_verifier(state, "client-secret")
    assert params["state"] == [state]
    assert params["code_challenge"] == [generate_pkce_challenge(verifier)]
    assert params["code_challenge_method"] == ["s256"]
    assert urlparse(login_url).netloc == "id.vk.com"

    callback = OAuth2Callback(code="code", state=state, device_id="device-id")
    request = client._prepare_token_request(callback)  # noqa: SLF001
    token_params = parse_qs(request.content.decode())
    assert token_params["code_verifier"] == [verifier]
    assert token_params["device_id"] == ["device-id"]
    assert "client_secret" not in token_params


async def test_pkce_can_be_disabled() -> None:
    client = VKSSO("client-id", "client-secret", "https://example.com/callback", use_pkce=False)

    login_url = await client.login_url(state="state")
    assert "code_challenge" not in parse_qs(urlparse(login_url).query)

    request = client._prepare_token_request(  # noqa: SLF001
        OAuth2Callback(code="code", state="state", device_id="device-id")
    )
    assert "code_verifier" not in parse_qs(request.content.decode())


def test_callback_payload() -> None:
    payload = json.dumps({"code": "code", "state": "state", "type": "code_v2", "device_id": "device-id"})

    callback = OAuth2Callback(payload=payload)

    assert callback.code == "code"
    assert callback.state == "state"
    assert callback.device_id == "device-id"


async def test_convert_userinfo() -> None:
    client = VKSSO("client-id", "client-secret", "https://example.com/callback")

    user = await client.convert_userinfo(
        {
            "user_id": "42",
            "email": "pavel@example.com",
            "first_name": "Pavel",
            "last_name": "Durov",
            "avatar": "https://example.com/photo.jpg",
        }
    )

    assert user.id == "42"
    assert user.email == "pavel@example.com"
    assert user.first_name == "Pavel"
    assert user.last_name == "Durov"
    assert user.display_name == "Pavel Durov"
    assert user.picture == "https://example.com/photo.jpg"
