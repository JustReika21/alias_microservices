from datetime import datetime, timezone
from sqlite3 import IntegrityError

from auth.database.models import User
from auth.exc.exceptions import (InvalidToken, TokenNotFound,
                                 UserCreationError, UserLoginError,
                                 UserNotFound)
from auth.repositories.repository import UserRepository
from auth.schemas.schemas import TokenInfo, UserCreate, UserLogin, UserRead
from auth.services.utils import (REFRESH_TOKEN_TYPE, create_access_token,
                                 decode_jwt, validate_password,
                                 validate_token_type)


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.db = self.user_repository.db

    async def create_user(self, data: UserCreate) -> None:
        user_exists = await self.user_repository.get_user_by_name(data)
        if user_exists:
            raise UserCreationError('User with this name already exists')
        user = await self.user_repository.create_user(data)
        await self.db.commit()
        await self.db.refresh(user)

    async def validate_auth_user(self, data: UserLogin) -> User:
        user = await self.user_repository.get_user_by_name(data)
        if not user:
            raise UserLoginError('Data is incorrect')

        password_is_correct = validate_password(data.password, user.password)
        if not password_is_correct:
            raise UserLoginError('Data is incorrect')
        return user

    async def get_user(self, user_id: int) -> User:
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFound('User not found')
        return user

    async def get_auth_user(self, token: str, token_type: str) -> User:
        try:
            payload = decode_jwt(token)
        except:
            raise InvalidToken('Invalid token')

        validate_token_type(payload, token_type)

        user_id = payload.get('sub')
        if not user_id:
            raise InvalidToken('Invalid token payload')

        user = await self.get_user(int(user_id))
        if not user:
            raise UserNotFound('User not found')

        return user

    async def refresh(self, refresh_token: str) -> TokenInfo:
        if not refresh_token:
            raise TokenNotFound('Token not found')
        user_id = await self.validate_refresh_token(refresh_token)

        user = await self.get_user(user_id)
        access_token = create_access_token(user)

        return TokenInfo(access_token=access_token)

    async def save_refresh_token(self, user_id: int, token: str) -> None:
        try:
            await self.user_repository.cleanup_refresh_tokens(user_id)
            token = await self.user_repository.save_refresh_token_in_db(user_id, token)
            await self.db.commit()
            await self.db.refresh(token)
        except IntegrityError:
            await self.db.rollback()
            raise UserLoginError('User login error')

    async def validate_refresh_token(self, token: str) -> int:
        payload = decode_jwt(token)

        validate_token_type(payload, REFRESH_TOKEN_TYPE)

        stored_token = await self.user_repository.get_refresh_token(token)

        if not stored_token:
            raise InvalidToken('Invalid token')
        elif stored_token.expires_at < datetime.now(timezone.utc):
            raise InvalidToken('Token is expired')

        return int(payload.get('sub'))

    async def validate_refresh_token_for_websocket(self, refresh_token: str) -> UserRead:
        if not refresh_token:
            raise TokenNotFound('Token not found')

        user_id = await self.validate_refresh_token(refresh_token)
        user = await self.get_user(user_id)

        return UserRead.model_validate(user)
