from typing import List

from game.grpc.clients.cards import CardsClient
from game.repositories.card import GameCardRepository


class GameCardService:
    def __init__(
            self,
            card_repo: GameCardRepository,

            cards_client: CardsClient,
    ):
        self.card_repo = card_repo

        self.cards_client = cards_client

    async def get_card(self, game_id: str, current_player_id: int) -> dict | None:
        cursor = await self.card_repo.get_card_cursor(game_id)
        cards = await self.card_repo.get_players_cards(game_id, cursor)

        current_card = cards['current']
        if current_card is None:
            return None

        previous_card = cards['previous']

        await self.card_repo.commit_card(game_id, current_card)

        data = {
            'current_player_id': current_player_id,
            'current_card': current_card,
            'previous_card': previous_card
        }
        return data

    async def get_final_card(self, game_id: str) -> dict:
        cursor = await self.card_repo.get_card_cursor(game_id)
        cards = await self.card_repo.get_players_cards(game_id, cursor)
        card = cards['previous']

        return card

    async def set_guessed_cards(self, game_id: str) -> None:
        await self.card_repo.set_guessed_cards(game_id)

    async def card_guessed(
            self,
            game_id: str,
            card_id: int,
            guessed: bool,
            played_cards: List[dict]
    ) -> dict | None:
        played_card_ids = set(card['id'] for card in played_cards)
        if card_id not in played_card_ids:
            return None

        await self.card_repo.guess_card(game_id, card_id, guessed)

        result = {'type': 'guess', 'card': card_id, 'guessed': guessed}
        return result

    async def get_cards(self, pack_id: int) -> List[dict]:
        cards = await self.cards_client.get_random_cards(pack_id, 100)
        return cards

    async def set_up_game_cards(self, game_id: str, pack_id: int) -> None:
        cards = await self.get_cards(pack_id)
        await self.card_repo.set_game_cards(game_id, cards)
        await self.card_repo.set_card_cursor(game_id)

    async def get_played_cards(self, game_id: str) -> List[dict]:
        cards = await self.card_repo.get_played_cards(game_id)
        return cards

    async def get_guessed_cards(self, game_id: str) -> set[str]:
        guessed_cards = await self.card_repo.get_guessed_cards(game_id)
        return guessed_cards
