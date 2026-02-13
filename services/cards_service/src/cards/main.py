from contextlib import asynccontextmanager

from cards.api.router import card_router
from cards.exc.exception_handlers import register_card_exception_handlers
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from cards.grpc.clients.packs import PacksClient

@asynccontextmanager
async def lifespan(app: FastAPI):
    packs_client = PacksClient("packs_service:50051")
    await packs_client.connect()
    app.state.packs_client = packs_client
    yield
    await packs_client.close()

app = FastAPI(lifespan=lifespan)

app.include_router(card_router)

register_card_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
