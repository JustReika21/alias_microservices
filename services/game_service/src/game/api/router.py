from fastapi import WebSocket

from fastapi import APIRouter
from fastapi.params import Depends
from starlette.websockets import WebSocketDisconnect

from game.dependencies import get_game_service, get_websoket_game_service
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


connections: dict[str, list[WebSocket]] = {}

@game_router.websocket('/ws/game/{game_id}')
async def game_websocket(
        game_id: str,
        websocket: WebSocket,
        game_service: GameService = Depends(get_websoket_game_service),
):
    await websocket.accept()
    await game_service.join_game(game_id, player=Player(id=1, name='PLACEHOLDER', score=0))

    if game_id not in connections:
        connections[game_id] = []

    connections[game_id].append(websocket)
    try:
        while True:
            data = await websocket.receive_text()

            if data == 'next_turn':
                p_id = await game_service.game_repository.next_turn(game_id)
                for ws in connections.get(game_id, []):
                    await ws.send_text(p_id)

            if data == 'get_words':
                cards = await game_service.cards_client.get_random_cards(1, 100)
                await websocket.send_text(cards)

    except WebSocketDisconnect:
        connections[game_id].remove(websocket)
