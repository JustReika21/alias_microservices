from typing import List, Iterable, Sequence

from sqlalchemy import select, func, exists, ScalarResult
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from cards.database.models import Card
from cards.exc.exceptions import CardCreationError
from cards.grpc.clients.packs import PacksClient
from cards.schemas.schemas import CardCreate


# async def save_cards()


async def save_card(
        card: CardCreate,
        db: AsyncSession
) -> Card:
    packs_client = PacksClient('packs_service:50051')

    pack_exists = await packs_client.is_pack_exist(
        card.pack_id
    )

    if not pack_exists:
        raise CardCreationError("Collection does not exist")

    card = Card(word=card.word, pack_id=card.pack_id)

    try:
        db.add(card)
        await db.commit()
        await db.refresh(card)

        return card
    except IntegrityError:
        await db.rollback()
        raise CardCreationError('Card creation error')

#
# async def get_random_cards_from_db(
#         collection_id: int,
#         limit: int,
#         db: AsyncSession,
#         played_cards: Iterable[int] = ()
# ) -> Sequence[Card]:
#     card = await db.execute(
#         select(Card)
#         .where(
#             Card.collection_id == collection_id,
#             Card.id.not_in(played_cards)
#         )
#         .limit(limit)
#     )
#     #
#     # if not card:
#     #     raise 'No more cards'
#
#     return card.scalars().all()
