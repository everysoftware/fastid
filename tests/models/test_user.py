import pytest

from fastid.auth.models import User
from fastid.auth.schemas import Contact, ContactType


@pytest.mark.parametrize(
    ("user", "display_name"),
    [
        (User(first_name="John", last_name="Doe"), "John Doe"),
        (User(first_name="John"), "John"),
    ],
)
def test_user_display_name(user: User, display_name: str) -> None:
    assert user.display_name == display_name


def test_user_display_name_no_names() -> None:
    user = User()
    with pytest.raises(ValueError):  # noqa: PT011
        _ = user.display_name


@pytest.mark.parametrize(
    ("user", "notification_method"),
    [
        (User(email="user@example.com"), Contact(type=ContactType.email, recipient={"email": "user@example.com"})),
        (User(telegram_id=1), Contact(type=ContactType.telegram, recipient={"telegram_id": 1})),
        (
            User(email="user@example.com", telegram_id=1),
            Contact(type=ContactType.telegram, recipient={"telegram_id": 1}),
        ),
    ],
)
def test_user_notification_method(user: User, contact: Contact) -> None:
    assert user.find_priority_contact() == contact


def test_user_notification_method_no_contacts() -> None:
    user = User()
    with pytest.raises(ValueError):  # noqa: PT011
        _ = user.find_priority_contact()
