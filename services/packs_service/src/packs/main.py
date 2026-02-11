from contextlib import asynccontextmanager

from fastapi import FastAPI
from packs.api.router import pack_router
from packs.exc.exception_handlers import register_pack_exception_handlers
from packs.grpc.server import start_grpc_server


@asynccontextmanager
async def lifespan(app: FastAPI):
    grpc_server = await start_grpc_server()
    yield
    await grpc_server.stop(grace=5)


app = FastAPI(lifespan=lifespan)

app.include_router(pack_router)

register_pack_exception_handlers(app)
