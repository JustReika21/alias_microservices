from sqlalchemy.exc import IntegrityError

import pytest

from packs.repositories.repository import PackRepository


class TestPacksRepository:
    @pytest.mark.asyncio
    async def test_is_pack_exists_returns_true_if_exists(
            self, pack_repository: PackRepository, create_packs
    ):
        pack = await create_packs(1)

        exists = await pack_repository.is_pack_exist(pack[0].id)

        assert exists is True

    @pytest.mark.asyncio
    async def test_is_pack_exists_returns_false_if_not_exists(
            self, pack_repository: PackRepository, create_packs
    ):
        exists = await pack_repository.is_pack_exist(9999)

        assert exists is False

    @pytest.mark.asyncio
    @pytest.mark.parametrize('count', [
        0, 1, 100, 5000
    ])
    async def test_get_total_cards_in_pack_returns_total_cards(
            self, pack_repository: PackRepository, create_pack, count
    ):
        pack = await create_pack('test', 'test', count)

        total = await pack_repository.get_total_cards(pack.id)

        assert total == count

    @pytest.mark.asyncio
    async def test_get_total_cards_in_not_exists_pack(
            self, pack_repository: PackRepository
    ):
        total = await pack_repository.get_total_cards(9999)

        assert total is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize('count', [
        1, 100, 5000
    ])
    async def test_increase_total_cards_in_pack(
            self, pack_repository: PackRepository, create_pack, count
    ):
        pack = await create_pack('test', 'test', 0)

        updated_pack_id = await pack_repository.update_total_cards(pack.id, count)

        assert updated_pack_id == pack.id

        total = await pack_repository.get_total_cards(updated_pack_id)

        assert total == count

    @pytest.mark.asyncio
    @pytest.mark.parametrize('count', [
        -1, -100, -5000
    ])
    async def test_decrease_total_cards_in_pack(
            self, pack_repository: PackRepository, create_pack, count
    ):
        pack = await create_pack('test', 'test', 5000)

        updated_pack_id = await pack_repository.update_total_cards(pack.id, count)

        assert updated_pack_id == pack.id

        total = await pack_repository.get_total_cards(updated_pack_id)

        assert total == 5000 + count

    @pytest.mark.asyncio
    @pytest.mark.parametrize('count', [
        -1, 5001
    ])
    async def test_update_total_cards_raises_integrity_error_when_total_out_of_bounds(
            self, pack_repository: PackRepository, create_pack, count
    ):
        pack = await create_pack('test', 'test', 0)

        with pytest.raises(IntegrityError):
            await pack_repository.update_total_cards(pack.id, count)

    @pytest.mark.asyncio
    async def test_update_total_cards_in_not_exists_pack(
            self, pack_repository: PackRepository
    ):
        pack_id = await pack_repository.update_total_cards(9999, 1)

        assert pack_id is None