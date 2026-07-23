import asyncio
import ipaddress
import json
import socket
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime

import httpx

from fastid.webhooks.config import webhook_settings

HTTPS_PORT = 443


class UnsafeWebhookURLError(ValueError):
    pass


@dataclass(frozen=True)
class ResolvedTarget:
    url: httpx.URL
    host_header: str
    sni_hostname: str | None


@dataclass(frozen=True)
class WebhookResponse:
    status_code: int
    content: dict[str, object]
    error: str | None
    retry_after_seconds: int | None
    duration_ms: int


async def resolve_targets(value: str) -> list[ResolvedTarget]:
    url = httpx.URL(value)
    if not url.host:
        msg = "Webhook URL must include a host"
        raise UnsafeWebhookURLError(msg)
    if url.username or url.password:
        msg = "Webhook URL must not include credentials"
        raise UnsafeWebhookURLError(msg)
    if webhook_settings.allow_insecure_urls:
        return [ResolvedTarget(url=url, host_header=_host_header(url), sni_hostname=url.host)]
    if url.scheme != "https":
        msg = "Webhook URL must use HTTPS"
        raise UnsafeWebhookURLError(msg)

    port = url.port or HTTPS_PORT
    loop = asyncio.get_running_loop()
    try:
        records = await loop.getaddrinfo(url.host, port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        msg = f"Webhook host could not be resolved: {exc}"
        raise UnsafeWebhookURLError(msg) from exc
    addresses = list(dict.fromkeys(record[4][0].split("%", 1)[0] for record in records))
    if not addresses:
        msg = "Webhook host did not resolve to an address"
        raise UnsafeWebhookURLError(msg)
    parsed = [ipaddress.ip_address(address) for address in addresses]
    if any(not address.is_global for address in parsed):
        msg = "Webhook host resolves to a non-public address"
        raise UnsafeWebhookURLError(msg)
    return [
        ResolvedTarget(url=url.copy_with(host=str(address)), host_header=_host_header(url), sni_hostname=url.host)
        for address in parsed
    ]


def _host_header(url: httpx.URL) -> str:
    host = url.host
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    if url.port and url.port != HTTPS_PORT:
        return f"{host}:{url.port}"
    return host


def _retry_after(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return max(0, int(value))
    except ValueError:
        try:
            retry_at = parsedate_to_datetime(value)
        except (TypeError, ValueError):
            return None
        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=UTC)
        return max(0, int((retry_at - datetime.now(UTC)).total_seconds()))


def _content(raw: bytes, *, truncated: bool) -> dict[str, object]:
    text = raw.decode(errors="replace")
    try:
        value = json.loads(text) if text else None
    except json.JSONDecodeError:
        value = text
    content: dict[str, object] = value if isinstance(value, dict) else {"value": value}
    if truncated:
        content["truncated"] = True
    return content


class WebhookSender:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client

    async def send(self, url: str, body: bytes, headers: dict[str, str]) -> WebhookResponse:
        started = time.monotonic()
        try:
            targets = await resolve_targets(url)
        except UnsafeWebhookURLError as exc:
            return self._error(exc, started)

        last_error: httpx.RequestError | None = None
        for target in targets:
            request_headers = headers | {"Host": target.host_header}
            extensions = {"sni_hostname": target.sni_hostname} if target.sni_hostname else None
            request = self.client.build_request(
                "POST", target.url, content=body, headers=request_headers, extensions=extensions
            )
            try:
                response = await self.client.send(request, stream=True, follow_redirects=False)
            except httpx.RequestError as exc:
                last_error = exc
                continue
            try:
                raw = bytearray()
                truncated = False
                async for chunk in response.aiter_bytes():
                    remaining = webhook_settings.max_response_bytes - len(raw)
                    if remaining <= 0:
                        truncated = True
                        break
                    raw.extend(chunk[:remaining])
                    if len(chunk) > remaining:
                        truncated = True
                        break
            finally:
                await response.aclose()
            return WebhookResponse(
                status_code=response.status_code,
                content=_content(bytes(raw), truncated=truncated),
                error=None,
                retry_after_seconds=_retry_after(response.headers.get("Retry-After")),
                duration_ms=int((time.monotonic() - started) * 1000),
            )
        assert last_error is not None
        return self._error(last_error, started)

    @staticmethod
    def _error(exc: Exception, started: float) -> WebhookResponse:
        return WebhookResponse(
            status_code=0,
            content={"error": str(exc)},
            error=str(exc),
            retry_after_seconds=None,
            duration_ms=int((time.monotonic() - started) * 1000),
        )
