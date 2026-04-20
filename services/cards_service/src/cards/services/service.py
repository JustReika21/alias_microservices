from random import sample, shuffle
from typing import List, Sequence

from cards.database.models import Card
from cards.exc.exceptions import (CardCreationError, CardDeletionError,
                                  CardDoesNotExistError, CardError)
from cards.grpc.clients.packs import PacksClient
from cards.repositories.repository import CardRepository
from cards.schemas.schemas import (CardRead, CardsCreate, CardsDelete,
                                   RandomCardRead, RandomCardsRequest)
from sqlalchemy.exc import IntegrityError


class CardService:
    def __init__(self, card_repository: CardRepository, packs_client: PacksClient):
        self.card_repository = card_repository
        self.db = self.card_repository.db
        self.packs_client = packs_client

    async def create_cards(
            self,
            cards: CardsCreate,
    ) -> List[Card]:
        if not await self.packs_client.is_pack_exist(cards.pack_id):
            raise CardCreationError('Collection does not exist')

        cards_count = len(cards.words)

        start_pos = await self.card_repository.get_max_card_position(cards.pack_id)
        new_cards = [
            Card(
                word=word,
                pack_id=cards.pack_id,
                position=start_pos + i + 1,
            )
            for i, word in enumerate(cards.words)
        ]

        try:
            await self.card_repository.create(new_cards)
            await self.db.commit()

            result = await self.packs_client.update_total_cards_in_pack(cards.pack_id, cards_count)
            if not result:
                raise CardCreationError('Failed to create cards')

            return new_cards
        except IntegrityError:
            await self.db.rollback()
            raise CardCreationError('Failed to create cards')

    async def get_cards(self, pack_id: int) -> List[CardRead]:
        cards = await self.card_repository.get(pack_id)

        validated_cards = [
            CardRead.model_validate(card)
            for card in cards
        ]
        return validated_cards

    async def get_random_cards(
            self,
            payload: RandomCardsRequest,
    ) -> Sequence[RandomCardRead]:
        max_pos = await self.card_repository.get_max_card_position(payload.pack_id)

        if not max_pos:
            raise CardError('No cards in pack')

        attempt = 0
        cards = None
        while not cards and attempt < 3:
            random_ids = sample(range(1, max_pos + 1), min(max_pos, payload.limit))

            cards = await self.card_repository.get_random_cards(
                payload, random_ids
            )

            attempt += 1

        if not cards:
            raise CardError('No cards in pack')

        validated_cards = [RandomCardRead.model_validate(card) for card in cards]
        shuffle(validated_cards)
        return validated_cards

    async def delete_cards(self, payload: CardsDelete):
        try:
            card_ids = await self.card_repository.delete_cards(payload)
            total_deleted = len(card_ids)

            if card_ids:
                success = await self.packs_client.update_total_cards_in_pack(payload.pack_id, -total_deleted)
                if not success:
                    raise CardDeletionError('Failed to delete cards')

            await self.db.commit()

        except IntegrityError:
            await self.db.rollback()
            raise CardDeletionError('Card deletion failed')

    async def delete_all_cards_in_pack(self, pack_id: int) -> bool:
        try:
            await self.card_repository.delete_all_cards_in_pack(pack_id)
            await self.db.commit()
            return True
        except IntegrityError:
            await self.db.rollback()
            raise CardDeletionError('Card deletion failed')

    async def is_pack_creator(self, pack_id: int, access_token: str) -> None:
        is_creator = await self.packs_client.is_pack_creator(pack_id, access_token)

        if not is_creator:
            raise CardError('You do not have permission')
