from typing import List, Sequence

from cards.database.models import Card
from cards.schemas.schemas import RandomCardsRequest, CardsDelete
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession


class CardRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_max_card_position(self, pack_id: int) -> int:
        stmt = select(func.max(Card.position)).where(Card.pack_id == pack_id)
        position = await self.db.scalar(stmt)
        return position or 0

    async def create(
            self,
            cards: List[Card],
    ) -> None:
        self.db.add_all(cards)

    async def get(self, pack_id: int) -> Sequence[Card]:
        stmt = (
            select(Card)
            .where(Card.pack_id == pack_id)
        )
        cards = await self.db.execute(stmt)
        return cards.scalars().all()


    async def get_random_cards(
            self,
            payload: RandomCardsRequest,
            random_ids: List[int]
    ) -> Sequence[Card]:
        stmt = (
            select(Card)
            .where(
                Card.pack_id == payload.pack_id,
                Card.position.in_(random_ids)
            )
            .limit(payload.limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def delete_cards(self, payload: CardsDelete) -> Sequence[int]:
        stmt = (
            delete(Card)
            .where(
                Card.pack_id == payload.pack_id,
                Card.id.in_(payload.card_ids)
            )
            .returning(Card.id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def delete_all_cards_in_pack(self, pack_id: int) -> None:
        stmt = (
            delete(Card)
            .where(Card.pack_id == pack_id)
        )
        await self.db.execute(stmt)
