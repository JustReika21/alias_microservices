from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette import status

from game.dependencies import get_game_service
from game.exc.exceptions import GameNotFoundError
from game.schemas.schemas import GameCreate, Player
from game.services.service import GameService

game_router = APIRouter(tags=['Games'])



@game_router.post(
    '/api/v1/game',
    status_code=status.HTTP_201_CREATED,
)
async def game_create_api(
        game_data: GameCreate,
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        game_service: GameService = Depends(get_game_service),
):
    access_token = credentials.credentials
    user = await game_service.auth_client.get_user(access_token)
    player = Player(id=user.user_id, name=user.name, score=0)
    return await game_service.create_game(game_data, player)


@game_router.post('/api/v1/game/{game_id}/player')
async def join_game_api(
        game_id: str,
        player: Player,
        game_service: GameService = Depends(get_game_service),
):
    return await game_service.join_game(game_id, player)


connections: dict[str, dict[int, WebSocket]] = {}

@game_router.websocket('/ws/game/{game_id}')
async def game_websocket(
        game_id: str,
        websocket: WebSocket,
        game_service: GameService = Depends(get_game_service),
):
    exist = await game_service.game_repository.is_game_exist(game_id)
    if not exist:
        raise GameNotFoundError('Game not found')

    game_status = await game_service.game_repository.get_game_status(game_id)

    await websocket.accept()

    refresh_token = websocket.cookies.get('refresh_token')
    user = await game_service.auth_client.verify_user_websocket(refresh_token)
    player = Player(id=user.user_id, name=user.name, score=0, team_id=1)

    await game_service.join_game(game_id, player=player)

    if game_id not in connections:
        connections[game_id] = {}

    connections[game_id][user.user_id] = websocket

    await game_service.load_snapshot(game_id, user.user_id, game_status, websocket)

    players = await game_service.get_players(game_id)
    host = await game_service.get_host(game_id)

    for ws in connections[game_id].values():
        await ws.send_json({'type': 'players', 'players': players})
        await ws.send_json({'type': 'host', 'host': host})

    await websocket.send_json({'type': 'my_id', 'my_id': user.user_id})

    teams = await game_service.get_teams(game_id)
    await websocket.send_json({'type': 'teams', 'teams': teams})

    try:
        while True:
            data = await websocket.receive_json()
            con = connections[game_id]
            game_status = await game_service.get_game_status(game_id)

            if data['type'] == 'set_up' and game_status == 'setting_up':
                await game_service.game_repository.set_game_status(game_id, 'waiting')
                for ws in con.values():
                    await ws.send_json({'type': 'status', 'value': 'waiting'})

            if data['type'] == 'start' and game_status == 'waiting':
                if await game_service.sender_is_current_player(game_id, websocket, con):
                    await game_service.start_game(game_id, con)

            if data['type'] == 'next' and game_status == 'started':
                if await game_service.sender_is_current_player(game_id, websocket, con):
                    await game_service.send_card(game_id, con)

            if data['type'] == 'switch_team' and game_status == 'setting_up':
                new_team_id = int(data['new_team_id'])
                await game_service.switch_team(game_id, user.user_id, new_team_id, con)

            if data['type'] == 'guessed' and game_status == 'calculating':
                card_id = int(data['card'])
                await game_service.card_guessed(game_id, card_id, True, con)

            if data['type'] == 'not_guessed' and game_status == 'calculating':
                card_id = int(data['card'])
                await game_service.card_guessed(game_id, card_id, False, con)

            if data['type'] == 'calculated' and game_status == 'calculating':
                if await game_service.sender_is_current_player(game_id, websocket, con):
                    await game_service.set_scores(game_id, con)

            if data['type'] == 'kick':
                for ws in con.values():
                    await ws.send_json({'type': 'kick'})
                pass

    except WebSocketDisconnect:
        connections[game_id].pop(user.user_id)
