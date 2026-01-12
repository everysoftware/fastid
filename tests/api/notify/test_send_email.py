import pytest
from fastlink.schemas import TokenResponse
from httpx import AsyncClient
from starlette import status

from fastid.auth.schemas import UserDTO
from fastid.database.uow import SQLAlchemyUOW
from tests import mocks


async def test_send_email(client: AsyncClient, user_token: TokenResponse) -> None:
    response = await client.post(
        "/email/send",
        headers={"Authorization": f"Bearer {user_token.access_token}"},
        json=mocks.PUSH_NOTIFICATION_REQUEST.model_dump(mode="json"),
    )
    assert response.status_code == status.HTTP_200_OK


async def test_send_email_fake_template(client: AsyncClient, user_token: TokenResponse) -> None:
    with pytest.raises(RuntimeError):
        await client.post(
            "/email/send",
            headers={"Authorization": f"Bearer {user_token.access_token}"},
            json=mocks.PUSH_NOTIFICATION_REQUEST_FAKE_TEMPLATE.model_dump(mode="json"),
        )


async def test_send_email_no_email(
    client: AsyncClient, uow: SQLAlchemyUOW, user: UserDTO, user_token: TokenResponse
) -> None:
    user_orm = await uow.users.get(user.id)
    user_orm.email = None
    await uow.commit()

    with pytest.raises(RuntimeError):
        await client.post(
            "/email/send",
            headers={"Authorization": f"Bearer {user_token.access_token}"},
            json=mocks.PUSH_NOTIFICATION_REQUEST.model_dump(mode="json"),
        )
