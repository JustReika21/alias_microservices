from packs.exc.exceptions import PackCreationError, PackUpdateError, \
    PackDoesNotExist
from packs.repositories.repository import PackRepository
from packs.schemas.schemas import PackCreate, PackRead
from sqlalchemy.exc import IntegrityError


class PackService:
    def __init__(self, pack_repository: PackRepository):
        self.pack_repository = pack_repository
        self.db = self.pack_repository.db

    async def create_pack(self, pack: PackCreate) -> PackRead:
        try:
            created_pack = await self.pack_repository.create(pack)
            await self.db.commit()
            await self.db.refresh(created_pack)

            return PackRead.model_validate(created_pack)
        except IntegrityError:
            await self.db.rollback()
            raise PackCreationError('Pack creation error')

    async def is_pack_exist(self, pack_id: int) -> bool:
        return await self.pack_repository.is_pack_exist(pack_id)

    async def get_total_cards_in_pack(self, pack_id: int):
        total_cards = await self.pack_repository.get_total_cards(pack_id)

        if total_cards is None:
            raise PackDoesNotExist('Pack not found')

        return total_cards

    async def update_total_cards_in_pack(self, pack_id: int, count: int) -> bool:
        try:
            pack_id = await self.pack_repository.update_total_cards(pack_id, count)

            if pack_id is None:
                await self.db.rollback()
                raise PackDoesNotExist('Pack not found')

            await self.db.commit()
            return True
        except IntegrityError:
            await self.db.rollback()
            raise PackUpdateError('Update failed')
