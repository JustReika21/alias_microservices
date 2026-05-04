from typing import List


class GameSnapshotService:
    async def load_snapshot(
            self,
            game_id: str,
            user_id: int,
            game_status: str,
            current_player_id: int,
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
            'status': game_status,
            'cards': None,
            'timer': None
        }

        if game_status == 'started':
            snapshot['cards'] = played_cards if is_current else played_cards[:-1]
            snapshot['end_time'] = end_time

        elif game_status == 'calculating':
            snapshot['cards'] = played_cards

        return snapshot