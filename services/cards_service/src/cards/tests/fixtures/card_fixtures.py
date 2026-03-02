from typing import List, cast

import pytest_asyncio
from cards.database.models import Card
from cards.grpc.clients.packs import PacksClient
from cards.repositories.repository import CardRepository
from cards.services.service import CardService
from cards.tests.fixtures.fakes import FakePacksClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture
async def cards_repository(test_get_session: AsyncSession) -> CardRepository:
    return CardRepository(test_get_session)


@pytest_asyncio.fixture
async def cards_service(cards_repository, get_fake_packs_client: FakePacksClient) -> CardService:
    packs_client = cast(PacksClient, get_fake_packs_client)
    return CardService(cards_repository, packs_client)


@pytest_asyncio.fixture
async def create_cards(
        test_get_session: AsyncSession, get_fake_packs_client: FakePacksClient
):
    async def _create(pack_id: int = 1, count: int = 1) -> List[Card]:
        stmt = select(func.max(Card.position)).where(Card.pack_id == pack_id)
        max_position = await test_get_session.scalar(stmt) or 0

        cards = [
            Card(
                word=f'test_{i}',
                pack_id=pack_id,
                position=max_position + i + 1,
            )
            for i in range(count)
        ]

        test_get_session.add_all(cards)
        await test_get_session.commit()

        await get_fake_packs_client.update_total_cards_in_pack(pack_id=pack_id, count=count)

        return cards
    return _create
