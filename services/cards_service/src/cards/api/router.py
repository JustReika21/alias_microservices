from typing import List

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from cards.api.service import create_card, create_cards, get_random_cards
from cards.database.dependencies import get_session
from cards.schemas.schemas import CardCreate, CardRead, CardsCreate

card_router = APIRouter(tags=['Cards'])


@card_router.post('/card')
async def card_create_api(
        card: CardCreate,
        db: AsyncSession = Depends(get_session)
) -> CardRead:
    return await create_card(card, db)

@card_router.post('/cards')
async def cards_create_api(
        cards: CardsCreate,
        db: AsyncSession = Depends(get_session)
) -> List[CardRead]:
    return await create_cards(cards, db)

@card_router.post('/cards/random')
async def random_cards_get_api(
        pack_id: int,
        limit: int = 100,
        db: AsyncSession = Depends(get_session)
) -> List[CardRead]:
    return await get_random_cards(pack_id, limit, db)

