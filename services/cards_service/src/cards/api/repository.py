from typing import Sequence, Iterable
from random import sample

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from cards.database.models import Card
from cards.exc.exceptions import CardCreationError
from cards.grpc.clients.packs import PacksClient
from cards.schemas.schemas import CardCreate, CardsCreate


def get_packs_client():
    return PacksClient('packs_service:50051')


async def get_max_card_position(pack_id, db):
    stmt = select(func.max(Card.position)).where(Card.pack_id == pack_id)
    result = await db.execute(stmt)
    return result.scalar()


async def save_cards(
        cards: CardsCreate,
        db: AsyncSession
) -> Sequence[Card]:
    packs_client = get_packs_client()

    if not await packs_client.is_pack_exist(cards.pack_id):
        raise CardCreationError("Collection does not exist")

    cards_list = []
    cur_pos = await get_max_card_position(cards.pack_id, db) or 0
    for word in cards.words:
        cur_pos += 1
        if cur_pos > 5000:
            raise CardCreationError("Collection overflow")
        cards_list.append(
            Card(word=word, pack_id=cards.pack_id, position=cur_pos)
        )

    try:
        db.add_all(cards_list)
        await db.commit()

        for card in cards_list:
            await db.refresh(card)

        return cards_list
    except IntegrityError:
        await db.rollback()
        raise CardCreationError("Card error")


async def save_card(
        card: CardCreate,
        db: AsyncSession
) -> Card:
    packs_client = get_packs_client()

    if not await packs_client.is_pack_exist(card.pack_id):
        raise CardCreationError("Collection does not exist")

    max_pos = await get_max_card_position(card.pack_id, db) or 0

    if max_pos >= 5000:
        raise CardCreationError("Collection overflow")

    card = Card(word=card.word, pack_id=card.pack_id, position=max_pos+1)

    try:
        db.add(card)
        await db.commit()
        await db.refresh(card)

        return card
    except IntegrityError:
        await db.rollback()
        raise CardCreationError('Card creation error')


async def get_random_cards_from_db(
        pack_id: int,
        limit: int,
        db: AsyncSession,
) -> Sequence[Card]:
    max_pos = await get_max_card_position(pack_id, db) or 0

    random_ids = sample(range(1, max_pos +1), min(max_pos, limit))

    stmt = (
        select(Card)
        .where(
            Card.pack_id == pack_id,
            Card.position.in_(random_ids)
        )
        .limit(limit)
    )

    result = await db.execute(stmt)

    # if not card:
    #     raise 'No more cards'

    return result.scalars().all()
