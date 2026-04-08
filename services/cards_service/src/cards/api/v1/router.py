from typing import List

from cards.dependencies import get_card_service
from cards.schemas.schemas import CardRead, CardsCreate, RandomCardsRequest, \
    RandomCardRead
from cards.services.service import CardService
from fastapi import APIRouter, status
from fastapi.params import Depends

card_router = APIRouter(prefix='/cards', tags=['Cards'])


@card_router.post(
    '',
    status_code=status.HTTP_201_CREATED,
    response_model=List[CardRead],
)
async def cards_create_api(
        cards: CardsCreate,
        cards_service: CardService = Depends(get_card_service)
):
    return await cards_service.create_cards(cards)

@card_router.post(
    '/random',
    status_code=status.HTTP_200_OK,
    response_model=List[RandomCardRead],
)
async def random_cards_get_api(
        payload: RandomCardsRequest,
        cards_service: CardService = Depends(get_card_service)
):
    return await cards_service.get_random_cards(payload)

@card_router.delete(
    '/{card_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def card_delete_api(
        card_id: int,
        cards_service: CardService = Depends(get_card_service)
) -> None:
    await cards_service.delete_card(card_id)
