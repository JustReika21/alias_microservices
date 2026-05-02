from game.repositories.repository import GameRepository


class GameSnapshotService:
    def __init__(self, repo: GameRepository):
        self.repo = repo

    async def load_snapshot(
            self,
            game_id: str,
            user_id: int,
            game_status: str,
            current_player_id: int
    ):
        is_current = user_id == current_player_id

        snapshot = {
            'type': 'snapshot',
            'current_player': {
                'player_id': current_player_id,
                'is_current': is_current
            },
            'status': game_status,
            'cards': None,
            'timer': None
        }

        if game_status == 'started':
            cards = await self.repo.get_played_cards(game_id)
            snapshot['cards'] = cards if is_current else cards[:-1]
            end_time = await self.repo.get_timer(game_id)
            snapshot['end_time'] = end_time

        elif game_status == 'calculating':
            cards = await self.repo.get_played_cards(game_id)
            snapshot['cards'] = cards

        return snapshot