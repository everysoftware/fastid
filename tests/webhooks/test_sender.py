import httpx
import pytest
from starlette import status

from fastid.webhooks.config import webhook_settings
from fastid.webhooks.senders.httpx import WebhookSender, resolve_targets
from tests.mocks import faker


async def test_sender_does_not_follow_redirects(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(webhook_settings, "allow_insecure_urls", True)

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.content == b'{"ok":true}'
        return httpx.Response(302, headers={"Location": "http://127.0.0.1/private"}, text="redirect")

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        result = await WebhookSender(client).send("http://example.test/hook", b'{"ok":true}', {})

    assert result.status_code == status.HTTP_302_FOUND
    assert result.content == {"value": "redirect"}


async def test_sender_bounds_response(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(webhook_settings, "allow_insecure_urls", True)
    monkeypatch.setattr(webhook_settings, "max_response_bytes", 4)

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda _request: httpx.Response(status.HTTP_200_OK, text="123456"))
    ) as client:
        result = await WebhookSender(client).send("http://example.test/hook", b"{}", {})

    assert result.content == {"value": 1234, "truncated": True}


@pytest.mark.parametrize(
    ("url", "message"),
    [("http://example.com/hook", "HTTPS"), (f"https://user:{faker.password()}@example.com/hook", "credentials")],
)
async def test_resolve_targets_rejects_unsafe_url(monkeypatch: pytest.MonkeyPatch, url: str, message: str) -> None:
    monkeypatch.setattr(webhook_settings, "allow_insecure_urls", False)

    with pytest.raises(ValueError, match=message):
        await resolve_targets(url)


async def test_resolve_targets_rejects_loopback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(webhook_settings, "allow_insecure_urls", False)

    with pytest.raises(ValueError, match="non-public"):
        await resolve_targets("https://127.0.0.1/hook")
