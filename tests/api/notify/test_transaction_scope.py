from typing import Any
from unittest.mock import AsyncMock

from sqlalchemy import select

from fastid.auth.schemas import UserDTO
from fastid.notify.models import Notification, NotificationType
from fastid.notify.schemas import PushNotificationRequest
from fastid.notify.use_cases import NotificationUseCases
from tests.dependencies import get_test_cache, get_test_uow


async def test_email_delivery_releases_read_transaction(user: UserDTO) -> None:
    uow = get_test_uow()
    async with uow:
        user_orm = await uow.users.get(user.id)
    service = NotificationUseCases(uow, AsyncMock(), AsyncMock(), get_test_cache(), "http://testserver")

    async def deliver(**kwargs: Any) -> None:
        assert not service.uow.is_active
        assert not service.uow.session.in_transaction()

    service.mail.send = deliver
    await service.push_email(user_orm, PushNotificationRequest(template="welcome", context={"scope_test": True}))
    async with get_test_uow() as check:
        rows = (
            await check.session.scalars(
                select(Notification).where(
                    Notification.user_id == user.id, Notification.context["scope_test"].as_boolean().is_(True)
                )
            )
        ).all()
        assert len(rows) == 1
        assert rows[0].type == NotificationType.email
