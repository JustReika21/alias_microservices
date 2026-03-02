import pytest

from cards.repositories.repository import CardRepository
from cards.tests.test_cards_api import PACK_ID


class TestCardsRepository:
    @pytest.mark.asyncio
    @pytest.mark.parametrize('count_cards', [
        0, 5, 100, 5000
    ])
    async def test_get_max_card_position(
            self, cards_repository: CardRepository, create_cards, count_cards
    ):
        await create_cards(PACK_ID, count_cards)
        position = await cards_repository.get_max_card_position(PACK_ID)

        assert position == count_cards

    @pytest.mark.asyncio
    async def test_card_delete_returns_pack_id_when_card_deleted(
            self, cards_repository: CardRepository, create_cards
    ):
        card = await create_cards(PACK_ID, 1)

        pack_id = await cards_repository.delete(card[0].id)

        assert pack_id == PACK_ID

    @pytest.mark.asyncio
    async def test_card_delete_returns_none_when_card_not_exist(
            self, cards_repository: CardRepository
    ):
        pack_id = await cards_repository.delete(9999)

        assert pack_id is None
