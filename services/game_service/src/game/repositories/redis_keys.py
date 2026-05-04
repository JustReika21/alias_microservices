class RedisConfig:
    EXPIRE_TIME = 7200

    def _game_key(self, game_id: str) -> str:
        return f'alias:game:{game_id}'

    def _player_key(self, game_id: str, player_id: int) -> str:
        return f'alias:game:{game_id}:player:{player_id}'

    def _team_key(self, game_id: str, team_id: int) -> str:
        return f'alias:game:{game_id}:team:{team_id}'

    def _teams_key(self, game_id: str):
        return f'alias:game:{game_id}:teams'

    def _team_players_key(self, game_id: str, team_id: int) -> str:
        return f'alias:game:{game_id}:team:{team_id}:players'

    def _turn_offset_key(self, game_id: str) -> str:
        return f'alias:game:{game_id}:turn_offset'

    def _current_player_key(self, game_id: str) -> str:
        return f'alias:game:{game_id}:current_player'

    def _cards_key(self, game_id: str) -> str:
        return f'alias:game:{game_id}:cards'

    def _card_cursor_key(self, game_id: str) -> str:
        return f'alias:game:{game_id}:card_cursor'

    def _played_cards_key(self, game_id: str) -> str:
        return f'alias:game:{game_id}:played_cards'

    def _guessed_cards_key(self, game_id: str) -> str:
        return f'alias:game:{game_id}:guessed_cards'

    def _timer_key(self, game_id: str) -> str:
        return f'alias:game:{game_id}:timer'
