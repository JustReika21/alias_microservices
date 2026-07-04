import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from game.api.router import game_router
from game.dependencies import start_up_redis
from game.exc.exception_handlers import register_game_exception_handlers
from game.grpc.clients.auth import AuthClient
from game.grpc.clients.cards import CardsClient
from game.grpc.clients.packs import PacksClient
from game.redis_listener import redis_listener, ws_worker
from game.services.connection_manager import ConnectionManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    packs_client = PacksClient('packs:50051')
    cards_client = CardsClient('cards:50051')
    auth_client = AuthClient('auth:50051')

    await packs_client.connect()
    await cards_client.connect()
    await auth_client.connect()

    app.state.packs_client = packs_client
    app.state.cards_client = cards_client
    app.state.auth_client = auth_client

    app.state.redis_client = await start_up_redis()

    app.state.connection_manager = ConnectionManager()

    app.state.ws_queue = asyncio.Queue(maxsize=10000)

    app.state.redis_listener_task = asyncio.create_task(
        redis_listener(app.state.redis_client, app.state.ws_queue)
    )

    app.state.ws_workers = [
        asyncio.create_task(
            ws_worker(app.state.ws_queue, app.state.connection_manager))
        for _ in range(2)
    ]

    yield

    await packs_client.close()
    await cards_client.close()
    await auth_client.close()

    await app.state.start_up_redis.close()

    app.state.redis_listener_task.cancel()

    for worker in app.state.ws_workers:
        worker.cancel()

app = FastAPI(lifespan=lifespan)

app.include_router(game_router)

register_game_exception_handlers(app)
