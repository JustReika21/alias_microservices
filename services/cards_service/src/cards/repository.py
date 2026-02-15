from random import sample
from typing import Sequence

from cards.database.models import Card
from cards.exc.exceptions import CardCreationError, CardError
from cards.grpc.clients.packs import PacksClient
from cards.schemas.schemas import CardCreate, CardsCreate, RandomCardsRequest, \
    CardDelete
from sqlalchemy import func, select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


async def get_max_card_position(pack_id, db):
    stmt = select(func.max(Card.position)).where(Card.pack_id == pack_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def save_cards(
        cards: CardsCreate,
        db: AsyncSession,
        packs_client: PacksClient
) -> Sequence[Card]:
    if not await packs_client.is_pack_exist(cards.pack_id):
        raise CardCreationError("Collection does not exist")

    total_in_pack = await packs_client.get_total_cards_in_pack(cards.pack_id)
    cards_count = len(cards.words)
    if cards_count + total_in_pack > 5000:
        raise CardCreationError("Collection overflow")

    await packs_client.update_total_cards_in_pack(cards.pack_id, cards_count)

    start_pos = await get_max_card_position(cards.pack_id, db) or 0
    new_cards = [
        Card(
            word=word,
            pack_id=cards.pack_id,
            position=start_pos + i + 1,
        )
        for i, word in enumerate(cards.words)
    ]

    try:
        db.add_all(new_cards)
        await db.commit()
        return new_cards
    except IntegrityError:
        await db.rollback()
        await packs_client.update_total_cards_in_pack(cards.pack_id, -cards_count)
        raise CardCreationError("Card error")


async def save_card(
        card: CardCreate,
        db: AsyncSession,
        packs_client: PacksClient
) -> Card:
    if not await packs_client.is_pack_exist(card.pack_id):
        raise CardCreationError("Collection does not exist")

    if await packs_client.get_total_cards_in_pack(card.pack_id) >= 5000:
        raise CardCreationError("Collection overflow")

    max_pos = await get_max_card_position(card.pack_id, db) or 0
    card = Card(word=card.word, pack_id=card.pack_id, position=max_pos+1)

    try:
        db.add(card)
        await db.commit()
        await db.refresh(card)
        await packs_client.update_total_cards_in_pack(card.pack_id, 1)

        return card
    except IntegrityError:
        await db.rollback()
        await packs_client.update_total_cards_in_pack(card.pack_id, -1)
        raise CardCreationError('Card creation error')


async def get_random_cards_from_db(
        payload: RandomCardsRequest,
        db: AsyncSession,
) -> Sequence[Card]:
    max_pos = await get_max_card_position(payload.pack_id, db) or 0

    if not max_pos:
        raise CardError('No cards in pack')

    attempt = 0
    result = None
    while not result and attempt < 3:
        random_ids = sample(range(1, max_pos +1), min(max_pos, payload.limit))

        stmt = (
            select(Card)
            .where(
                Card.pack_id == payload.pack_id,
                Card.position.in_(random_ids)
            )
            .limit(payload.limit)
        )

        attempt += 1
        result = await db.execute(stmt)
        result = result.scalars().all()

    if not result:
        raise CardError('No cards in pack')

    return result


async def delete_card_from_db(
        payload: CardDelete,
        db: AsyncSession,
        packs_client: PacksClient
) -> None:
    stmt = delete(Card).where(Card.id == payload.card_id).returning(Card.pack_id)
    result = await db.execute(stmt)
    pack_id = result.scalar_one_or_none()

    if pack_id is not None:
        await packs_client.update_total_cards_in_pack(pack_id, -1)
        await db.commit()
