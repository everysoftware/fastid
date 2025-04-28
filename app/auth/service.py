from auth365.exceptions import Auth365Error

from app.auth.exceptions import InvalidTokenError, UserAlreadyExistsError, UserIDNotFoundError
from app.auth.models import User
from app.auth.repositories import UserEmailSpecification
from app.auth.schemas import UserCreate
from app.base.datatypes import UUIDv7
from app.base.service import UseCase
from app.db.dependencies import UOWDep
from app.db.exceptions import NoResultFoundError
from app.security.jwt import jwt_backend


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
