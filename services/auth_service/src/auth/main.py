from contextlib import asynccontextmanager

from auth.api.v1.router import auth_router
from auth.exc.exception_handlers import register_auth_exception_handlers
from auth.grpc.server import start_grpc_server
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    grpc_server = await start_grpc_server()
    yield
    await grpc_server.stop(grace=5)


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router, prefix='/api/v1/auth')

register_auth_exception_handlers(app)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://82.146.60.75'
    ],
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'DELETE'],
    allow_headers=['Authorization', 'Content-Type'],
)
