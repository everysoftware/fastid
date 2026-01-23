from fastid.auth.exceptions import InvalidTokenError, UserAlreadyExistsError, UserIDNotFoundError
from fastid.auth.models import User
from fastid.auth.repositories import EmailUserSpecification
from fastid.auth.schemas import UserCreate
from fastid.core.base import UseCase
from fastid.database.dependencies import UOWDep
from fastid.database.exceptions import NoResultFoundError
from fastid.database.utils import UUIDv7
from fastid.security.exceptions import JWTError
from fastid.security.jwt import jwt_backend


class AuthUseCases(UseCase):
    def __init__(self, uow: UOWDep) -> None:
        self.uow = uow

    async def register(self, dto: UserCreate) -> User:
        try:
            await self.uow.users.find(EmailUserSpecification(dto.email))
        except NoResultFoundError:
            pass
        else:
            raise UserAlreadyExistsError
        user = User.from_create(dto)
        user = await self.uow.users.add(user)
        await self.uow.commit()
        return user

    async def get_userinfo(self, token: str, *, token_type: str = "access") -> User:  # noqa: S107
        try:
            payload = jwt_backend.validate(token_type, token)
        except JWTError as e:
            raise InvalidTokenError from e
        try:
            return await self.uow.users.get(UUIDv7(payload.sub))
        except NoResultFoundError as e:
            raise UserIDNotFoundError from e
