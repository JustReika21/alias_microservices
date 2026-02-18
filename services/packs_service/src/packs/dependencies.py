from fastapi import Depends
from packs.database.db import async_session
from packs.repositories.repository import PackRepository
from packs.services.service import PackService
from sqlalchemy.ext.asyncio import AsyncSession


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

def get_pack_service(db: AsyncSession = Depends(get_session)) -> PackService:
    repository = PackRepository(db)
    return PackService(repository)
