from typing import Sequence

from packs.database.models import Pack
from packs.schemas.schemas import PackCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import delete, exists, select, update, func


class PackRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, pack: PackCreate, user_id: int) -> Pack:
        pack = Pack(name=pack.name, description=pack.description, creator=user_id)
        self.db.add(pack)
        return pack

    async def is_pack_exist(self, pack_id: int) -> bool:
        stmt = select(exists().where(Pack.id == pack_id))
        pack_exists = await self.db.scalar(stmt)
        return pack_exists

    async def get_total_cards(self, pack_id: int) -> int | None:
        stmt = (
            select(Pack.total)
            .where(Pack.id == pack_id)
        )
        total_cards = await self.db.scalar(stmt)
        return total_cards

    async def update_total_cards(self, pack_id: int, count: int) -> int | None:
        stmt = (
            update(Pack)
            .where(Pack.id == pack_id,)
            .values(total=Pack.total + count)
            .returning(Pack.id)
        )
        result = await self.db.scalar(stmt)
        return result

    async def get_packs(self, page: int, limit: int) -> Sequence[Pack]:
        stmt = (
            select(Pack)
            .offset((page - 1) * limit)
            .limit(limit)
            .order_by(Pack.id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_total_packs(self) -> int:
        stmt = (select(func.count(Pack.id)))
        result = await self.db.execute(stmt)
        return result.scalar()

    async def get_pack(self, pack_id: int) -> Pack | None:
        stmt = (
            select(Pack)
            .where(Pack.id == pack_id)
        )
        result = await self.db.scalar(stmt)
        return result

    async def get_packs_by_name(
            self,
            pack_name: str,
            page: int,
            limit: int
    ) -> Sequence[Pack]:
        stmt = (
            select(Pack)
            .where(Pack.name.icontains(pack_name))
            .offset((page - 1) * limit)
            .limit(limit)
            .order_by(Pack.id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_packs_by_creator_id(
            self,
            creator_id: int,
            page: int,
            limit: int
    ) -> Sequence[Pack]:
        stmt = (
            select(Pack)
            .where(Pack.creator == creator_id)
            .offset((page - 1) * limit)
            .limit(limit)
            .order_by(Pack.id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_total_user_packs(self, user_id: int) -> int:
        stmt = (
            select(func.count(Pack.id))
            .where(Pack.creator == user_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar()

    async def delete_pack(self, pack_id: int) -> int | None:
        stmt = (
            delete(Pack)
            .where(Pack.id == pack_id)
            .returning(Pack.id)
        )
        result = await self.db.scalar(stmt)
        return result

    async def get_pack_creator_id(self, pack_id: int) -> int | None:
        stmt = (
            select(Pack.creator)
            .where(Pack.id == pack_id)
        )
        result = await self.db.scalar(stmt)
        return result

    async def update(self, pack_id: int, data: dict) -> Pack:
        stmt = (
            update(Pack)
            .where(Pack.id == pack_id)
            .values(**data)
            .returning(Pack)
        )
        pack = await self.db.scalar(stmt)
        return pack
