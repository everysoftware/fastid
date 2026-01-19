from typing import Any

import httpx


class WebhookSender:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client

    async def send(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        async with self.client:
            try:
                response = await self.client.post(url, json=payload)
            except httpx.NetworkError as e:
                return {"status_code": 0, "content": {"error": str(e)}}
            try:
                content = response.json()
            except Exception:  # noqa: BLE001
                content = {"text": response.text}
            return {"status_code": response.status_code, "content": content}
