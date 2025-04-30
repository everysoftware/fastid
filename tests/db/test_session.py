from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastid.auth.models import User


async def test_session_execute(session: AsyncSession) -> None:
    result = await session.execute(select(1))
    assert result.scalar() == 1


async def test_session_orm(session: AsyncSession) -> None:
    user = User(first_name="John", last_name="Smith")
    session.add(user)
    await session.commit()

    # Refresh the instance to get the updated values from the database
    await session.refresh(user)

    # Assertions to check the user instance
    assert user.id is not None
    assert user.first_name == "John"
    assert user.last_name == "Smith"
    assert user.is_active
    assert not user.is_verified
    assert not user.is_superuser
    assert user.created_at is not None
    assert user.updated_at is not None
