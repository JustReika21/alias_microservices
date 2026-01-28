import grpc

from packs_grpc.v1.packs_grpc_pb2 import IsPackExistReq
from packs_grpc.v1.packs_grpc_pb2_grpc import PacksStub


class PacksClient:
    def __init__(self, target: str):
        self.target = target

    async def is_pack_exist(self, pack_id: int) -> bool:
        async with grpc.aio.insecure_channel(self.target) as channel:
            stub = PacksStub(channel)
            response = await stub.IsPackExist(
                IsPackExistReq(id=pack_id)
            )
            return response.exist

