from time import time
from typing import List

from game.repositories.repository import GameRepository


class GameRoundService:
    def __init__(self, repo: GameRepository):
        self.repo = repo

    async def get_card(self, game_id: str, current_player_id: int):
        cards = await self.repo.get_player_cards(game_id)

        current_card = cards['current']
        if current_card is None:
            return None

        previous_card = cards['previous']

        await self.repo.push_played_card(game_id, current_card)
        await self.repo.increment_cursor(game_id)

        data = {
            'current_player_id': current_player_id,
            'current_card': current_card,
            'previous_card': previous_card
        }
        return data

    async def get_final_card(self, game_id: str, current_player_id: int):
        cards = await self.repo.get_player_cards(game_id)
        card = cards['previous']

        return card

    async def card_guessed(
            self,
            game_id: str,
            card_id: int,
            guessed: bool,
            played_cards: List[dict]
    ):
        played_card_ids = set(card['id'] for card in played_cards)
        if card_id not in played_card_ids:
            return None

        await self.repo.guess_card(game_id, card_id, guessed)

        result = {'type': 'guess', 'card': card_id, 'guessed': guessed}
        return result

    async def set_timer(self, game_id: str, round_time: int) -> int:
        end_time = int(time()) + round_time
        await self.repo.set_timer(game_id, end_time)

        return end_time

    async def next_round(self, game_id: str):
        next_player_id = await self.repo.next_turn(game_id)
        return next_player_id
