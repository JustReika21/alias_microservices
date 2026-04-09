from sqlalchemy.ext.asyncio import AsyncSession

from auth.exc.exceptions import UserLoginError, UserCreationError, UserNotFound
from auth.database.models import User
from auth.repositories.repository import save_user, get_user_by_name, \
    get_user_by_id
from auth.schemas.schemas import UserCreate, UserLogin, UserRead
from auth.services.utils import validate_password


async def create_user(data: UserCreate, db: AsyncSession) -> None:
    user_exists = await get_user_by_name(data, db)
    if user_exists:
        raise UserCreationError('User with this name already exists')
    await save_user(data, db)


async def validate_auth_user(data: UserLogin, db: AsyncSession) -> User:
    user = await get_user_by_name(data, db)
    if not user:
        raise UserLoginError('Data is incorrect')

    password_is_correct = validate_password(data.password, user.password)
    if not password_is_correct:
        raise UserLoginError('Data is incorrect')
    return user

async def get_user(user_id: int, db: AsyncSession) -> UserRead:
    user = await get_user_by_id(user_id, db)
    if not user:
        raise UserNotFound('User not found')
    return UserRead.model_validate(user)

