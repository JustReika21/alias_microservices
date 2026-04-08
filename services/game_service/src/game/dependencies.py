from fastapi import Request
from fastapi.params import Depends
from redis.asyncio import Redis
from starlette.websockets import WebSocket

from game.database.db import async_session
from game.grpc.clients.cards import CardsClient
from game.grpc.clients.packs import PacksClient
from sqlalchemy.ext.asyncio import AsyncSession

from game.repositories.repository import GameRepository
from game.services.service import GameService
from game.settings import settings


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

async def get_redis_client() -> Redis:
    redis_client = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        decode_responses=True,
    )
    try:
        await redis_client.ping()
        print(f'''
==================
Redis is connected
==================
''')
    except Exception as e:
        print(f'''
=============================
Redis is not connected {e}
=============================
''')
    return redis_client

def get_packs_client(request: Request) -> PacksClient:
    return request.app.state.packs_client

def get_cards_client(request: Request) -> CardsClient:
    return request.app.state.cards_client

def get_game_repository(
        db: AsyncSession = Depends(get_session),
        redis_client: Redis = Depends(get_redis_client)
) -> GameRepository:
    return GameRepository(db, redis_client)

def get_game_service(
        repository: GameRepository = Depends(get_game_repository),
        packs_client: PacksClient = Depends(get_packs_client),
        cards_client: CardsClient = Depends(get_cards_client),
):
    return GameService(repository, packs_client, cards_client)

def get_websocket_packs_client(websocket: WebSocket) -> PacksClient:
    return websocket.app.state.packs_client

def get_websocket_cards_client(websocket: WebSocket) -> CardsClient:
    return websocket.app.state.cards_client

def get_websocket_game_repository(
        db: AsyncSession = Depends(get_session),
        redis_client: Redis = Depends(get_redis_client)
) -> GameRepository:
    return GameRepository(db, redis_client)

def get_websoket_game_service(
        repository: GameRepository = Depends(get_websocket_game_repository),
        packs_client: PacksClient = Depends(get_websocket_packs_client),
        cards_client: CardsClient = Depends(get_websocket_cards_client),
):
    return GameService(repository, packs_client, cards_client)


