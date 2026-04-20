from auth.database.db import async_session
from auth.repositories.repository import UserRepository
from auth.services.service import UserService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

def get_user_repository(db: AsyncSession = Depends(get_session)) -> UserRepository:
    return UserRepository(db)

def get_user_service(repository: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repository)
