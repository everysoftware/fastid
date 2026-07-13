import pytest
from httpx import AsyncClient
from starlette import status

from fastid.auth.config import auth_settings
from fastid.auth.schemas import JWKS, DiscoveryDocument
from fastid.core.config import core_settings


async def test_openid_configuration(
    frontend_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(core_settings, "public_url", None)
    monkeypatch.setattr(core_settings, "behind_proxy", False)
    response = await frontend_client.get(
        "/.well-known/openid-configuration",
        headers={
            "X-Forwarded-Host": "ignored.example.com",
            "X-Forwarded-Proto": "https",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    document = DiscoveryDocument.model_validate_json(response.content)
    request_origin = "http://testserver"
    assert document.issuer == request_origin
    assert document.authorization_endpoint == f"{request_origin}/authorize"
    assert document.token_endpoint == f"{request_origin}/api/v1/token"
    assert document.userinfo_endpoint == f"{request_origin}/api/v1/userinfo"
    assert document.jwks_uri == f"{request_origin}/.well-known/jwks.json"


async def test_openid_configuration_behind_proxy(
    frontend_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(core_settings, "public_url", None)
    monkeypatch.setattr(core_settings, "behind_proxy", True)
    response = await frontend_client.get(
        "/.well-known/openid-configuration",
        headers={
            "X-Forwarded-Host": "identity.example.com",
            "X-Forwarded-Proto": "https",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    document = DiscoveryDocument.model_validate_json(response.content)
    proxy_origin = "https://identity.example.com"
    assert document.issuer == proxy_origin
    assert document.authorization_endpoint == f"{proxy_origin}/authorize"
    assert document.token_endpoint == f"{proxy_origin}/api/v1/token"
    assert document.userinfo_endpoint == f"{proxy_origin}/api/v1/userinfo"
    assert document.jwks_uri == f"{proxy_origin}/.well-known/jwks.json"


async def test_openid_configuration_with_configured_public_url(
    frontend_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server_url = "https://configured.example.com"
    monkeypatch.setattr(core_settings, "public_url", f"{server_url}/")
    monkeypatch.setattr(core_settings, "behind_proxy", True)

    response = await frontend_client.get(
        "/.well-known/openid-configuration",
        headers={
            "X-Forwarded-Host": "ignored.example.com",
            "X-Forwarded-Proto": "http",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    document = DiscoveryDocument.model_validate_json(response.content)
    assert auth_settings.server_url == server_url
    assert document.issuer == server_url
    assert document.authorization_endpoint == f"{server_url}/authorize"
    assert document.token_endpoint == f"{server_url}/api/v1/token"
    assert document.userinfo_endpoint == f"{server_url}/api/v1/userinfo"
    assert document.jwks_uri == f"{server_url}/.well-known/jwks.json"


async def test_jwks(frontend_client: AsyncClient) -> None:
    response = await frontend_client.get("/.well-known/jwks.json")
    assert response.status_code == status.HTTP_200_OK
    JWKS.model_validate_json(response.content)
