from typing import List


class GameSnapshotService:
    async def load_snapshot(
            self,
            user_id: int,
            game_status: str,
            players: List[dict],
            my_id: int,
            current_player_id: int,
            host: int,
            teams: List[dict],
            played_cards: List[dict] | None,
            end_time: int | None,
    ) -> dict:
        is_current = user_id == current_player_id

        snapshot = {
            'type': 'snapshot',
            'current_player': {
                'player_id': current_player_id,
                'is_current': is_current
            },
            'players': players,
            'my_id': my_id,
            'status': game_status,
            'host': host,
            'teams': teams,
            'cards': None,
            'timer': None
        }

        if game_status == 'started':
            snapshot['cards'] = played_cards if is_current else played_cards[:-1]
            snapshot['end_time'] = end_time

        elif game_status == 'calculating':
            snapshot['cards'] = played_cards

        return snapshot