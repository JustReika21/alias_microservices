from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from packs.api.v1.router import pack_router
from packs.exc.exception_handlers import register_pack_exception_handlers
from packs.grpc.clients.auth import AuthClient
from packs.grpc.clients.cards import CardsClient
from packs.grpc.server import start_grpc_server


@asynccontextmanager
async def lifespan(app: FastAPI):
    auth_client = AuthClient('auth:50051')
    cards_client = CardsClient('cards:50051')

    app.state.auth_client = auth_client
    app.state.cards_client = cards_client

    await auth_client.connect()
    await cards_client.connect()

    grpc_server = await start_grpc_server(auth_client, cards_client)

    yield

    await auth_client.close()
    await cards_client.close()

    await grpc_server.stop(grace=5)


app = FastAPI(lifespan=lifespan)

app.include_router(pack_router, prefix="/api/v1")

register_pack_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
