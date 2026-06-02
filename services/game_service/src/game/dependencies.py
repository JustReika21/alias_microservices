from fastapi import Depends
from game.database.db import async_session
from game.settings import settings
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import HTTPConnection

from game.grpc.clients.auth import AuthClient
from game.grpc.clients.cards import CardsClient
from game.grpc.clients.packs import PacksClient

from game.repositories.card import GameCardRepository
from game.repositories.core import GameCoreRepository
from game.repositories.player import GamePlayerRepository
from game.repositories.round import GameRoundRepository
from game.repositories.score import GameScoreRepository
from game.repositories.team import GameTeamRepository
from game.repositories.timer import GameTimerRepository

from game.services.broadcast import GameBroadcastService
from game.services.card import GameCardService
from game.services.core import GameCoreService
from game.services.player import GamePlayerService
from game.services.round import GameRoundService
from game.services.score import GameScoreService
from game.services.snapshot import GameSnapshotService
from game.services.team import GameTeamService
from game.services.timer import GameTimerService
from game.services.orchestration import GameOrchestrationService


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


def get_redis_from_app(conn: HTTPConnection) -> Redis:
    return conn.app.state.redis_client

# =========================
# CLIENTS
# =========================

def get_cards_client(conn: HTTPConnection) -> CardsClient:
    return conn.app.state.cards_client


def get_packs_client(conn: HTTPConnection) -> PacksClient:
    return conn.app.state.packs_client


def get_auth_client(conn: HTTPConnection) -> AuthClient:
    return conn.app.state.auth_client


# =========================
# REPOSITORIES
# =========================

def get_game_card_repository(
    db: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis_from_app),
) -> GameCardRepository:
    return GameCardRepository(db, redis)


def get_game_core_repository(
    db: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis_from_app),
) -> GameCoreRepository:
    return GameCoreRepository(db, redis)


def get_game_player_repository(
    db: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis_from_app),
) -> GamePlayerRepository:
    return GamePlayerRepository(db, redis)


def get_game_round_repository(
    db: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis_from_app),
) -> GameRoundRepository:
    return GameRoundRepository(db, redis)


def get_game_score_repository(
    db: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis_from_app),
) -> GameScoreRepository:
    return GameScoreRepository(db, redis)


def get_game_team_repository(
    db: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis_from_app),
) -> GameTeamRepository:
    return GameTeamRepository(db, redis)


def get_game_timer_repository(
    db: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis_from_app),
) -> GameTimerRepository:
    return GameTimerRepository(db, redis)


# =========================
# SERVICES
# =========================

def get_broadcast_service() -> GameBroadcastService:
    return GameBroadcastService()


def get_game_card_service(
    repo: GameCardRepository = Depends(get_game_card_repository),
    cards_client: CardsClient = Depends(get_cards_client),
) -> GameCardService:
    return GameCardService(repo, cards_client)


def get_game_core_service(
    repo: GameCoreRepository = Depends(get_game_core_repository),
) -> GameCoreService:
    return GameCoreService(repo)


def get_game_player_service(
    repo: GamePlayerRepository = Depends(get_game_player_repository),
) -> GamePlayerService:
    return GamePlayerService(repo)


def get_game_round_service(
    repo: GameRoundRepository = Depends(get_game_round_repository),
) -> GameRoundService:
    return GameRoundService(repo)


def get_game_score_service(
    repo: GameScoreRepository = Depends(get_game_score_repository),
) -> GameScoreService:
    return GameScoreService(repo)


def get_game_team_service(
    repo: GameTeamRepository = Depends(get_game_team_repository),
) -> GameTeamService:
    return GameTeamService(repo)


def get_game_timer_service(
    repo: GameTimerRepository = Depends(get_game_timer_repository),
) -> GameTimerService:
    return GameTimerService(repo)


def get_game_snapshot_service() -> GameSnapshotService:
    return GameSnapshotService()


# =========================
# ORCHESTRATION
# =========================

def get_orchestration_service(
    broadcast: GameBroadcastService = Depends(get_broadcast_service),
    card: GameCardService = Depends(get_game_card_service),
    core: GameCoreService = Depends(get_game_core_service),
    player: GamePlayerService = Depends(get_game_player_service),
    round_svc: GameRoundService = Depends(get_game_round_service),
    score: GameScoreService = Depends(get_game_score_service),
    team: GameTeamService = Depends(get_game_team_service),
    timer: GameTimerService = Depends(get_game_timer_service),
    snapshot: GameSnapshotService = Depends(get_game_snapshot_service),
    auth: AuthClient = Depends(get_auth_client),
    packs: PacksClient = Depends(get_packs_client),
) -> GameOrchestrationService:
    return GameOrchestrationService(
        broadcast_service=broadcast,
        card_service=card,
        core_service=core,
        player_service=player,
        round_service=round_svc,
        score_service=score,
        team_service=team,
        timer_service=timer,
        snapshot_service=snapshot,
        auth_client=auth,
        packs_client=packs,
    )
