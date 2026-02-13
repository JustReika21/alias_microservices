from game.database.db import async_session
from sqlalchemy.ext.asyncio import AsyncSession

from game.grpc.clients.packs import PacksClient
from fastapi import Request


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

def get_packs_client(request: Request) -> PacksClient:
    return request.app.state.packs_client
