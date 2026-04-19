from typing import Optional

import grpc
import grpc.aio
from cards_grpc.v1.cards_grpc_pb2 import DeleteAllCardsInPackReq
from cards_grpc.v1.cards_grpc_pb2_grpc import CardsStub

class CardsClient:
    def __init__(self, target: str):
        self.target = target
        self.channel: Optional[grpc.aio.Channel] = None
        self.stub: Optional[CardsStub] = None

    async def connect(self):
        self.channel = grpc.aio.insecure_channel(self.target)
        self.stub = CardsStub(self.channel)

    async def close(self):
        if self.channel:
            await self.channel.close()

    async def delete_all_cards_in_pack(self, pack_id: int):
        response = await self.stub.DeleteAllCardsInPack(DeleteAllCardsInPackReq(pack_id=pack_id))
        return response.success
