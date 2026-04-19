from packs.database.db import async_session
from packs.grpc.clients.auth import AuthClient
from packs.grpc.clients.cards import CardsClient
from packs.repositories.repository import PackRepository
from packs.services.service import PackService
from packs_grpc.v1 import packs_grpc_pb2, packs_grpc_pb2_grpc


class Packs(packs_grpc_pb2_grpc.PacksServicer):
    def __init__(self, auth_client: AuthClient, cards_client: CardsClient):
        self.auth_client = auth_client
        self.cards_client = cards_client

    async def IsPackExist(self, request, context):
        pack_id = request.id
        async with async_session() as db:
            service = PackService(PackRepository(db), self.auth_client, self.cards_client)
            exists = await service.is_pack_exist(pack_id)
        return packs_grpc_pb2.IsPackExistResp(exist=exists)

    async def GetTotalCardsInPack(self, request, context):
        pack_id = request.id
        async with async_session() as db:
            service = PackService(PackRepository(db), self.auth_client, self.cards_client)
            total = await service.get_total_cards_in_pack(pack_id)
        return packs_grpc_pb2.GetTotalCardsInPackResp(total=total)

    async def UpdateTotalCardsInPack(self, request, context):
        pack_id = request.pack_id
        count = request.count
        async with async_session() as db:
            service = PackService(PackRepository(db), self.auth_client, self.cards_client)
            success = await service.update_total_cards_in_pack(pack_id, count)
        return packs_grpc_pb2.UpdateTotalCardsInPackResp(success=success)

    async def IsPackCreator(self, request, context):
        pack_id = request.pack_id
        access_token = request.access_token
        async with async_session() as db:
            service = PackService(PackRepository(db), self.auth_client, self.cards_client)
            is_creator = await service.is_creator(pack_id, access_token)
        return packs_grpc_pb2.IsPackCreatorResp(is_creator=is_creator)
