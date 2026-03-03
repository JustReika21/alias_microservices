from contextlib import asynccontextmanager

from fastapi import FastAPI
from game.api.router import game_router
from game.exc.exception_handlers import register_game_exception_handlers
from game.grpc.clients.packs import PacksClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    packs_client = PacksClient("packs_service:50051")
    await packs_client.connect()
    app.state.packs_client = packs_client
    yield
    await packs_client.close()

app = FastAPI(lifespan=lifespan)

app.include_router(game_router)

register_game_exception_handlers(app)
