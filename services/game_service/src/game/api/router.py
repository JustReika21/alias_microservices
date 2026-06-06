from aiormq.tools import awaitable
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette import status

from game.dependencies import get_orchestration_service
from game.exc.exceptions import GameNotFoundError
from game.schemas.schemas import GameCreate, Player, GameCreated
from game.services.orchestration import GameOrchestrationService

game_router = APIRouter(tags=['Games'])


@game_router.post(
    '/api/v1/game',
    status_code=status.HTTP_201_CREATED,
    response_model=GameCreated,
)
async def game_create_api(
        game_data: GameCreate,
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        game_service: GameOrchestrationService = Depends(get_orchestration_service),
):
    access_token = credentials.credentials
    user = await game_service.auth_client.get_user(access_token)
    player = Player(id=user.user_id, name=user.name, score=0)
    return await game_service.create_game(game_data, player)


connections: dict[str, dict[int, WebSocket]] = {}

@game_router.websocket('/ws/game/{game_id}')
async def game_websocket(
        game_id: str,
        websocket: WebSocket,
        game_service: GameOrchestrationService = Depends(get_orchestration_service),
):
    game_status = await game_service.get_game_status(game_id)
    if game_status is None:
        raise GameNotFoundError('Game not found')

    await websocket.accept()

    refresh_token = websocket.cookies.get('refresh_token')
    user = await game_service.auth_client.verify_user_websocket(refresh_token)
    player = Player(id=user.user_id, name=user.name, score=0, team_id=1)

    await game_service.join_game(game_id, player, game_status)

    if game_id not in connections:
        connections[game_id] = {}

    connections[game_id][user.user_id] = websocket

    try:
        con = connections[game_id]
        await game_service.broadcast_service.broadcast(
            con, {'type': 'player_joined', 'player': player.model_dump()}
        )

        await game_service.handle_snapshot(
            game_id, user.user_id, game_status, user.user_id, websocket
        )

        while True:
            data = await websocket.receive_json()
            con = connections[game_id]
            game_status = await game_service.get_game_status(game_id)

            if data['type'] == 'set_up' and game_status == 'setting_up':
                if await game_service.sender_is_host(game_id, websocket, con):
                    await game_service.handle_set_up(game_id, con)

            if data['type'] == 'start' and game_status == 'waiting':
                if await game_service.sender_is_current_player(game_id, websocket, con):
                    await game_service.handle_start_round(game_id, con)

            if data['type'] == 'next' and game_status == 'started':
                if await game_service.sender_is_current_player(game_id, websocket, con):
                    await game_service.send_card(game_id, con)

            if data['type'] == 'switch_team' and game_status == 'setting_up':
                new_team_id = int(data['new_team_id'])
                await game_service.handle_switch_team(game_id, user.user_id, new_team_id, con)

            if data['type'] == 'guessed' and game_status == 'calculating':
                card_id = int(data['card'])
                await game_service.handle_card_guess(game_id, card_id, True, con)

            if data['type'] == 'not_guessed' and game_status == 'calculating':
                card_id = int(data['card'])
                await game_service.handle_card_guess(game_id, card_id, False, con)

            if data['type'] == 'calculated' and game_status == 'calculating':
                if await game_service.sender_is_current_player(game_id, websocket, con):
                    await game_service.handle_calculating(game_id, con)

            if data['type'] == 'restart' and game_status == 'finished':
                if await game_service.sender_is_host(game_id, websocket, con):
                    await game_service.restart_game(game_id, con)

            if data['type'] == 'kick':
                for ws in con.values():
                    await ws.send_json({'type': 'kick'})
                pass

    except WebSocketDisconnect:
        connections[game_id].pop(user.user_id)
