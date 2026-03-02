import pytest

from cards.constants.packs_constants import MAX_CARDS_IN_PACK
from cards.schemas.validators import WORD_MAX_LENGTH
from cards.tests.fixtures.fakes import FakePacksClient, get_fake_packs_client, PACK_ID
from httpx import AsyncClient




class TestCardsAPI:
    URL = 'api/v1/cards'

    @pytest.mark.asyncio
    @pytest.mark.parametrize('words, total', [
        (['test', 'test2', 'test3'], 3),
        (['a' * WORD_MAX_LENGTH, 'aaa'], 2),
        (['test'], 1),
    ])
    async def test_create_cards_returns_201_when_valid(
            self, client: AsyncClient, get_fake_packs_client: FakePacksClient,
            words, total
    ):
        response = await client.post(
            self.URL,
            json={'words': words, 'pack_id': PACK_ID},
        )

        assert response.status_code == 201

        total_result = await get_fake_packs_client.get_total_cards_in_pack(PACK_ID)
        assert total_result == total

    @pytest.mark.asyncio
    @pytest.mark.parametrize('words, status', [
        (['a' * (WORD_MAX_LENGTH + 1)], 422),
        (['test', 'test'], 400),
        ([f'test_{i}' for i in range(MAX_CARDS_IN_PACK + 1)], 400)
    ])
    async def test_create_cards_invalid(
            self, client: AsyncClient, get_fake_packs_client: FakePacksClient,
            words, status
    ):
        response = await client.post(
            self.URL,
            json={'words': words, 'pack_id': PACK_ID},
        )

        assert response.status_code == status

    @pytest.mark.asyncio
    async def test_get_random_cards_returns_200_when_valid(
            self, client: AsyncClient, get_fake_packs_client: FakePacksClient,
            create_cards
    ):
        await create_cards(PACK_ID, 5)

        response = await client.post(
            self.URL + '/random',
            json={'pack_id': PACK_ID, 'limit': 100},
        )

        assert response.status_code == 200
        assert len(response.json()) == 5

    @pytest.mark.asyncio
    async def test_get_random_cards_returns_400_when_pack_is_empty(
            self, client: AsyncClient, get_fake_packs_client: FakePacksClient,
    ):
        response = await client.post(
            self.URL + '/random',
            json={'pack_id': PACK_ID, 'limit': 100},
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    @pytest.mark.parametrize('limit', [
        -1, 0, MAX_CARDS_IN_PACK + 1
    ])
    async def test_get_random_cards_returns_422_when_limits_are_wrong(
            self, client: AsyncClient, get_fake_packs_client: FakePacksClient,
            limit
    ):
        response = await client.post(
            self.URL + '/random',
            json={'pack_id': PACK_ID, 'limit': limit},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_delete_card_returns_204_when_valid(
            self, client: AsyncClient, get_fake_packs_client: FakePacksClient,
            create_cards
    ):
        cards = await create_cards(PACK_ID, 2)

        response = await client.delete(self.URL + f'/{cards[0].id}')

        assert response.status_code == 204

        total_cards_in_pack = await get_fake_packs_client.get_total_cards_in_pack(PACK_ID)

        assert total_cards_in_pack == 1

    @pytest.mark.asyncio
    async def test_delete_card_returns_204_when_card_does_not_exist(
            self, client: AsyncClient, get_fake_packs_client: FakePacksClient,
            create_cards
    ):
        await create_cards(PACK_ID, 1)

        response = await client.delete(self.URL + '/9999')

        assert response.status_code == 404

        total = await get_fake_packs_client.get_total_cards_in_pack(PACK_ID)

        assert total == 1
