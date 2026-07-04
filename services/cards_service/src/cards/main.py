from contextlib import asynccontextmanager

from cards.api.v1.router import card_router
from cards.exc.exception_handlers import register_card_exception_handlers
from cards.grpc.clients.packs import PacksClient
from cards.grpc.server import start_grpc_server
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    packs_client = PacksClient('packs:50051')
    await packs_client.connect()
    app.state.packs_client = packs_client

    grpc_server = await start_grpc_server(packs_client)

    yield

    await packs_client.close()

    await grpc_server.stop(grace=5)

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
