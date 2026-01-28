from packs_grpc.v1 import packs_grpc_pb2, packs_grpc_pb2_grpc

from packs.api.repository import is_pack_exist
from packs.database.db import async_session


class Packs(packs_grpc_pb2_grpc.PacksServicer):
    async def IsPackExist(self, request, context):
        pack_id = request.id
        async with async_session() as db:
            exists = await is_pack_exist(pack_id, db)
        return packs_grpc_pb2.IsPackExistResp(exist=exists)
