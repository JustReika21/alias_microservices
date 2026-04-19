from typing import Optional

import grpc
import grpc.aio
from packs_grpc.v1.packs_grpc_pb2 import (GetTotalCardsInPackReq,
                                          IsPackExistReq,
                                          UpdateTotalCardsInPackReq,
                                          IsPackCreatorReq)
from packs_grpc.v1.packs_grpc_pb2_grpc import PacksStub


class PacksClient:
    def __init__(self, target: str):
        self.target = target
        self.channel: Optional[grpc.aio.Channel] = None
        self.stub: Optional[PacksStub] = None

    async def connect(self):
        self.channel = grpc.aio.insecure_channel(self.target)
        self.stub = PacksStub(self.channel)

    async def close(self):
        if self.channel:
            await self.channel.close()

    async def is_pack_exist(self, pack_id: int) -> bool:
        response = await self.stub.IsPackExist(IsPackExistReq(id=pack_id))
        return response.exist

    async def get_total_cards_in_pack(self, pack_id: int) -> int:
        response = await self.stub.GetTotalCardsInPack(GetTotalCardsInPackReq(id=pack_id))
        return response.total

    async def update_total_cards_in_pack(self, pack_id: int, count: int) -> bool:
        response = await self.stub.UpdateTotalCardsInPack(
            UpdateTotalCardsInPackReq(pack_id=pack_id, count=count)
        )
        return response.success

    async def is_pack_creator(self, pack_id: int, access_token: str) -> bool:
        response = await self.stub.IsPackCreator(
            IsPackCreatorReq(pack_id=pack_id, access_token=access_token)
        )
        return response.is_creator
