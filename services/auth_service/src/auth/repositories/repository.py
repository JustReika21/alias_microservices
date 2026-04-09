from datetime import datetime, timezone, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.database.models import User, RefreshToken
from auth.schemas.schemas import UserCreate, UserLogin, RefreshTokenCreate
from auth.services.utils import hash_password
from auth.settings import settings


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, data: UserCreate) -> User:
        password = hash_password(data.password)
        user = User(name=data.name, password=password)
        self.db.add(user)
        return user

    async def save_refresh_token_in_db(self, user_id, token) -> RefreshToken:
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.auth_jwt.refresh_token_expire_minutes
        )
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        self.db.add(refresh_token)
        return refresh_token

    async def get_user_by_name(self, data: UserCreate | UserLogin) -> User | None:
        result = await self.db.execute(
            select(User)
            .where(User.name == data.name)
        )
        user = result.scalar_one_or_none()
        return user

    async def get_user_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(
            select(User)
            .where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        return user

    async def get_refresh_token(self, token: str) -> RefreshToken | None:
        result = await self.db.execute(
            select(RefreshToken)
            .where(RefreshToken.token == token)
        )
        token = result.scalar_one_or_none()
        return token