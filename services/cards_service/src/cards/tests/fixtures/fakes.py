import pytest_asyncio
from cards.constants.packs_constants import MAX_CARDS_IN_PACK
from fastapi import Request

PACK_ID = 1


class FakePacksClient:
    def __init__(self):
        self.id = PACK_ID
        self.name = 'test'
        self.description = 'test'
        self.total = 0

    async def is_pack_exist(self, pack_id: int) -> bool:
        return self.id == pack_id

    async def get_total_cards_in_pack(self, pack_id: int) -> int:
        if self.id == pack_id:
            return self.total
        else:
            return 0

    async def update_total_cards_in_pack(self, pack_id: int, count: int) -> bool:
        if self.id == pack_id and count + self.total <= MAX_CARDS_IN_PACK:
            self.total += count
            return True


@pytest_asyncio.fixture
def get_fake_packs_client(request: Request) -> FakePacksClient:
    return FakePacksClient()
