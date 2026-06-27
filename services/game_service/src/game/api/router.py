from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from game.services.connection_manager import ConnectionManager
from starlette import status

from game.dependencies import get_orchestration_service, get_connection_manager
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


@game_router.websocket('/ws/game/{game_id}')
async def game_websocket(
        game_id: str,
        websocket: WebSocket,
        game_service: GameOrchestrationService = Depends(get_orchestration_service),
        manager: ConnectionManager = Depends(get_connection_manager)
):
    game_status = await game_service.get_game_status(game_id)
    if game_status is None:
        raise GameNotFoundError('Game not found')

    await websocket.accept()

    refresh_token = websocket.cookies.get('refresh_token')
    user = await game_service.auth_client.verify_user_websocket(refresh_token)

    player = await game_service.join_game(game_id, user, game_status)

    try:
        await manager.connect(game_id, user.user_id, websocket)

        await game_service.event_publisher.publish(
            game_id, {'type': 'player_joined', 'player': player.model_dump()}
        )

        await game_service.handle_snapshot(
            game_id, user.user_id, game_status, user.user_id
        )

        while True:
            data = await websocket.receive_json()
            cmd = data.get('type')
            game_status = await game_service.get_game_status(game_id)

            if cmd == 'set_up' and game_status == 'setting_up':
                if await game_service.sender_is_host(game_id, user.user_id):
                    await game_service.handle_set_up(game_id)

            if cmd == 'start' and game_status == 'waiting':
                if await game_service.sender_is_current_player(game_id, user.user_id):
                    await game_service.handle_start_round(game_id)

            if cmd == 'next' and game_status == 'started':
                if await game_service.sender_is_current_player(game_id, user.user_id):
                    await game_service.send_card(game_id)

            if cmd == 'switch_team' and game_status == 'setting_up':
                new_team_id = int(data.get('new_team_id'))
                await game_service.handle_switch_team(game_id, user.user_id, new_team_id)

            if cmd == 'guessed' and game_status == 'calculating':
                card_id = int(data.get('card'))
                await game_service.handle_card_guess(game_id, card_id, True)

            if cmd == 'not_guessed' and game_status == 'calculating':
                card_id = int(data.get('card'))
                await game_service.handle_card_guess(game_id, card_id, False)

            if cmd == 'calculated' and game_status == 'calculating':
                if await game_service.sender_is_current_player(game_id, user.user_id):
                    await game_service.handle_calculating(game_id)

            if cmd == 'restart' and game_status == 'finished':
                if await game_service.sender_is_host(game_id, user.user_id):
                    await game_service.restart_game(game_id)

            if cmd == 'kick':
                if await game_service.sender_is_host(game_id, user.user_id):
                    await game_service.kick_player(game_id, data.get('id'))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f'Unexpected WS error: {e}')
    finally:
        manager.disconnect(game_id, user.user_id)
        await game_service.disconnect_user(game_id, user.user_id)
