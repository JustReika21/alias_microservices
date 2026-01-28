from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from cards.api.service import create_card
from cards.database.dependencies import get_session
from cards.schemas.schemas import CardCreate, CardRead

card_router = APIRouter(tags=['Cards'])


@card_router.post('/card', response_model=CardRead)
async def card_create_api(
        card: CardCreate,
        db: AsyncSession = Depends(get_session)
) -> CardRead:
    return await create_card(card, db)
