import pytest
from httpx import AsyncClient

from packs.exc.exceptions import PackUpdateError, PackDoesNotExist
from packs.services.service import PackService

from sqlalchemy.ext.asyncio import AsyncSession

class TestPackService:
    @pytest.mark.asyncio
    async def test_is_pack_exist_returns_true_when_exists(
            self, client: AsyncClient, pack_service: PackService, create_pack
    ):
        pack = await create_pack('Test', 'Test')

        exists = await pack_service.is_pack_exist(pack.id)

        assert exists is True

    @pytest.mark.asyncio
    async def test_is_pack_exist_returns_false_when_not_exists(
            self, client: AsyncClient, pack_service: PackService, create_pack
    ):
        exists = await pack_service.is_pack_exist(9999)

        assert exists is False

    @pytest.mark.asyncio
    @pytest.mark.parametrize('total', [
        0, 1, 100, 5000
    ])
    async def test_get_total_cards_in_pack_returns_total_cards(
            self, client: AsyncClient, pack_service: PackService, create_pack,
            total
    ):
        pack = await create_pack('Test', 'Test', total)

        result = await pack_service.get_total_cards_in_pack(pack.id)

        assert result == total

    @pytest.mark.asyncio
    @pytest.mark.parametrize('count', [
        0, 1, 100, 5000
    ])
    @pytest.mark.asyncio
    async def test_update_total_cards_in_pack_increases_total(
            self, client: AsyncClient, pack_service: PackService,
            test_get_session: AsyncSession, create_pack,  count
    ):
        pack = await create_pack('Test', 'Test', 0)

        await pack_service.update_total_cards_in_pack(pack.id, count)

        await test_get_session.refresh(pack)
        total = await pack_service.get_total_cards_in_pack(pack.id)

        assert total == count

    @pytest.mark.asyncio
    @pytest.mark.parametrize('count', [
        -1, -100, -5000
    ])
    async def test_update_total_cards_in_pack_decreases_total(
            self, client: AsyncClient, pack_service: PackService,
            test_get_session: AsyncSession, create_pack, count
    ):
        pack = await create_pack('Test', 'Test', 5000)

        await pack_service.update_total_cards_in_pack(pack.id, count)

        await test_get_session.refresh(pack)
        total = await pack_service.get_total_cards_in_pack(pack.id)

        assert total == 5000 + count

    @pytest.mark.asyncio
    @pytest.mark.parametrize('count', [
        5001, -1
    ])
    async def test_get_total_cards_in_pack_raises_when_total_out_of_bounds(
            self, client: AsyncClient, pack_service: PackService,
            test_get_session: AsyncSession, create_pack, count
    ):
        pack = await create_pack('Test', 'Test', 0)

        with pytest.raises(PackUpdateError):
            await pack_service.update_total_cards_in_pack(pack.id, count)

        await test_get_session.refresh(pack)
        total = await pack_service.get_total_cards_in_pack(pack.id)

        assert total == 0

    @pytest.mark.asyncio
    async def test_update_total_cards_raises_when_pack_does_not_exist(
            self, client: AsyncClient, pack_service: PackService
    ):
        with pytest.raises(PackDoesNotExist):
            await pack_service.update_total_cards_in_pack(99999, 1)

    @pytest.mark.asyncio
    async def test_get_total_cards_raises_when_pack_does_not_exist(
            self, client: AsyncClient, pack_service: PackService
    ):
        with pytest.raises(PackDoesNotExist):
            await pack_service.get_total_cards_in_pack(99999)
