from packs.database.db import async_session
from packs.repositories.repository import PackRepository
from packs.services.service import PackService
from packs_grpc.v1 import packs_grpc_pb2, packs_grpc_pb2_grpc


class Packs(packs_grpc_pb2_grpc.PacksServicer):
    async def IsPackExist(self, request, context):
        pack_id = request.id
        async with async_session() as db:
            service = PackService(PackRepository(db))
            exists = await service.is_pack_exist(pack_id)
        return packs_grpc_pb2.IsPackExistResp(exist=exists)

    async def GetTotalCardsInPack(self, request, context):
        pack_id = request.id
        async with async_session() as db:
            service = PackService(PackRepository(db))
            total = await service.get_total_cards_in_pack(pack_id)
        return packs_grpc_pb2.GetTotalCardsInPackResp(total=total)

    async def UpdateTotalCardsInPack(self, request, context):
        pack_id = request.pack_id
        count = request.count
        async with async_session() as db:
            service = PackService(PackRepository(db))
            success = await service.update_total_cards_in_pack(pack_id, count)
        return packs_grpc_pb2.UpdateTotalCardsInPackResp(success=success)
