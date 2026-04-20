from typing import List

from cards.dependencies import get_card_service
from cards.schemas.schemas import (CardFullRead, CardRead, CardsCreate,
                                   CardsDelete, RandomCardRead,
                                   RandomCardsRequest)
from cards.services.service import CardService
from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

card_router = APIRouter(prefix='/cards', tags=['Cards'])


@card_router.post(
    '',
    status_code=status.HTTP_201_CREATED,
    response_model=List[CardFullRead],
)
async def cards_create_api(
        cards: CardsCreate,
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        cards_service: CardService = Depends(get_card_service)
):
    access_token = credentials.credentials
    await cards_service.is_pack_creator(cards.pack_id, access_token)
    return await cards_service.create_cards(cards)


@card_router.get(
    '',
    status_code=status.HTTP_200_OK,
    response_model=List[CardRead],
)
async def cards_get_api(
        pack_id: int,
        cards_service: CardService = Depends(get_card_service)
):
    return await cards_service.get_cards(pack_id)


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
    '',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def cards_delete_api(
        payload: CardsDelete,
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        cards_service: CardService = Depends(get_card_service)
):
    access_token = credentials.credentials
    await cards_service.is_pack_creator(payload.pack_id, access_token)
    await cards_service.delete_cards(payload)
