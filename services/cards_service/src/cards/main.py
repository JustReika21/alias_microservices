from contextlib import asynccontextmanager

from cards.api.v1.router import card_router
from cards.exc.exception_handlers import register_card_exception_handlers
from cards.grpc.clients.packs import PacksClient
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    packs_client = PacksClient('aliasmicro-packs-1:50051')
    await packs_client.connect()
    app.state.packs_client = packs_client
    yield
    await packs_client.close()

app = FastAPI(lifespan=lifespan)

app.include_router(card_router, prefix='/api/v1')

register_card_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
