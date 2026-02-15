from random import shuffle
from typing import List

from cards.repository import (get_random_cards_from_db, save_card,
                              save_cards, delete_card_from_db)
from cards.grpc.clients.packs import PacksClient
from cards.schemas.schemas import CardCreate, CardRead, CardsCreate, \
    RandomCardsRequest, CardDelete
from sqlalchemy.ext.asyncio import AsyncSession


async def create_card(
        card: CardCreate,
        db: AsyncSession,
        packs_client: PacksClient
) -> CardRead:
    created_card = await save_card(card, db, packs_client)

    return CardRead.model_validate(created_card)


async def create_cards(
        cards: CardsCreate,
        db: AsyncSession,
        packs_client: PacksClient
) -> List[CardRead]:
    created_cards = await save_cards(cards, db, packs_client)

    validated_cards = [CardRead.model_validate(card) for card in created_cards]

    return validated_cards


async def get_random_cards(
        payload: RandomCardsRequest,
        db: AsyncSession,
) -> List[CardRead]:
    cards = await get_random_cards_from_db(payload, db)

    validated_cards = [CardRead.model_validate(card) for card in cards]
    shuffle(validated_cards)

    return validated_cards

async def delete_card(
        payload: CardDelete,
        db: AsyncSession,
        packs_client: PacksClient
) -> None:
    await delete_card_from_db(payload, db, packs_client)

