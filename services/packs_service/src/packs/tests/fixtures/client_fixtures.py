import pytest_asyncio

from packs.dependencies import get_session
from packs.main import app
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture
async def client(test_get_session: AsyncSession) -> AsyncClient:
    app.dependency_overrides[get_session] = lambda: test_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
