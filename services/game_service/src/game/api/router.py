from typing import Optional
from fastapi import WebSocket

from fastapi import APIRouter
from fastapi.params import Depends
from redis.asyncio import Redis

from game.dependencies import get_game_service, get_redis_client, \
    get_websoket_game_service
from game.schemas.schemas import Game, Player

from game.services.service import GameService

game_router = APIRouter(tags=['Games'])


@game_router.post('/api/v1/game')
async def game_create_api(
        game: Game,
        game_service: GameService = Depends(get_game_service),
):
    return await game_service.create_game(game)

@game_router.post('/api/v1/game/{game_id}/player')
async def join_game_api(
        game_id: str,
        player: Player,
        game_service: GameService = Depends(get_game_service),
):
    return await game_service.join_game(game_id, player)

@game_router.websocket('/ws/game')
async def game_websocket(
        websocket: WebSocket,
        game_service: GameService = Depends(get_websoket_game_service),
):
    await websocket.accept()
    await game_service.join_game('asdfas', player = Player(id=10, name='PLACEHOLDER', score=0))
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(data)
