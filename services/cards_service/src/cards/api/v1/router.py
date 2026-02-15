from typing import List

from cards.service import create_card, create_cards, get_random_cards, \
    delete_card
from cards.dependencies import get_session, get_packs_client
from cards.grpc.clients.packs import PacksClient
from cards.schemas.schemas import CardCreate, CardRead, CardsCreate, \
    RandomCardsRequest, CardsDelete
from fastapi import APIRouter, status
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

card_router = APIRouter(tags=['Cards'])


@card_router.post(
    '/card',
    status_code=status.HTTP_201_CREATED,
)
async def card_create_api(
        card: CardCreate,
        db: AsyncSession = Depends(get_session),
        packs_client: PacksClient = Depends(get_packs_client),
) -> CardRead:
    return await create_card(card, db, packs_client)

@card_router.post(
    '/cards',
    status_code=status.HTTP_201_CREATED,
)
async def cards_create_api(
        cards: CardsCreate,
        db: AsyncSession = Depends(get_session),
        packs_client: PacksClient = Depends(get_packs_client),
) -> List[CardRead]:
    return await create_cards(cards, db, packs_client)

@card_router.post(
    '/cards/random',
    status_code=status.HTTP_200_OK,
)
async def random_cards_get_api(
        payload: RandomCardsRequest,
        db: AsyncSession = Depends(get_session),
) -> List[CardRead]:
    return await get_random_cards(payload, db)

@card_router.delete(
    '/cards/{card_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def card_delete_api(
        payload: CardsDelete,
        db: AsyncSession = Depends(get_session),
        packs_client: PacksClient = Depends(get_packs_client),
) -> None:
    await delete_card(payload, db, packs_client)
