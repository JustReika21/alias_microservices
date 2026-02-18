from cards.database.db import async_session
from sqlalchemy.ext.asyncio import AsyncSession

from cards.grpc.clients.packs import PacksClient
from fastapi import Request

from cards.repositories.repository import CardRepository
from cards.services.service import CardService

from fastapi import Depends


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


def get_packs_client(request: Request) -> PacksClient:
    return request.app.state.packs_client


def get_card_repository(db: AsyncSession = Depends(get_session)) -> CardRepository:
    return CardRepository(db)


def get_card_service(
        repository: CardRepository = Depends(get_card_repository),
        packs_client: PacksClient = Depends(get_packs_client),
) -> CardService:
    return CardService(repository, packs_client)
