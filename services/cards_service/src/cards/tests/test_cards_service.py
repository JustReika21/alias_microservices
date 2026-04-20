import pytest
from cards.exc.exceptions import CardCreationError, CardError
from cards.schemas.schemas import CardFullRead, CardsCreate, RandomCardsRequest
from cards.services.service import CardService
from cards.tests.fixtures.fakes import MAX_CARDS_IN_PACK, FakePacksClient
from cards.tests.test_cards_api import PACK_ID


class TestCardsService:
    @pytest.mark.asyncio
    async def test_get_random_cards_returns_limited_result(
            self, cards_service: CardService, create_cards
    ):
        await create_cards(PACK_ID, 101)

        payload = RandomCardsRequest(pack_id=1, limit=100)
        result = await cards_service.get_random_cards(payload=payload)

        assert len(result) == 100

    @pytest.mark.asyncio
    @pytest.mark.parametrize('limit', [
        -1, 0, MAX_CARDS_IN_PACK + 1
    ])
    async def test_get_random_cards_schema_with_wrong_limits(
            self, cards_service: CardService, create_cards, limit
    ):
        with pytest.raises(ValueError):
            RandomCardsRequest(pack_id=1, limit=limit)


    @pytest.mark.asyncio
    async def test_get_random_cards_raise_when_no_cards_in_pack(
            self, cards_service: CardService, create_cards
    ):
        payload = RandomCardsRequest(pack_id=1, limit=100)
        with pytest.raises(CardError):
            await cards_service.get_random_cards(payload=payload)

    @pytest.mark.asyncio
    async def test_get_random_cards(
            self, cards_service: CardService, create_cards
    ):
        await create_cards(PACK_ID, 200)

        payload = RandomCardsRequest(pack_id=1, limit=100)
        result_1 = await cards_service.get_random_cards(payload=payload)
        result_2 = await cards_service.get_random_cards(payload=payload)

        assert result_1 != result_2

    @pytest.mark.asyncio
    async def test_get_random_cards_limit_more_than_total_cards(
            self, cards_service: CardService, create_cards
    ):
        await create_cards(PACK_ID, 5)

        payload = RandomCardsRequest(pack_id=1, limit=100)
        result = await cards_service.get_random_cards(payload=payload)

        assert len(result) == 5

    @pytest.mark.asyncio
    async def test_create_cards_valid(
            self, cards_service: CardService
    ):
        cards = CardsCreate(words=['test1', 'test2', 'test3'], pack_id=1)
        result = await cards_service.create_cards(cards=cards)
        validated = [CardFullRead.model_validate(card) for card in result]

        current = [[card.word, card.position, card.pack_id] for card in validated]
        expected = [['test1', 1, 1], ['test2', 2, 1], ['test3', 3, 1]]

        assert current == expected

    @pytest.mark.asyncio
    @pytest.mark.parametrize('words', [
        (['test', 'test']),
        ([f'test_{i}' for i in range(MAX_CARDS_IN_PACK + 1)])
    ])
    async def test_create_cards_invalid(
            self, cards_service: CardService,
            get_fake_packs_client: FakePacksClient, words
    ):
        cards = CardsCreate(words=words, pack_id=1)
        with pytest.raises(CardCreationError):
            await cards_service.create_cards(cards=cards)

        total = await get_fake_packs_client.get_total_cards_in_pack(PACK_ID)

        assert total == 0

    @pytest.mark.asyncio
    async def test_create_cards_raise_when_total_cards_out_of_bounds(
            self, get_fake_packs_client: FakePacksClient,
            cards_service: CardService, create_cards,
    ):
        await create_cards(PACK_ID, MAX_CARDS_IN_PACK)

        cards = CardsCreate(words=['test1'], pack_id=1)
        with pytest.raises(CardCreationError):
            await cards_service.create_cards(cards=cards)


    @pytest.mark.asyncio
    async def test_delete_card_returns_204_when_valid(
            self, cards_service: CardService,
            get_fake_packs_client: FakePacksClient, create_cards
    ):
        card = await create_cards(PACK_ID, 1)

        await cards_service.delete_card(card[0].id)

        total = await get_fake_packs_client.get_total_cards_in_pack(PACK_ID)

        assert total == 0
