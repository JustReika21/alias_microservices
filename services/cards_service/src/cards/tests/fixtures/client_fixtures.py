import pytest_asyncio
from cards.dependencies import get_packs_client, get_session
from cards.main import app
from cards.tests.fixtures.fakes import FakePacksClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture
async def client(
        get_fake_packs_client: FakePacksClient, test_get_session: AsyncSession
) -> AsyncClient:
    app.dependency_overrides[get_session] = lambda: test_get_session
    app.dependency_overrides[get_packs_client] = lambda: get_fake_packs_client

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
