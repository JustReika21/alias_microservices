from typing import Dict

from starlette.websockets import WebSocket


class GameConnectionManager:
    def __init__(self) -> None:
        self.connections: Dict[str, Dict[int, WebSocket]] = {}

    async def connect(self, game_id: str, user_id: int, websocket: WebSocket) -> None:
        if game_id not in self.connections:
            self.connections[game_id] = {}

        self.connections[game_id][user_id] = websocket

    def disconnect(self, game_id: str, user_id: int) -> None:
        if game_id in self.connections:
            self.connections[game_id].pop(user_id, None)
