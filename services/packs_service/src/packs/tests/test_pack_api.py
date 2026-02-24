import pytest
from httpx import AsyncClient

from packs.schemas.validators import DESCRIPTION_MAX_LENGTH, NAME_MAX_LENGTH


class TestPacksAPI:
    URL = 'api/v1/packs'

    @pytest.mark.asyncio
    @pytest.mark.parametrize('name, description', [
        ('Test', ''),
        ('Test', 'Test'),
        ('Test', None),
        ('A' * NAME_MAX_LENGTH, 'Test'),
        ('Test', 'A' * DESCRIPTION_MAX_LENGTH),
    ])
    async def test_create_pack_returns_201_when_valid(
            self, client: AsyncClient, name, description
    ):
        response = await client.post(
            self.URL,
            json={'name': name, 'description': description},
        )

        assert response.status_code == 201

    @pytest.mark.asyncio
    @pytest.mark.parametrize('name, description', [
        ('T', ''),
        ('A' * (NAME_MAX_LENGTH + 1), 'Test'),
        ('Test', 'A' * (DESCRIPTION_MAX_LENGTH + 1)),
    ])
    async def test_create_pack_returns_422_invalid(
            self, client: AsyncClient, name, description
    ):
        response = await client.post(
            self.URL,
            json={'name': name, 'description': description},
        )

        assert response.status_code == 422
