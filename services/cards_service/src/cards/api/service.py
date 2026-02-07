from random import shuffle
from typing import List

from cards.api.repository import (get_random_cards_from_db, save_card,
                                  save_cards)
from cards.grpc.clients.packs import PacksClient
from cards.schemas.schemas import CardCreate, CardRead, CardsCreate
from sqlalchemy.ext.asyncio import AsyncSession


async def create_card(card: CardCreate, db: AsyncSession, packs_client: PacksClient) -> CardRead:
    created_card = await save_card(card, db, packs_client)

    return CardRead.model_validate(created_card)


async def create_cards(cards: CardsCreate, db: AsyncSession, packs_client: PacksClient) -> List[CardRead]:
    created_cards = await save_cards(cards, db, packs_client)
    validated_cards = [CardRead.model_validate(card) for card in created_cards]
    return validated_cards


async def get_random_cards(
        pack_id: int,
        limit: int,
        db: AsyncSession,
        packs_client: PacksClient
) -> List[CardRead]:
    cards = await get_random_cards_from_db(pack_id, limit, db, packs_client)
    validated_cards = [CardRead.model_validate(card) for card in cards]
    shuffle(validated_cards)
    return validated_cards
