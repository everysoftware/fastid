import pytest

from app.auth.models import User
from app.auth.repositories import UserEmailSpecification
from app.db.exceptions import NoResultFoundError
from app.db.uow import IUnitOfWork
from tests import mocks


def test_repository_add(mock_user: User) -> None:
    assert mock_user.id is not None
    assert mock_user.first_name == mocks.USER_CREATE["first_name"]
    assert mock_user.last_name == mocks.USER_CREATE["last_name"]
    assert mock_user.email == mocks.USER_CREATE["email"]
    assert mock_user.created_at is not None
    assert mock_user.updated_at is not None


async def test_repository_get(uow: IUnitOfWork, mock_user: User) -> None:
    user = await uow.users.get_one(mock_user.id)
    assert user == mock_user


async def test_repository_update(uow: IUnitOfWork, mock_user: User) -> None:
    mock_user.first_name = "Jane"
    await uow.commit()

    user = await uow.users.get_one(mock_user.id)
    assert user.first_name == "Jane"


async def test_repository_delete(uow: IUnitOfWork, mock_user: User) -> None:
    await uow.users.delete(mock_user)
    await uow.commit()

    with pytest.raises(NoResultFoundError):
        await uow.users.get_one(mock_user.id)


async def test_repository_find(uow: IUnitOfWork, mock_user: User) -> None:
    assert mock_user.email is not None
    user = await uow.users.find_one(UserEmailSpecification(mock_user.email))
    assert user == mock_user


async def test_repository_get_many(uow: IUnitOfWork, mock_user: User) -> None:
    page = await uow.users.get_many()
    assert page.total == 1
    assert page.items[0] == mock_user
