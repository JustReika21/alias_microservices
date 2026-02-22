import pytest
from cards.tests.fixtures.fakes import FakePacksClient, get_fake_packs_client
from httpx import AsyncClient

PACK_ID = 1


class TestCards:
    URL = 'api/v1/cards'

    @pytest.mark.asyncio
    @pytest.mark.parametrize('words, total', [
        (['test', 'test2', 'test3'], 3),
        (['a' * 127, 'aaa'], 2),
        (['test'], 1),
    ])
    async def test_00_valid_create_cards(
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
        (['a' * 128], 422),
        (['test', 'test'], 400),
    ])
    async def test_01_invalid_create_cards(
            self, client: AsyncClient, get_fake_packs_client: FakePacksClient,
            words, status
    ):
        response = await client.post(
            self.URL,
            json={'words': words, 'pack_id': PACK_ID},
        )

        assert response.status_code == status

    @pytest.mark.asyncio
    async def test_02_valid_get_random_cards(
            self, client: AsyncClient, get_fake_packs_client: FakePacksClient,
            create_cards
    ):
        await create_cards(PACK_ID, 5)

        response = await client.post(
            self.URL + '/random',
            json={'pack_id': PACK_ID, 'limit': 100},
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_03_get_random_cards_from_empty_pack(
            self, client: AsyncClient, get_fake_packs_client: FakePacksClient,
    ):
        response = await client.post(
            self.URL + '/random',
            json={'pack_id': PACK_ID, 'limit': 100},
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_04_valid_delete_card(
            self, client: AsyncClient, get_fake_packs_client: FakePacksClient,
            create_cards
    ):
        cards = await create_cards(PACK_ID, 2)

        response = await client.delete(self.URL + f'/{cards[0].id}')

        assert response.status_code == 204

        total_cards_in_pack = await get_fake_packs_client.get_total_cards_in_pack(PACK_ID)

        assert total_cards_in_pack == 1

    @pytest.mark.asyncio
    async def test_05_delete_card_not_exists(
            self, client: AsyncClient, get_fake_packs_client: FakePacksClient,
            create_cards
    ):
        await create_cards(PACK_ID, 1)

        response = await client.delete(self.URL + '/9999')

        assert response.status_code == 204

        total_cards_in_pack = await get_fake_packs_client.get_total_cards_in_pack(PACK_ID)

        assert total_cards_in_pack == 1
