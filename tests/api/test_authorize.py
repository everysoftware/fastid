from auth365.schemas import TokenResponse


async def test_authorize_password_grant(token: TokenResponse) -> None:
    assert token.access_token is not None
