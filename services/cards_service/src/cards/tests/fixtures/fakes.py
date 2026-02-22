import pytest_asyncio
from fastapi import Request


class FakePacksClient:
    def __init__(self):
        self.id = 1
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
        if self.id == pack_id:
            self.total += count
            return True
        else:
            return False

@pytest_asyncio.fixture
def get_fake_packs_client(request: Request) -> FakePacksClient:
    return FakePacksClient()
