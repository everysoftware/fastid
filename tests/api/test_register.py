from app.auth.schemas import UserDTO
from tests.mocks import USER_CREATE


def test_register(user: UserDTO) -> None:
    assert user.first_name == USER_CREATE.first_name
    assert user.last_name == USER_CREATE.last_name
    assert user.email == USER_CREATE.email
