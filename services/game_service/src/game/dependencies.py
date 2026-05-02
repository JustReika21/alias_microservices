from fastapi import Depends
from game.database.db import async_session
from game.grpc.clients.auth import AuthClient
from game.grpc.clients.cards import CardsClient
from game.grpc.clients.packs import PacksClient
from game.repositories.repository import GameRepository
from game.services.broadcast_service import GameBroadcastService
from game.services.core import GameCoreService
from game.services.orchestration_service import GameOrchestrationService
from game.services.round_service import GameRoundService
from game.services.score_service import GameScoreService
from game.services.snapshot_service import GameSnapshotService
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
        print('Redis is connected')
    except Exception as e:
        print(f'Redis connection failed: {e}')
    return redis_client


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


def get_broadcast_service() -> GameBroadcastService:
    return GameBroadcastService()


def get_core_service(
    repo: GameRepository = Depends(get_game_repository),
) -> GameCoreService:
    return GameCoreService(repo)


def get_round_service(
    repo: GameRepository = Depends(get_game_repository),
) -> GameRoundService:
    return GameRoundService(repo)


def get_score_service(
    repo: GameRepository = Depends(get_game_repository),
) -> GameScoreService:
    return GameScoreService(repo)


def get_snapshot_service(
    repo: GameRepository = Depends(get_game_repository),
) -> GameSnapshotService:
    return GameSnapshotService(repo)


def get_orchestration_service(
    repo: GameRepository = Depends(get_game_repository),
    broadcast: GameBroadcastService = Depends(get_broadcast_service),
    core: GameCoreService = Depends(get_core_service),
    round_service: GameRoundService = Depends(get_round_service),
    score_service: GameScoreService = Depends(get_score_service),
    snapshot_service: GameSnapshotService = Depends(get_snapshot_service),
    auth_client: AuthClient = Depends(get_auth_client),
    cards_client: CardsClient = Depends(get_cards_client),
    packs_client: PacksClient = Depends(get_packs_client),
) -> GameOrchestrationService:
    return GameOrchestrationService(
        repo=repo,
        broadcast=broadcast,
        core=core,
        round_service=round_service,
        score_service=score_service,
        snapshot_service=snapshot_service,
        auth_client=auth_client,
        cards_client=cards_client,
        packs_client=packs_client,
    )