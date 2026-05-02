# app/dependencies.py

from fastapi import Depends
from game.database.db import async_session
from game.grpc.clients.auth import AuthClient
from game.grpc.clients.cards import CardsClient
from game.grpc.clients.packs import PacksClient
from game.repositories.repository import GameRepository
from game.services.service import GameService
from game.settings import settings
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import HTTPConnection


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


async def start_up_redis() -> Redis:
    redis_client = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        decode_responses=True,
    )
    try:
        await redis_client.ping()
        print("Redis is connected")
    except Exception as e:
        print(f"Redis connection failed: {e}")
    return redis_client


# --- unified dependencies ---

def get_packs_client(conn: HTTPConnection) -> PacksClient:
    return conn.app.state.packs_client


def get_cards_client(conn: HTTPConnection) -> CardsClient:
    return conn.app.state.cards_client


def get_auth_client(conn: HTTPConnection) -> AuthClient:
    return conn.app.state.auth_client


def get_redis_from_app(conn: HTTPConnection) -> Redis:
    return conn.app.state.redis_client


def get_game_repository(
    db: AsyncSession = Depends(get_session),
    redis_client: Redis = Depends(get_redis_from_app),
) -> GameRepository:
    return GameRepository(db, redis_client)


def get_game_service(
    repository: GameRepository = Depends(get_game_repository),
    packs_client: PacksClient = Depends(get_packs_client),
    cards_client: CardsClient = Depends(get_cards_client),
    auth_client: AuthClient = Depends(get_auth_client),
) -> GameService:
    return GameService(repository, packs_client, cards_client, auth_client)