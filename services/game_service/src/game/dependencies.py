from fastapi import Request
from fastapi.params import Depends

from game.database.db import async_session
from game.grpc.clients.packs import PacksClient
from sqlalchemy.ext.asyncio import AsyncSession

from game.repositories.repository import GameRepository
from game.services.service import GameService


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

def get_packs_client(request: Request) -> PacksClient:
    return request.app.state.packs_client

def get_game_repository(db: AsyncSession = Depends(get_session)) -> GameRepository:
    return GameRepository(db)

def get_game_service(
        repository: GameRepository = Depends(get_game_repository),
        packs_client: PacksClient = Depends(get_packs_client),
):
    return GameService(repository, packs_client)
