from cards.database.db import async_session
from cards.grpc.clients.packs import PacksClient
from cards.repositories.repository import CardRepository
from cards.schemas.schemas import RandomCardsRequest
from cards.services.service import CardService
from cards_grpc.v1 import cards_grpc_pb2, cards_grpc_pb2_grpc


class Cards(cards_grpc_pb2_grpc.CardsServicer):
    def __init__(self, packs_client: PacksClient):
        self.packs_client = packs_client

    async def GetRandomCards(self, request, context):
        pack_id = request.pack_id
        LIMIT = 100
        payload = RandomCardsRequest(pack_id=pack_id, limit=LIMIT)
        async with async_session() as db:
            service = CardService(CardRepository(db), self.packs_client)
            cards = await service.get_random_cards(payload)
        return cards_grpc_pb2.GetRandomCardsResp(
            cards=[
                cards_grpc_pb2.Card(id=card.id, word=card.word)
                for card in cards
            ]
        )

    async def DeleteAllCardsInPack(self, request, context):
        pack_id = request.pack_id
        async with async_session() as db:
            service = CardService(CardRepository(db), self.packs_client)
            success = await service.delete_all_cards_in_pack(pack_id)
        return cards_grpc_pb2.DeleteAllCardsInPackResp(success=success)
