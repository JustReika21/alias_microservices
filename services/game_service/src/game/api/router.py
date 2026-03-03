from typing import Optional
from fastapi import FastAPI, WebSocket

from fastapi import APIRouter
from fastapi.params import Depends
from game.dependencies import get_game_service

from game.services.service import GameService

game_router = APIRouter(tags=['Games'])


@game_router.post('/api/v1/game')
async def game_create_api(
        password: Optional[str] = None,
        game_service: GameService = Depends(get_game_service),
):
    return await game_service.create_game(password)


@game_router.websocket('/game/{game_id}')
async def game_websocket(
        game_id: str,
        websocket: WebSocket,
        game_service: GameService = Depends(get_game_service)
):

    await websocket.accept()
    while True:
        data = await websocket.receive_json()
