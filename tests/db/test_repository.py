import pytest

from app.auth.models import User
from app.auth.repositories import UserEmailSpecification
from app.db.exceptions import NoResultFoundError
from app.db.uow import IUnitOfWork
from tests import mocks


def test_repository_add(test_user: User) -> None:
    assert test_user.id is not None
    assert test_user.first_name == mocks.USER_CREATE["first_name"]
    assert test_user.last_name == mocks.USER_CREATE["last_name"]
    assert test_user.email == mocks.USER_CREATE["email"]
    assert test_user.created_at is not None
    assert test_user.updated_at is not None


async def test_repository_get(uow: IUnitOfWork, test_user: User) -> None:
    user = await uow.users.get_one(test_user.id)
    assert user == test_user


async def test_repository_update(uow: IUnitOfWork, test_user: User) -> None:
    test_user.first_name = "Jane"
    await uow.commit()

    user = await uow.users.get_one(test_user.id)
    assert user.first_name == "Jane"


async def test_repository_delete(uow: IUnitOfWork, test_user: User) -> None:
    await uow.users.remove(test_user)
    await uow.commit()

    with pytest.raises(NoResultFoundError):
        await uow.users.get_one(test_user.id)


async def test_repository_find(uow: IUnitOfWork, test_user: User) -> None:
    assert test_user.email is not None
    user = await uow.users.find_one(UserEmailSpecification(test_user.email))
    assert user == test_user


async def test_repository_get_many(uow: IUnitOfWork, test_user: User) -> None:
    page = await uow.users.get_many()
    assert page.total == 1
    assert page.items[0] == test_user
