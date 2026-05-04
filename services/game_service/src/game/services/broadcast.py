from starlette.websockets import WebSocket


class GameBroadcastService:
    async def broadcast(self, con: dict[int, WebSocket], payload: dict) -> None:
        for ws in con.values():
            await ws.send_json(payload)

    async def send_to(self, ws: WebSocket, payload: dict) -> None:
        await ws.send_json(payload)
