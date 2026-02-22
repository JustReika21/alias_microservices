import pytest_asyncio
from cards.database.db import Base
from cards.settings import settings
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)


@pytest_asyncio.fixture
async def engine() -> AsyncEngine:
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def test_get_session(engine: AsyncEngine) -> AsyncSession:
    session_maker = async_sessionmaker(engine,expire_on_commit=False)

    async with session_maker() as session:
        yield session
