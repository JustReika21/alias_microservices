from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.database.models import User
from auth.schemas.schemas import UserCreate, UserLogin
from auth.services.utils import hash_password


async def save_user(
        data: UserCreate,
        db: AsyncSession
) -> None:
    password = hash_password(data.password)
    user = User(name=data.name, password=password)

    db.add(user)
    await db.commit()
    await db.refresh(user)


async def get_user_by_name(
        data: UserCreate | UserLogin,
        db: AsyncSession
) -> User:
    result = await db.execute(select(User).where(User.name == data.name))
    user = result.scalar_one_or_none()
    return user

async def get_user_by_id(
        user_id: int,
        db: AsyncSession
) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    return user