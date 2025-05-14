import pytest

from fastid.api.exceptions import ValidationError
from fastid.auth.models import User
from fastid.auth.repositories import UserEmailSpecification
from fastid.database.exceptions import NoResultFoundError, NotSupportedPaginationError
from fastid.database.schemas import LimitOffset, Pagination, Sorting
from fastid.database.uow import SQLAlchemyUOW
from fastid.database.utils import uuid
from tests import mocks


def test_repository_add(mock_user: User) -> None:
    assert mock_user.id is not None
    assert mock_user.first_name == mocks.USER_RECORD["first_name"]
    assert mock_user.last_name == mocks.USER_RECORD["last_name"]
    assert mock_user.email == mocks.USER_RECORD["email"]
    assert mock_user.created_at is not None
    assert mock_user.updated_at is not None


async def test_repository_get(uow: SQLAlchemyUOW, mock_user: User) -> None:
    user = await uow.users.get(mock_user.id)
    assert user == mock_user


async def test_repository_get_not_exists(uow: SQLAlchemyUOW) -> None:
    with pytest.raises(NoResultFoundError):
        await uow.users.get(uuid())


async def test_repository_update(uow: SQLAlchemyUOW, mock_user: User) -> None:
    mock_user.first_name = "Jane"
    await uow.commit()

    user = await uow.users.get(mock_user.id)
    assert user.first_name == "Jane"


async def test_repository_delete(uow: SQLAlchemyUOW, mock_user: User) -> None:
    await uow.users.delete(mock_user)
    await uow.commit()

    with pytest.raises(NoResultFoundError):
        await uow.users.get(mock_user.id)


async def test_repository_find(uow: SQLAlchemyUOW, mock_user: User) -> None:
    assert mock_user.email is not None
    user = await uow.users.find(UserEmailSpecification(mock_user.email))
    assert user == mock_user


async def test_repository_find_non_existent(uow: SQLAlchemyUOW) -> None:
    with pytest.raises(NoResultFoundError):
        await uow.users.find(UserEmailSpecification("user@example.com"))


@pytest.mark.parametrize(
    "sorting",
    [
        Sorting(),
        Sorting(sort="created_at"),
        Sorting(sort="created_at:desc"),
        Sorting(sort="created_at:asc"),
        Sorting(sort="created_at:asc,updated_at:asc"),
        Sorting(sort="created_at:desc,updated_at:asc"),
        Sorting(sort="created_at:asc,updated_at:desc"),
        Sorting(sort="created_at:desc,updated_at:desc"),
    ],
)
async def test_repository_get_many(uow: SQLAlchemyUOW, mock_user: User, sorting: Sorting) -> None:
    page = await uow.users.get_many(pagination=LimitOffset(), sorting=sorting)
    assert page.total == 1
    assert page.items[0] == mock_user


@pytest.mark.parametrize(
    "sorting",
    [
        Sorting(sort="incorrect:format:bla:bla:bla"),
        Sorting(sort="created_at:i_am_not_existing_order"),
        Sorting(sort="i_am_not_existing_field"),
    ],
)
def test_invalid_sorting(sorting: Sorting) -> None:
    with pytest.raises(ValidationError):
        sorting.render(User)


async def test_repository_get_many_unsupported_pagination(uow: SQLAlchemyUOW, mock_user: User) -> None:
    with pytest.raises(NotSupportedPaginationError):
        await uow.users.get_many(pagination=Pagination())
