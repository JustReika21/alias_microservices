from collections import defaultdict
from starlette.websockets import WebSocket


class ConnectionManager:
    def __init__(self):
        self.connections: dict[str, dict[int, WebSocket]] = defaultdict(dict)

    async def connect(self, game_id: str, user_id: int, ws: WebSocket):
        self.connections[game_id][user_id] = ws

    def disconnect(self, game_id: str, user_id: int):
        if user_id in self.connections[game_id]:
            del self.connections[game_id][user_id]

        if not self.connections[game_id]:
            del self.connections[game_id]

    async def broadcast(self, game_id: str, payload: dict):
        con = self.connections.get(game_id, {})
        if payload.get('type') == 'card':
            await self._handle_card_msg(con, payload)
        elif payload.get('type') == 'current_player':
            await self._handle_current_player_msg(con, payload)
        elif payload.get('type') == 'player_kicked':
            await self._handle_kick_player(game_id, con, payload)
        else:
            for ws in con.values():
                await ws.send_json(payload)

    async def send_to(self, game_id: str, user_id: int, payload: dict):
        con = self.connections.get(game_id)
        if not con:
            return

        ws = con.get(user_id)
        if ws:
            await ws.send_json(payload)

    async def _handle_card_msg(self, con: dict, payload: dict):
        for user_id, ws in con.items():
            card = (
                payload['current_card']
                if user_id == payload['current_player_id']
                else payload['previous_card']
            )
            await ws.send_json({
                'type': 'card',
                'card': card,
                'guessed': True
            })

    async def _handle_current_player_msg(self, con: dict, payload: dict):
        for user_id, ws in con.items():
            payload['is_current'] = int(user_id) == int(payload['player_id'])
            await ws.send_json(payload)

    async def _handle_kick_player(self, game_id: str, con: dict, payload: dict):
        for user_id, ws in con.items():
            if user_id == payload.get('kicked_user_id'):
                await ws.send_json(
                    {'type': 'you_have_been_kicked', 'user_id': user_id}
                )
                self.disconnect(game_id, user_id)
            else:
                await ws.send_json(payload)
