from fastapi import Depends, Request
from packs.database.db import async_session
from packs.grpc.clients.auth import AuthClient
from packs.grpc.clients.cards import CardsClient
from packs.repositories.repository import PackRepository
from packs.services.service import PackService
from sqlalchemy.ext.asyncio import AsyncSession


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

def get_auth_client(request: Request) -> AuthClient:
    return request.app.state.auth_client

def get_cards_client(request: Request) -> CardsClient:
    return request.app.state.cards_client

def get_pack_service(
        db: AsyncSession = Depends(get_session),
        auth_client: AuthClient = Depends(get_auth_client),
        cards_client: CardsClient = Depends(get_cards_client),
) -> PackService:
    repository = PackRepository(db)
    return PackService(repository, auth_client, cards_client)
