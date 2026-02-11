from packs.api.repository import get_total_cards_in_pack, is_pack_exist, \
    update_total_cards_in_pack
from packs.database.db import async_session
from packs_grpc.v1 import packs_grpc_pb2, packs_grpc_pb2_grpc


class Packs(packs_grpc_pb2_grpc.PacksServicer):
    async def IsPackExist(self, request, context):
        pack_id = request.id
        async with async_session() as db:
            exists = await is_pack_exist(pack_id, db)
        return packs_grpc_pb2.IsPackExistResp(exist=exists)

    async def GetTotalCardsInPack(self, request, context):
        pack_id = request.id
        async with async_session() as db:
            total = await get_total_cards_in_pack(pack_id, db)
        return packs_grpc_pb2.GetTotalCardsInPackResp(total=total)

    async def UpdateTotalCardsInPack(self, request, context):
        pack_id = request.pack_id
        count = request.count
        async with async_session() as db:
            success = await update_total_cards_in_pack(pack_id, count, db)
        return packs_grpc_pb2.UpdateTotalCardsInPackResp(success=success)
