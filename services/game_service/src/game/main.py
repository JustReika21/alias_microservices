from contextlib import asynccontextmanager

from fastapi import FastAPI
from game.api.router import game_router
from game.dependencies import get_redis_client
from game.exc.exception_handlers import register_game_exception_handlers
from game.grpc.clients.cards import CardsClient
from game.grpc.clients.packs import PacksClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    packs_client = PacksClient("aliasmicro-packs-1:50051")
    cards_client = CardsClient("aliasmicro-cards-1:50051")
    await packs_client.connect()
    await cards_client.connect()
    app.state.packs_client = packs_client
    app.state.cards_client = cards_client

    app.state.redis_client = await get_redis_client()

    yield

    await packs_client.close()
    await cards_client.close()

    await app.state.redis_client.close()

app = FastAPI(lifespan=lifespan)

app.include_router(game_router)

register_game_exception_handlers(app)
