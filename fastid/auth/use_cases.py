from auth365.exceptions import Auth365Error

from fastid.auth.exceptions import InvalidTokenError, UserAlreadyExistsError, UserIDNotFoundError
from fastid.auth.models import User
from fastid.auth.repositories import UserEmailSpecification
from fastid.auth.schemas import UserCreate
from fastid.core.base import UseCase
from fastid.database.dependencies import UOWDep
from fastid.database.exceptions import NoResultFoundError
from fastid.database.utils import UUIDv7
from fastid.security.jwt import jwt_backend


class AuthUseCases(UseCase):
    def __init__(self, uow: UOWDep) -> None:
        self.uow = uow

    async def register(self, dto: UserCreate) -> User:
        try:
            await self.uow.users.find(UserEmailSpecification(dto.email))
        except NoResultFoundError:
            pass
        else:
            raise UserAlreadyExistsError
        user = User.from_create(dto)
        user = await self.uow.users.add(user)
        await self.uow.commit()
        return user

    async def get_userinfo(self, token: str) -> User:
        try:
            payload = jwt_backend.validate("access", token)
        except Auth365Error as e:
            raise InvalidTokenError from e
        try:
            return await self.uow.users.get(UUIDv7(payload.sub))
        except NoResultFoundError as e:
            raise UserIDNotFoundError from e
