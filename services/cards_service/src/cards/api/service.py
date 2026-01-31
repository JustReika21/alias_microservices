from random import shuffle
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from cards.api.repository import save_card, save_cards, \
    get_random_cards_from_db
from cards.schemas.schemas import CardCreate, CardRead, CardsCreate


async def create_card(card: CardCreate, db: AsyncSession) -> CardRead:
    created_card = await save_card(card, db)

    return CardRead.model_validate(created_card)


async def create_cards(cards: CardsCreate, db: AsyncSession) -> List[CardRead]:
    created_cards = await save_cards(cards, db)
    validated_cards = [CardRead.model_validate(card) for card in created_cards]
    return validated_cards


async def get_random_cards(
        pack_id: int,
        limit: int,
        db: AsyncSession
) -> List[CardRead]:
    cards = await get_random_cards_from_db(pack_id, limit, db)
    validated_cards = [CardRead.model_validate(card) for card in cards]
    shuffle(validated_cards)
    return validated_cards
