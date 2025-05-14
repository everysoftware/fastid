import pytest

from fastid.auth.models import User


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
        (User(email="user@example.com"), "email"),
        (User(telegram_id=1), "telegram"),
        (User(email="user@example.com", telegram_id=1), "telegram"),
    ],
)
def test_user_notification_method(user: User, notification_method: str) -> None:
    assert user.notification_method == notification_method


def test_user_notification_method_no_contacts() -> None:
    user = User()
    with pytest.raises(ValueError):  # noqa: PT011
        _ = user.notification_method
