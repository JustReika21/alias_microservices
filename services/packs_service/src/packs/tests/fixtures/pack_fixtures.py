from typing import List, Optional

import pytest_asyncio
from packs.database.models import Pack
from sqlalchemy.ext.asyncio import AsyncSession

from packs.repositories.repository import PackRepository
from packs.services.service import PackService


@pytest_asyncio.fixture
async def pack_repository(test_get_session: AsyncSession) -> PackRepository:
    return PackRepository(test_get_session)


@pytest_asyncio.fixture
async def pack_service(pack_repository: PackRepository) -> PackService:
    return PackService(pack_repository)


@pytest_asyncio.fixture
async def create_pack(test_get_session: AsyncSession):
    async def _create(
            name: str, description: Optional[str] = None,
            total: Optional[int] = 0
    ) -> Pack:
        pack = Pack(
            name=name,
            description=description,
            total=total
        )

        test_get_session.add(pack)
        await test_get_session.commit()
        await test_get_session.refresh(pack)

        return pack
    return _create



@pytest_asyncio.fixture
async def create_packs(test_get_session: AsyncSession):
    async def _create(count: int = 1) -> List[Pack]:
        packs = [
            Pack(
                name=f'test_{i}',
            )
            for i in range(count)
        ]

        test_get_session.add_all(packs)
        await test_get_session.commit()

        return packs
    return _create
