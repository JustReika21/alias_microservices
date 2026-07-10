from typing import List

from packs.exc.exceptions import (PackCreationError, PackDeletionError,
                                  PackDoesNotExist, PackUpdateError,
                                  PermissionDenied)
from packs.grpc.clients.auth import AuthClient
from packs.grpc.clients.cards import CardsClient
from packs.repositories.repository import PackRepository
from packs.schemas.schemas import PackCreate, PackRead, PackUpdate, \
    PackPreview, PaginatedPacksPreview, PaginatedInfiniteScroll
from sqlalchemy.exc import IntegrityError

PACKS_QUERY_LIMIT = 5
PACKS_QUERY_LIMIT_FOR_CREATE_GAME = 100


class PackService:
    def __init__(
            self,
            pack_repository: PackRepository,
            auth_client: AuthClient,
            cards_client: CardsClient
    ):
        self.pack_repository = pack_repository
        self.db = self.pack_repository.db

        self.auth_client = auth_client
        self.cards_client = cards_client

    async def create_pack(self, pack: PackCreate, user_id: int) -> PackRead:
        total = await self.pack_repository.get_total_user_packs(user_id)

        if total >= 10:
            raise PackCreationError('Too many packs. Max 10')

        try:
            created_pack = await self.pack_repository.create(pack, user_id)
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

    async def get_pack(self, pack_id: int) -> PackRead:
        pack = await self.pack_repository.get_pack(pack_id)

        if pack is None:
            raise PackDoesNotExist('Pack not found')

        return PackRead.model_validate(pack)

    async def get_packs(self, pack_name: str, page: int) -> PaginatedInfiniteScroll:
        packs = await self.pack_repository.get_packs_by_name(
            pack_name, page, PACKS_QUERY_LIMIT_FOR_CREATE_GAME
        )

        response = PaginatedInfiniteScroll(
            items=[PackPreview.model_validate(pack) for pack in packs],
            page=page,
        )
        return response

    async def get_my_packs(self, access_token: str, page: int) -> PaginatedPacksPreview:
        user = await self.auth_client.get_user(access_token)

        packs = await self.pack_repository.get_packs_by_creator_id(
            user.user_id, page, PACKS_QUERY_LIMIT
        )

        total = await self.pack_repository.get_total_user_packs(user.user_id)

        response = PaginatedPacksPreview(
            items=[PackPreview.model_validate(pack) for pack in packs],
            total=total,
            page=page,
            limit=PACKS_QUERY_LIMIT,
            pages=(total + PACKS_QUERY_LIMIT - 1) // PACKS_QUERY_LIMIT,
        )
        return response


    async def delete_pack(self, pack_id: int):
        try:
            pack_id = await self.pack_repository.delete_pack(pack_id)

            if pack_id is None:
                await self.db.rollback()
                raise PackDoesNotExist('Pack not found')

            await self.db.commit()

        except IntegrityError:
            await self.db.rollback()
            raise PackDeletionError('Pack deletion error')

    async def is_creator(self, pack_id: int, access_token: str) -> bool:
        user = await self.auth_client.get_user(access_token)
        creator_id = await self.pack_repository.get_pack_creator_id(pack_id)

        if user.user_id != creator_id:
            raise PermissionDenied('You do not have permission to delete this pack')

        return True

    async def update_pack(self, pack_id: int, payload: PackUpdate) -> PackRead:
        data = payload.model_dump(exclude_unset=True)
        try:
            pack = await self.pack_repository.update(pack_id, data)
            await self.db.commit()
            await self.db.refresh(pack)
            return PackRead.model_validate(pack)
        except IntegrityError:
            await self.db.rollback()
            raise PackUpdateError('Update failed')
